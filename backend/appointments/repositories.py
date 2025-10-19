"""
Repository layer for Appointment data access.

This module implements the Repository Pattern for Appointment models,
with Redis caching for practitioner availability queries.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from django.db.models import Q
from django.core.cache import cache
from django.utils import timezone
from common.repositories import BaseRepository
from .models import Appointment


class AppointmentRepository(BaseRepository[Appointment]):
    """
    Repository for managing Appointment data access.

    This class extends BaseRepository to provide Appointment-specific
    data access methods with Redis caching for availability checks.

    Inherited methods include:
    - get_by_id(id: UUID) -> Optional[Appointment]
    - get_all(limit: Optional[int]) -> QuerySet[Appointment]
    - filter_by(**kwargs) -> QuerySet[Appointment]
    - create(**data) -> Appointment
    - update(id: UUID, **data) -> Optional[Appointment]
    - delete(id: UUID) -> bool
    - paginate(page: int, page_size: int, **filters) -> Dict
    """

    model = Appointment
    cache_ttl = 900  # 15 minutes for appointment-related caching

    def find_by_patient(self, patient_id: UUID, limit: Optional[int] = None) -> List[Appointment]:
        """
        Find all appointments for a specific patient.

        Args:
            patient_id: UUID of the patient
            limit: Optional limit on number of results

        Returns:
            List of Appointment instances
        """
        queryset = self.filter_by(patient_id=patient_id).order_by('-start')
        if limit:
            queryset = queryset[:limit]
        return list(queryset)

    def find_by_practitioner(self, practitioner_id: UUID, limit: Optional[int] = None) -> List[Appointment]:
        """
        Find all appointments for a specific practitioner.

        Args:
            practitioner_id: UUID of the practitioner
            limit: Optional limit on number of results

        Returns:
            List of Appointment instances
        """
        queryset = self.filter_by(practitioner_id=practitioner_id).order_by('-start')
        if limit:
            queryset = queryset[:limit]
        return list(queryset)

    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        patient_id: Optional[UUID] = None,
        practitioner_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Appointment]:
        """
        Find appointments within a date range with optional filters.

        Args:
            start_date: Start of date range
            end_date: End of date range
            patient_id: Optional patient UUID filter
            practitioner_id: Optional practitioner UUID filter
            status: Optional status filter

        Returns:
            List of Appointment instances
        """
        filters = Q(start__gte=start_date, start__lte=end_date)

        if patient_id:
            filters &= Q(patient_id=patient_id)

        if practitioner_id:
            filters &= Q(practitioner_id=practitioner_id)

        if status:
            filters &= Q(status=status)

        return list(self.model.objects.filter(filters).order_by('start'))

    def find_upcoming(
        self,
        patient_id: Optional[UUID] = None,
        practitioner_id: Optional[UUID] = None,
        days_ahead: int = 30
    ) -> List[Appointment]:
        """
        Find upcoming appointments within specified number of days.

        Args:
            patient_id: Optional patient UUID filter
            practitioner_id: Optional practitioner UUID filter
            days_ahead: Number of days to look ahead (default 30)

        Returns:
            List of upcoming Appointment instances
        """
        now = timezone.now()
        end_date = now + timedelta(days=days_ahead)

        filters = Q(
            start__gte=now,
            start__lte=end_date,
            status__in=['proposed', 'pending', 'booked', 'waitlist']
        )

        if patient_id:
            filters &= Q(patient_id=patient_id)

        if practitioner_id:
            filters &= Q(practitioner_id=practitioner_id)

        return list(self.model.objects.filter(filters).order_by('start'))

    def find_conflicts(
        self,
        practitioner_id: UUID,
        start: datetime,
        end: datetime,
        exclude_appointment_id: Optional[UUID] = None
    ) -> List[Appointment]:
        """
        Find conflicting appointments for a practitioner in a time range.

        Args:
            practitioner_id: UUID of the practitioner
            start: Start time of proposed appointment
            end: End time of proposed appointment
            exclude_appointment_id: Optional appointment ID to exclude (for updates)

        Returns:
            List of conflicting Appointment instances
        """
        # Find appointments that overlap with the proposed time slot
        # An appointment conflicts if:
        # 1. It starts before the proposed end time, AND
        # 2. It ends after the proposed start time, AND
        # 3. It's in an active status
        filters = Q(
            practitioner_id=practitioner_id,
            start__lt=end,
            end__gt=start,
            status__in=['proposed', 'pending', 'booked', 'arrived', 'checked-in']
        )

        if exclude_appointment_id:
            filters &= ~Q(id=exclude_appointment_id)

        return list(self.model.objects.filter(filters))

    def check_availability(
        self,
        practitioner_id: UUID,
        start: datetime,
        end: datetime,
        exclude_appointment_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if a practitioner is available for a time slot (with Redis caching).

        This method caches the availability check for 15 minutes to reduce
        database queries for frequently checked time slots.

        Args:
            practitioner_id: UUID of the practitioner
            start: Start time of proposed appointment
            end: End time of proposed appointment
            exclude_appointment_id: Optional appointment ID to exclude

        Returns:
            True if available, False if conflicting appointments exist
        """
        # Create cache key
        cache_key = f"availability:{practitioner_id}:{start.isoformat()}:{end.isoformat()}"
        if exclude_appointment_id:
            cache_key += f":{exclude_appointment_id}"

        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Query database
        conflicts = self.find_conflicts(
            practitioner_id=practitioner_id,
            start=start,
            end=end,
            exclude_appointment_id=exclude_appointment_id
        )

        is_available = len(conflicts) == 0

        # Cache the result
        cache.set(cache_key, is_available, timeout=self.cache_ttl)

        return is_available

    def get_practitioner_schedule(
        self,
        practitioner_id: UUID,
        date: datetime
    ) -> List[Appointment]:
        """
        Get all appointments for a practitioner on a specific date (with caching).

        Args:
            practitioner_id: UUID of the practitioner
            date: The date to get schedule for

        Returns:
            List of Appointment instances for that day
        """
        # Create cache key
        cache_key = f"schedule:{practitioner_id}:{date.date().isoformat()}"

        # Check cache first
        cached_schedule = cache.get(cache_key)
        if cached_schedule is not None:
            return cached_schedule

        # Query database
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        schedule = self.find_by_date_range(
            start_date=start_of_day,
            end_date=end_of_day,
            practitioner_id=practitioner_id
        )

        # Cache the result
        cache.set(cache_key, schedule, timeout=self.cache_ttl)

        return schedule

    def find_by_status(self, status: str, limit: Optional[int] = None) -> List[Appointment]:
        """
        Find all appointments with a specific status.

        Args:
            status: The appointment status
            limit: Optional limit on number of results

        Returns:
            List of Appointment instances
        """
        queryset = self.filter_by(status=status).order_by('-start')
        if limit:
            queryset = queryset[:limit]
        return list(queryset)

    def find_todays_appointments(
        self,
        patient_id: Optional[UUID] = None,
        practitioner_id: Optional[UUID] = None
    ) -> List[Appointment]:
        """
        Find all appointments for today.

        Args:
            patient_id: Optional patient UUID filter
            practitioner_id: Optional practitioner UUID filter

        Returns:
            List of today's Appointment instances
        """
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        return self.find_by_date_range(
            start_date=start_of_day,
            end_date=end_of_day,
            patient_id=patient_id,
            practitioner_id=practitioner_id
        )

    def invalidate_availability_cache(self, practitioner_id: UUID, date: datetime):
        """
        Invalidate cached availability and schedule for a practitioner on a date.

        This should be called when an appointment is created, updated, or deleted.

        Args:
            practitioner_id: UUID of the practitioner
            date: The date to invalidate cache for
        """
        # Invalidate schedule cache
        schedule_key = f"schedule:{practitioner_id}:{date.date().isoformat()}"
        cache.delete(schedule_key)

        # Note: Individual availability cache keys are harder to invalidate
        # since they include specific time ranges. They will expire naturally
        # after cache_ttl (15 minutes). For critical operations, consider
        # implementing a more sophisticated cache invalidation strategy.

    def get_appointment_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        practitioner_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get appointment statistics for a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            practitioner_id: Optional practitioner UUID filter

        Returns:
            Dictionary containing statistics
        """
        filters = Q(start__gte=start_date, start__lte=end_date)

        if practitioner_id:
            filters &= Q(practitioner_id=practitioner_id)

        appointments = self.model.objects.filter(filters)

        return {
            'total': appointments.count(),
            'booked': appointments.filter(status='booked').count(),
            'fulfilled': appointments.filter(status='fulfilled').count(),
            'cancelled': appointments.filter(status='cancelled').count(),
            'noshow': appointments.filter(status='noshow').count(),
        }
