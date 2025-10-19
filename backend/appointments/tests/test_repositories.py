"""
Tests for Appointment repository.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from appointments.repositories import AppointmentRepository
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentRepository:
    """Test Appointment repository functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        self.repository = AppointmentRepository()

    def test_find_by_patient(self, sample_appointment, sample_patient):
        """Test finding appointments by patient."""
        appointments = self.repository.find_by_patient(sample_patient.id)
        assert len(appointments) == 1
        assert appointments[0] == sample_appointment

    def test_find_by_practitioner(self, sample_appointment, sample_practitioner):
        """Test finding appointments by practitioner."""
        appointments = self.repository.find_by_practitioner(sample_practitioner.id)
        assert len(appointments) == 1
        assert appointments[0] == sample_appointment

    def test_find_by_date_range(self, sample_appointment):
        """Test finding appointments by date range."""
        start_date = timezone.now()
        end_date = timezone.now() + timedelta(days=7)
        
        appointments = self.repository.find_by_date_range(start_date, end_date)
        assert len(appointments) == 1
        assert appointments[0] == sample_appointment

    def test_find_upcoming(self, sample_appointment, past_appointment):
        """Test finding upcoming appointments."""
        appointments = self.repository.find_upcoming()
        assert len(appointments) == 1
        assert appointments[0] == sample_appointment
        assert past_appointment not in appointments

    def test_find_conflicts_no_conflict(self, sample_practitioner):
        """Test finding conflicts when there are none."""
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(hours=1)
        
        conflicts = self.repository.find_conflicts(
            sample_practitioner.id,
            start,
            end
        )
        assert len(conflicts) == 0

    def test_find_conflicts_with_conflict(self, sample_appointment, sample_practitioner):
        """Test finding conflicts when there is an overlap."""
        # Try to book during existing appointment
        start = sample_appointment.start + timedelta(minutes=30)
        end = start + timedelta(hours=1)
        
        conflicts = self.repository.find_conflicts(
            sample_practitioner.id,
            start,
            end
        )
        assert len(conflicts) == 1
        assert conflicts[0] == sample_appointment

    def test_find_conflicts_exclude_appointment(self, sample_appointment, sample_practitioner):
        """Test finding conflicts excluding specific appointment."""
        conflicts = self.repository.find_conflicts(
            sample_practitioner.id,
            sample_appointment.start,
            sample_appointment.end,
            exclude_appointment_id=sample_appointment.id
        )
        assert len(conflicts) == 0

    def test_check_availability_true(self, sample_practitioner):
        """Test checking availability when practitioner is available."""
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(hours=1)
        
        is_available = self.repository.check_availability(
            sample_practitioner.id,
            start,
            end
        )
        assert is_available is True

    def test_check_availability_false(self, sample_appointment, sample_practitioner):
        """Test checking availability when practitioner has conflict."""
        start = sample_appointment.start + timedelta(minutes=30)
        end = start + timedelta(hours=1)
        
        is_available = self.repository.check_availability(
            sample_practitioner.id,
            start,
            end
        )
        assert is_available is False

    def test_find_by_status(self, sample_appointment):
        """Test finding appointments by status."""
        appointments = self.repository.find_by_status('proposed')
        assert len(appointments) == 1
        assert appointments[0] == sample_appointment

    def test_find_todays_appointments(self, sample_patient, sample_practitioner):
        """Test finding today's appointments."""
        # Create appointment for today
        start = timezone.now() + timedelta(hours=2)
        end = start + timedelta(hours=1)
        today_appointment = Appointment.objects.create(
            status='booked',
            start=start,
            end=end,
            patient=sample_patient,
            practitioner=sample_practitioner
        )
        
        appointments = self.repository.find_todays_appointments()
        assert len(appointments) == 1
        assert appointments[0] == today_appointment

    def test_get_appointment_statistics(self, sample_appointment_data):
        """Test getting appointment statistics."""
        # Create appointments with different statuses
        Appointment.objects.create(**{**sample_appointment_data, 'status': 'booked'})
        Appointment.objects.create(**{
            **sample_appointment_data,
            'status': 'fulfilled',
            'start': sample_appointment_data['start'] + timedelta(hours=2),
            'end': sample_appointment_data['end'] + timedelta(hours=2),
        })
        Appointment.objects.create(**{
            **sample_appointment_data,
            'status': 'cancelled',
            'start': sample_appointment_data['start'] + timedelta(hours=4),
            'end': sample_appointment_data['end'] + timedelta(hours=4),
        })
        
        start_date = timezone.now()
        end_date = timezone.now() + timedelta(days=7)
        
        stats = self.repository.get_appointment_statistics(start_date, end_date)
        assert stats['total'] >= 3
        assert stats['booked'] >= 1
        assert stats['fulfilled'] >= 1
        assert stats['cancelled'] >= 1
