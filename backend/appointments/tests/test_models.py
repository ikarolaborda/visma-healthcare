"""
Tests for Appointment model.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentModel:
    """Test Appointment model functionality."""

    def test_create_appointment(self, sample_appointment_data):
        """Test creating an appointment."""
        appointment = Appointment.objects.create(**sample_appointment_data)
        assert appointment.id is not None
        assert appointment.status == 'proposed'
        assert appointment.patient == sample_appointment_data['patient']
        assert appointment.practitioner == sample_appointment_data['practitioner']

    def test_appointment_str(self, sample_appointment):
        """Test string representation of appointment."""
        expected = f"{sample_appointment.patient.get_full_name()} with {sample_appointment.practitioner.get_full_name()} on {sample_appointment.start.strftime('%Y-%m-%d %H:%M')}"
        assert str(sample_appointment) == expected

    def test_get_duration_minutes(self, sample_appointment):
        """Test getting appointment duration in minutes."""
        duration = sample_appointment.get_duration_minutes()
        assert duration == 60  # 1 hour appointment

    def test_is_upcoming(self, sample_appointment):
        """Test checking if appointment is upcoming."""
        assert sample_appointment.is_upcoming() is True

    def test_is_upcoming_past(self, past_appointment):
        """Test checking if past appointment is upcoming."""
        assert past_appointment.is_upcoming() is False

    def test_is_active_booked(self, booked_appointment):
        """Test checking if booked appointment is active."""
        assert booked_appointment.is_active() is True

    def test_is_active_cancelled(self, sample_appointment):
        """Test checking if cancelled appointment is not active."""
        sample_appointment.status = 'cancelled'
        sample_appointment.save()
        assert sample_appointment.is_active() is False

    def test_can_cancel_booked(self, booked_appointment):
        """Test that booked appointments can be cancelled."""
        assert booked_appointment.can_cancel() is True

    def test_can_cancel_fulfilled(self, booked_appointment):
        """Test that fulfilled appointments cannot be cancelled."""
        booked_appointment.status = 'fulfilled'
        booked_appointment.save()
        assert booked_appointment.can_cancel() is False

    def test_can_check_in_booked_in_window(self, booked_appointment):
        """Test that patient can check in within 30 minute window."""
        # Set appointment start to 20 minutes from now
        booked_appointment.start = timezone.now() + timedelta(minutes=20)
        booked_appointment.end = booked_appointment.start + timedelta(hours=1)
        booked_appointment.save()
        assert booked_appointment.can_check_in() is True

    def test_can_check_in_too_early(self, booked_appointment):
        """Test that patient cannot check in too early."""
        # Appointment is in the future (already set to tomorrow)
        assert booked_appointment.can_check_in() is False

    def test_can_check_in_wrong_status(self, sample_appointment):
        """Test that proposed appointments cannot be checked in."""
        # Set to check-in window
        sample_appointment.start = timezone.now() + timedelta(minutes=20)
        sample_appointment.end = sample_appointment.start + timedelta(hours=1)
        sample_appointment.save()
        assert sample_appointment.can_check_in() is False

    def test_get_status_display_color(self, sample_appointment):
        """Test getting color for appointment status."""
        color = sample_appointment.get_status_display_color()
        assert color == 'gray'  # proposed

        sample_appointment.status = 'booked'
        assert sample_appointment.get_status_display_color() == 'blue'

        sample_appointment.status = 'fulfilled'
        assert sample_appointment.get_status_display_color() == 'green'

        sample_appointment.status = 'cancelled'
        assert sample_appointment.get_status_display_color() == 'red'

    def test_appointment_ordering(self, sample_appointment_data):
        """Test that appointments are ordered by start time descending."""
        # Create two appointments with different start times
        appointment1_data = sample_appointment_data.copy()
        appointment1 = Appointment.objects.create(**appointment1_data)

        appointment2_data = sample_appointment_data.copy()
        appointment2_data['start'] = appointment2_data['start'] + timedelta(days=1)
        appointment2_data['end'] = appointment2_data['end'] + timedelta(days=1)
        appointment2 = Appointment.objects.create(**appointment2_data)

        appointments = list(Appointment.objects.all())
        assert appointments[0] == appointment2  # Later appointment first
        assert appointments[1] == appointment1

    def test_appointment_relationships(self, sample_appointment):
        """Test appointment relationships with patient and practitioner."""
        # Test forward relationships
        assert sample_appointment.patient is not None
        assert sample_appointment.practitioner is not None

        # Test reverse relationships
        patient_appointments = sample_appointment.patient.appointments.all()
        assert sample_appointment in patient_appointments

        practitioner_appointments = sample_appointment.practitioner.appointments.all()
        assert sample_appointment in practitioner_appointments

    def test_appointment_status_choices(self, sample_appointment):
        """Test that all status choices are valid."""
        valid_statuses = [
            'proposed', 'pending', 'booked', 'arrived', 'fulfilled',
            'cancelled', 'noshow', 'entered-in-error', 'checked-in', 'waitlist'
        ]
        for status in valid_statuses:
            sample_appointment.status = status
            sample_appointment.save()
            assert sample_appointment.status == status
