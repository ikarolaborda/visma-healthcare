"""
Tests for Appointment service.
"""
import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from appointments.services import AppointmentService
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentService:
    """Test Appointment service functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        self.service = AppointmentService()

    def test_validate_create_success(self, sample_appointment_data):
        """Test successful appointment creation validation."""
        # Remove related objects for validation
        data = sample_appointment_data.copy()
        data['patient_id'] = data.pop('patient').id
        data['practitioner_id'] = data.pop('practitioner').id
        
        # Should not raise exception
        self.service.validate_create(data)

    def test_validate_create_missing_patient(self, sample_appointment_data):
        """Test validation fails when patient is missing."""
        data = sample_appointment_data.copy()
        data.pop('patient')
        
        with pytest.raises(ValidationError, match='Patient is required'):
            self.service.validate_create(data)

    def test_validate_create_end_before_start(self, sample_appointment_data):
        """Test validation fails when end time is before start time."""
        data = sample_appointment_data.copy()
        data['patient_id'] = data.pop('patient').id
        data['practitioner_id'] = data.pop('practitioner').id
        data['end'] = data['start'] - timedelta(hours=1)
        
        with pytest.raises(ValidationError, match='End time must be after start time'):
            self.service.validate_create(data)

    def test_validate_create_past_appointment(self, sample_appointment_data):
        """Test validation fails for past appointments."""
        data = sample_appointment_data.copy()
        data['patient_id'] = data.pop('patient').id
        data['practitioner_id'] = data.pop('practitioner').id
        data['start'] = timezone.now() - timedelta(days=1)
        data['end'] = data['start'] + timedelta(hours=1)
        
        with pytest.raises(ValidationError, match='Cannot create appointments in the past'):
            self.service.validate_create(data)

    def test_validate_create_too_long(self, sample_appointment_data):
        """Test validation fails for appointments longer than 24 hours."""
        data = sample_appointment_data.copy()
        data['patient_id'] = data.pop('patient').id
        data['practitioner_id'] = data.pop('practitioner').id
        data['end'] = data['start'] + timedelta(hours=25)
        
        with pytest.raises(ValidationError, match='cannot exceed 24 hours'):
            self.service.validate_create(data)

    def test_validate_create_conflict(self, sample_appointment, sample_appointment_data):
        """Test validation fails when there's a scheduling conflict."""
        data = sample_appointment_data.copy()
        data['patient_id'] = data.pop('patient').id
        data['practitioner_id'] = data.pop('practitioner').id
        data['start'] = sample_appointment.start + timedelta(minutes=30)
        data['end'] = data['start'] + timedelta(hours=1)
        
        with pytest.raises(ValidationError, match='conflicting appointments'):
            self.service.validate_create(data)

    def test_book_appointment_success(self, sample_appointment):
        """Test successfully booking an appointment."""
        booked = self.service.book_appointment(sample_appointment.id)
        assert booked.status == 'booked'
        assert booked.patient_status == 'accepted'
        assert booked.practitioner_status == 'accepted'

    def test_book_appointment_wrong_status(self, booked_appointment):
        """Test booking fails for already booked appointment."""
        with pytest.raises(ValidationError, match='Cannot book appointment with status'):
            self.service.book_appointment(booked_appointment.id)

    def test_cancel_appointment_success(self, booked_appointment):
        """Test successfully cancelling an appointment."""
        cancelled = self.service.cancel_appointment(
            booked_appointment.id,
            cancellation_reason='Patient request'
        )
        assert cancelled.status == 'cancelled'
        assert cancelled.cancellation_reason == 'Patient request'

    def test_cancel_appointment_wrong_status(self, sample_appointment):
        """Test cancellation fails for fulfilled appointment."""
        sample_appointment.status = 'fulfilled'
        sample_appointment.save()
        
        with pytest.raises(ValidationError, match='Cannot cancel appointment'):
            self.service.cancel_appointment(sample_appointment.id)

    def test_check_in_appointment_success(self, booked_appointment):
        """Test successfully checking in for appointment."""
        # Set to check-in window
        booked_appointment.start = timezone.now() + timedelta(minutes=20)
        booked_appointment.end = booked_appointment.start + timedelta(hours=1)
        booked_appointment.save()
        
        checked_in = self.service.check_in_appointment(booked_appointment.id)
        assert checked_in.status == 'checked-in'

    def test_check_in_appointment_wrong_status(self, sample_appointment):
        """Test check-in fails for proposed appointment."""
        with pytest.raises(ValidationError):
            self.service.check_in_appointment(sample_appointment.id)

    def test_mark_as_arrived(self, booked_appointment):
        """Test marking appointment as arrived."""
        arrived = self.service.mark_as_arrived(booked_appointment.id)
        assert arrived.status == 'arrived'

    def test_mark_as_fulfilled(self, booked_appointment):
        """Test marking appointment as fulfilled."""
        booked_appointment.status = 'arrived'
        booked_appointment.save()
        
        fulfilled = self.service.mark_as_fulfilled(booked_appointment.id)
        assert fulfilled.status == 'fulfilled'

    def test_mark_as_noshow(self, past_appointment):
        """Test marking appointment as no-show."""
        noshow = self.service.mark_as_noshow(past_appointment.id)
        assert noshow.status == 'noshow'

    def test_mark_as_noshow_future(self, booked_appointment):
        """Test no-show fails for future appointments."""
        with pytest.raises(ValidationError, match='Cannot mark as no-show before'):
            self.service.mark_as_noshow(booked_appointment.id)

    def test_get_upcoming_appointments(self, sample_appointment, past_appointment):
        """Test getting upcoming appointments."""
        appointments = self.service.get_upcoming_appointments()
        assert sample_appointment in appointments
        assert past_appointment not in appointments

    def test_get_todays_appointments(self, sample_patient, sample_practitioner):
        """Test getting today's appointments."""
        # Create today's appointment
        start = timezone.now() + timedelta(hours=2)
        end = start + timedelta(hours=1)
        today_appointment = Appointment.objects.create(
            status='booked',
            start=start,
            end=end,
            patient=sample_patient,
            practitioner=sample_practitioner
        )
        
        appointments = self.service.get_todays_appointments()
        assert today_appointment in appointments

    def test_valid_status_transition(self):
        """Test valid status transitions."""
        assert self.service._is_valid_status_transition('proposed', 'booked') is True
        assert self.service._is_valid_status_transition('booked', 'arrived') is True
        assert self.service._is_valid_status_transition('arrived', 'fulfilled') is True

    def test_invalid_status_transition(self):
        """Test invalid status transitions."""
        assert self.service._is_valid_status_transition('proposed', 'fulfilled') is False
        assert self.service._is_valid_status_transition('fulfilled', 'booked') is False
        assert self.service._is_valid_status_transition('cancelled', 'booked') is False
