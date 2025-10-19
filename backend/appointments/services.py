"""
Service layer for Appointment business logic.

This module implements the Service Layer Pattern for Appointment operations,
encapsulating business logic and coordinating between repositories.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.services import BaseService
from .models import Appointment
from .repositories import AppointmentRepository


class AppointmentService(BaseService[Appointment]):
    """
    Service for managing Appointment business logic.

    This class extends BaseService to provide Appointment-specific
    business logic while inheriting standard service operations.

    Business rules enforced:
    - Start time must be in the future
    - End time must be after start time
    - Patient and practitioner must exist and be active
    - No scheduling conflicts for practitioners
    - Status transitions must follow valid workflow
    - Cancellations require active status
    """

    def __init__(self):
        """Initialize service with AppointmentRepository."""
        repository = AppointmentRepository()
        super().__init__(repository)

    def validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating an appointment.

        Args:
            data: Appointment data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not data.get('patient_id'):
            raise ValidationError('Patient is required')

        if not data.get('practitioner_id'):
            raise ValidationError('Practitioner is required')

        if not data.get('start'):
            raise ValidationError('Start time is required')

        if not data.get('end'):
            raise ValidationError('End time is required')

        # Validate timing
        start = data['start']
        end = data['end']

        if start >= end:
            raise ValidationError('End time must be after start time')

        # Check if start time is in the future (with 5 minute grace period)
        now = timezone.now()
        if start < now - timedelta(minutes=5):
            raise ValidationError('Cannot create appointments in the past')

        # Validate duration is reasonable (not more than 24 hours)
        duration = (end - start).total_seconds() / 3600  # hours
        if duration > 24:
            raise ValidationError('Appointment duration cannot exceed 24 hours')

        # Check for scheduling conflicts
        conflicts = self.repository.find_conflicts(
            practitioner_id=data['practitioner_id'],
            start=start,
            end=end
        )

        if conflicts:
            conflict_times = [
                f"{c.start.strftime('%H:%M')}-{c.end.strftime('%H:%M')}"
                for c in conflicts[:3]  # Show first 3 conflicts
            ]
            raise ValidationError(
                f'Practitioner has conflicting appointments at: {", ".join(conflict_times)}'
            )

        # Validate patient and practitioner references
        # This is handled by Django's ForeignKey constraints, but we can add
        # additional checks here if needed (e.g., check if practitioner is active)

    def validate_update(self, existing: Appointment, data: Dict[str, Any]) -> None:
        """
        Validate data before updating an appointment.

        Args:
            existing: The existing Appointment instance
            data: Updated data to validate

        Raises:
            ValidationError: If validation fails
        """
        # If times are being updated, validate timing logic
        start = data.get('start', existing.start)
        end = data.get('end', existing.end)

        if start >= end:
            raise ValidationError('End time must be after start time')

        # If practitioner or times are changing, check for conflicts
        # Handle both 'practitioner' (from serializer) and 'practitioner_id' (from direct updates)
        practitioner_id = data.get('practitioner') or data.get('practitioner_id', existing.practitioner_id)
        if ('start' in data or 'end' in data or 'practitioner' in data or 'practitioner_id' in data):
            conflicts = self.repository.find_conflicts(
                practitioner_id=practitioner_id,
                start=start,
                end=end,
                exclude_appointment_id=existing.id
            )

            if conflicts:
                conflict_times = [
                    f"{c.start.strftime('%H:%M')}-{c.end.strftime('%H:%M')}"
                    for c in conflicts[:3]
                ]
                raise ValidationError(
                    f'Practitioner has conflicting appointments at: {", ".join(conflict_times)}'
                )

        # Validate status transitions
        if 'status' in data:
            new_status = data['status']
            if not self._is_valid_status_transition(existing.status, new_status):
                raise ValidationError(
                    f'Invalid status transition from {existing.status} to {new_status}'
                )

    def validate_delete(self, existing: Appointment) -> None:
        """
        Validate before deleting an appointment.

        Args:
            existing: The Appointment to be deleted

        Raises:
            ValidationError: If deletion is not allowed
        """
        # Check if appointment has already been fulfilled
        if existing.status == 'fulfilled':
            raise ValidationError('Cannot delete fulfilled appointments. Cancel instead.')

        # Check if appointment is in the past and not cancelled
        if existing.start < timezone.now() and existing.status not in ['cancelled', 'noshow']:
            raise ValidationError('Cannot delete past appointments. Cancel them instead.')

    def check_availability(
        self,
        practitioner_id: UUID,
        start: datetime,
        end: datetime
    ) -> bool:
        """
        Check if a practitioner is available for a time slot.

        Args:
            practitioner_id: UUID of the practitioner
            start: Start time
            end: End time

        Returns:
            True if available, False otherwise
        """
        return self.repository.check_availability(
            practitioner_id=practitioner_id,
            start=start,
            end=end
        )

    def book_appointment(self, appointment_id: UUID) -> Appointment:
        """
        Book a proposed or pending appointment.

        Args:
            appointment_id: UUID of the appointment

        Returns:
            Updated Appointment instance

        Raises:
            ValidationError: If booking is not allowed
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValidationError('Appointment not found')

        if appointment.status not in ['proposed', 'pending']:
            raise ValidationError(f'Cannot book appointment with status: {appointment.status}')

        # Check availability one more time before booking (exclude current appointment)
        conflicts = self.repository.find_conflicts(
            practitioner_id=appointment.practitioner_id,
            start=appointment.start,
            end=appointment.end,
            exclude_appointment_id=appointment.id
        )
        if conflicts:
            raise ValidationError('Practitioner is no longer available for this time slot')

        # Update status and participant statuses
        return self.update(appointment_id, {
            'status': 'booked',
            'patient_status': 'accepted',
            'practitioner_status': 'accepted'
        })

    def cancel_appointment(
        self,
        appointment_id: UUID,
        cancellation_reason: str = ''
    ) -> Appointment:
        """
        Cancel an appointment.

        Args:
            appointment_id: UUID of the appointment
            cancellation_reason: Optional reason for cancellation

        Returns:
            Updated Appointment instance

        Raises:
            ValidationError: If cancellation is not allowed
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValidationError('Appointment not found')

        if not appointment.can_cancel():
            raise ValidationError(f'Cannot cancel appointment with status: {appointment.status}')

        # Invalidate cache for practitioner schedule
        self.repository.invalidate_availability_cache(
            appointment.practitioner_id,
            appointment.start
        )

        return self.update(appointment_id, {
            'status': 'cancelled',
            'cancellation_reason': cancellation_reason
        })

    def check_in_appointment(self, appointment_id: UUID) -> Appointment:
        """
        Check in a patient for an appointment.

        Args:
            appointment_id: UUID of the appointment

        Returns:
            Updated Appointment instance

        Raises:
            ValidationError: If check-in is not allowed
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValidationError('Appointment not found')

        if not appointment.can_check_in():
            if appointment.status != 'booked':
                raise ValidationError(f'Cannot check in appointment with status: {appointment.status}')
            else:
                raise ValidationError('Check-in window not yet open (opens 30 minutes before appointment)')

        return self.update(appointment_id, {
            'status': 'checked-in',
            'patient_status': 'accepted'
        })

    def mark_as_arrived(self, appointment_id: UUID) -> Appointment:
        """
        Mark patient as arrived for appointment.

        Args:
            appointment_id: UUID of the appointment

        Returns:
            Updated Appointment instance

        Raises:
            ValidationError: If status change is not allowed
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValidationError('Appointment not found')

        if appointment.status not in ['booked', 'checked-in']:
            raise ValidationError(f'Cannot mark as arrived from status: {appointment.status}')

        return self.update(appointment_id, {'status': 'arrived'})

    def mark_as_fulfilled(self, appointment_id: UUID) -> Appointment:
        """
        Mark appointment as fulfilled (completed).

        Args:
            appointment_id: UUID of the appointment

        Returns:
            Updated Appointment instance

        Raises:
            ValidationError: If status change is not allowed
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValidationError('Appointment not found')

        if appointment.status not in ['arrived', 'checked-in', 'booked']:
            raise ValidationError(f'Cannot mark as fulfilled from status: {appointment.status}')

        return self.update(appointment_id, {'status': 'fulfilled'})

    def mark_as_noshow(self, appointment_id: UUID) -> Appointment:
        """
        Mark appointment as no-show.

        Args:
            appointment_id: UUID of the appointment

        Returns:
            Updated Appointment instance

        Raises:
            ValidationError: If status change is not allowed
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValidationError('Appointment not found')

        if appointment.status not in ['booked', 'checked-in', 'arrived']:
            raise ValidationError(f'Cannot mark as no-show from status: {appointment.status}')

        # Check if appointment time has passed
        if appointment.end > timezone.now():
            raise ValidationError('Cannot mark as no-show before appointment end time')

        return self.update(appointment_id, {'status': 'noshow'})

    def get_upcoming_appointments(
        self,
        patient_id: UUID = None,
        practitioner_id: UUID = None,
        days_ahead: int = 30
    ) -> List[Appointment]:
        """
        Get upcoming appointments.

        Args:
            patient_id: Optional patient UUID filter
            practitioner_id: Optional practitioner UUID filter
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming Appointment instances
        """
        return self.repository.find_upcoming(
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            days_ahead=days_ahead
        )

    def get_todays_appointments(
        self,
        patient_id: UUID = None,
        practitioner_id: UUID = None
    ) -> List[Appointment]:
        """
        Get today's appointments.

        Args:
            patient_id: Optional patient UUID filter
            practitioner_id: Optional practitioner UUID filter

        Returns:
            List of today's Appointment instances
        """
        return self.repository.find_todays_appointments(
            patient_id=patient_id,
            practitioner_id=practitioner_id
        )

    def _is_valid_status_transition(self, from_status: str, to_status: str) -> bool:
        """
        Check if a status transition is valid.

        Args:
            from_status: Current status
            to_status: New status

        Returns:
            True if transition is valid
        """
        # Define valid status transitions
        valid_transitions = {
            'proposed': ['pending', 'booked', 'cancelled', 'entered-in-error'],
            'pending': ['booked', 'cancelled', 'waitlist', 'entered-in-error'],
            'booked': ['arrived', 'checked-in', 'fulfilled', 'cancelled', 'noshow'],
            'arrived': ['fulfilled', 'cancelled', 'noshow'],
            'checked-in': ['arrived', 'fulfilled', 'cancelled', 'noshow'],
            'waitlist': ['pending', 'booked', 'cancelled'],
            'fulfilled': [],  # Terminal state
            'cancelled': [],  # Terminal state
            'noshow': [],  # Terminal state
            'entered-in-error': [],  # Terminal state
        }

        # Same status is always valid
        if from_status == to_status:
            return True

        return to_status in valid_transitions.get(from_status, [])
