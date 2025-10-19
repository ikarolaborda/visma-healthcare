"""
Appointment models.

FHIR R4-compliant Appointment resource implementation for managing
scheduled healthcare appointments between patients and practitioners.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from patients.models import Patient
from practitioners.models import Practitioner


class Appointment(models.Model):
    """
    Appointment model conforming to FHIR Appointment resource structure.

    Represents a booking of a healthcare event among patient(s), practitioner(s),
    related person(s) and/or device(s) for a specific date/time.

    FHIR R4 Reference: https://hl7.org/fhir/R4/appointment.html
    """

    # Status choices based on FHIR AppointmentStatus value set
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('pending', 'Pending'),
        ('booked', 'Booked'),
        ('arrived', 'Arrived'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('noshow', 'No Show'),
        ('entered-in-error', 'Entered in Error'),
        ('checked-in', 'Checked In'),
        ('waitlist', 'Waitlist'),
    ]

    # Participant required choices
    PARTICIPANT_REQUIRED_CHOICES = [
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('information-only', 'Information Only'),
    ]

    # Participant status choices
    PARTICIPANT_STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('tentative', 'Tentative'),
        ('needs-action', 'Needs Action'),
    ]

    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')

    # Service information
    service_category = models.CharField(
        max_length=200,
        blank=True,
        help_text='Broad categorization of service'
    )
    service_type = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specific service to be performed'
    )
    specialty = models.CharField(
        max_length=200,
        blank=True,
        help_text='Required practitioner specialty'
    )
    appointment_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='Style of appointment or patient'
    )

    # Reason and priority
    reason_code = models.CharField(
        max_length=200,
        blank=True,
        help_text='Coded reason for appointment'
    )
    reason_description = models.TextField(
        blank=True,
        help_text='Detailed reason for appointment'
    )
    priority = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=5,
        help_text='Priority (0=highest, higher number=lower priority)'
    )

    # Description and instructions
    description = models.CharField(
        max_length=500,
        blank=True,
        help_text='Brief description shown in appointment list'
    )
    comment = models.TextField(
        blank=True,
        help_text='Additional comments about the appointment'
    )
    patient_instruction = models.TextField(
        blank=True,
        help_text='Detailed instructions for the patient'
    )

    # Timing
    start = models.DateTimeField(help_text='When appointment starts')
    end = models.DateTimeField(help_text='When appointment ends')
    minutes_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Duration in minutes (can be estimate)'
    )

    # Participants - ForeignKey relationships
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text='Patient involved in appointment'
    )
    patient_status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS_CHOICES,
        default='needs-action',
        help_text='Patient participation status'
    )

    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text='Practitioner involved in appointment'
    )
    practitioner_status = models.CharField(
        max_length=20,
        choices=PARTICIPANT_STATUS_CHOICES,
        default='needs-action',
        help_text='Practitioner participation status'
    )
    practitioner_required = models.CharField(
        max_length=20,
        choices=PARTICIPANT_REQUIRED_CHOICES,
        default='required',
        help_text='Whether practitioner is required'
    )

    # Metadata
    created = models.DateTimeField(auto_now_add=True, help_text='When appointment was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='Last update timestamp')
    cancellation_reason = models.TextField(
        blank=True,
        help_text='Reason for cancellation'
    )

    class Meta:
        ordering = ['-start']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['patient', 'start']),
            models.Index(fields=['practitioner', 'start']),
            models.Index(fields=['start', 'end']),
        ]
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'

    def __str__(self):
        """String representation of appointment."""
        return f"{self.patient.get_full_name()} with {self.practitioner.get_full_name()} on {self.start.strftime('%Y-%m-%d %H:%M')}"

    def get_duration_minutes(self):
        """
        Calculate duration in minutes.

        Returns:
            int: Duration in minutes, or minutes_duration if set
        """
        if self.minutes_duration:
            return self.minutes_duration

        if self.start and self.end:
            duration = self.end - self.start
            return int(duration.total_seconds() / 60)

        return 0

    def is_upcoming(self):
        """
        Check if appointment is upcoming.

        Returns:
            bool: True if appointment is in the future
        """
        from django.utils import timezone
        return self.start > timezone.now() and self.status not in ['cancelled', 'noshow', 'entered-in-error']

    def is_active(self):
        """
        Check if appointment is in an active state.

        Returns:
            bool: True if appointment is in active state
        """
        return self.status in ['proposed', 'pending', 'booked', 'arrived', 'checked-in']

    def can_cancel(self):
        """
        Check if appointment can be cancelled.

        Returns:
            bool: True if appointment can be cancelled
        """
        return self.status in ['proposed', 'pending', 'booked', 'waitlist']

    def can_check_in(self):
        """
        Check if patient can check in for appointment.

        Returns:
            bool: True if check-in is allowed
        """
        from django.utils import timezone
        from datetime import timedelta

        # Allow check-in 30 minutes before appointment
        check_in_window = self.start - timedelta(minutes=30)
        now = timezone.now()

        return (
            self.status == 'booked' and
            now >= check_in_window and
            now < self.end
        )

    def get_status_display_color(self):
        """
        Get color code for status display.

        Returns:
            str: Color code for UI display
        """
        status_colors = {
            'proposed': 'gray',
            'pending': 'yellow',
            'booked': 'blue',
            'arrived': 'green',
            'fulfilled': 'green',
            'cancelled': 'red',
            'noshow': 'red',
            'entered-in-error': 'red',
            'checked-in': 'blue',
            'waitlist': 'orange',
        }
        return status_colors.get(self.status, 'gray')
