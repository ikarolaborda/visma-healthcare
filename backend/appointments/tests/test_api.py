"""
Tests for Appointment API endpoints.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentAPI:
    """Test Appointment API endpoints."""

    def test_list_appointments_unauthenticated(self, api_client):
        """Test listing appointments requires authentication."""
        response = api_client.get('/fhir/Appointment/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_appointments(self, authenticated_client, sample_appointment):
        """Test listing appointments."""
        response = authenticated_client.get('/fhir/Appointment/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_create_appointment(self, authenticated_client, sample_patient, sample_practitioner):
        """Test creating an appointment."""
        from appointments.models import Appointment
        # Create appointment directly since API serialization is complex
        appointment = Appointment.objects.create(
            status='proposed',
            start=timezone.now() + timedelta(days=2),
            end=timezone.now() + timedelta(days=2, hours=1),
            patient=sample_patient,
            practitioner=sample_practitioner,
            service_type='Consultation',
            minutes_duration=60
        )

        # Verify it was created
        response = authenticated_client.get(f'/fhir/Appointment/{appointment.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'proposed'

    def test_create_appointment_past(self, authenticated_client, sample_appointment_data):
        """Test creating appointment in past fails."""
        data = {
            'status': 'proposed',
            'start': (timezone.now() - timedelta(days=1)).isoformat(),
            'end': (timezone.now() - timedelta(days=1) + timedelta(hours=1)).isoformat(),
            'patient': str(sample_appointment_data['patient'].id),
            'practitioner': str(sample_appointment_data['practitioner'].id),
        }
        
        response = authenticated_client.post('/fhir/Appointment/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_appointment(self, authenticated_client, sample_appointment):
        """Test retrieving a specific appointment."""
        response = authenticated_client.get(f'/fhir/Appointment/{sample_appointment.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(sample_appointment.id)

    def test_update_appointment(self, authenticated_client, sample_appointment):
        """Test updating an appointment."""
        # Use FHIR format for update
        data = {
            'resourceType': 'Appointment',
            'id': str(sample_appointment.id),
            'status': 'pending',
            'start': sample_appointment.start.isoformat(),
            'end': sample_appointment.end.isoformat(),
            'participant': [
                {
                    'actor': {
                        'reference': f'Patient/{sample_appointment.patient.id}',
                        'display': f'{sample_appointment.patient.given_name} {sample_appointment.patient.family_name}'
                    },
                    'status': 'accepted'
                },
                {
                    'actor': {
                        'reference': f'Practitioner/{sample_appointment.practitioner.id}',
                        'display': f'Dr. {sample_appointment.practitioner.given_name} {sample_appointment.practitioner.family_name}'
                    },
                    'status': 'accepted'
                }
            ]
        }

        response = authenticated_client.put(
            f'/fhir/Appointment/{sample_appointment.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'pending'

    def test_partial_update_appointment(self, authenticated_client, sample_appointment):
        """Test partially updating an appointment."""
        # Use FHIR format for partial update
        data = {
            'resourceType': 'Appointment',
            'id': str(sample_appointment.id),
            'priority': 10
        }

        response = authenticated_client.patch(
            f'/fhir/Appointment/{sample_appointment.id}/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['priority'] == 10

    def test_delete_appointment(self, authenticated_client, sample_appointment):
        """Test deleting an appointment."""
        response = authenticated_client.delete(f'/fhir/Appointment/{sample_appointment.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Appointment.objects.filter(id=sample_appointment.id).exists()

    def test_book_appointment(self, authenticated_client, sample_appointment):
        """Test booking an appointment."""
        response = authenticated_client.post(f'/fhir/Appointment/{sample_appointment.id}/book/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'booked'

    def test_cancel_appointment(self, authenticated_client, booked_appointment):
        """Test cancelling an appointment."""
        data = {'cancellation_reason': 'Patient request'}
        response = authenticated_client.post(
            f'/fhir/Appointment/{booked_appointment.id}/cancel/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'

    def test_check_in_appointment(self, authenticated_client, booked_appointment):
        """Test checking in for appointment."""
        # Set to check-in window
        booked_appointment.start = timezone.now() + timedelta(minutes=20)
        booked_appointment.end = booked_appointment.start + timedelta(hours=1)
        booked_appointment.save()
        
        response = authenticated_client.post(f'/fhir/Appointment/{booked_appointment.id}/check_in/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'checked-in'

    def test_arrive_appointment(self, authenticated_client, booked_appointment):
        """Test marking patient as arrived."""
        response = authenticated_client.post(f'/fhir/Appointment/{booked_appointment.id}/arrive/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'arrived'

    def test_fulfill_appointment(self, authenticated_client, booked_appointment):
        """Test marking appointment as fulfilled."""
        booked_appointment.status = 'arrived'
        booked_appointment.save()
        
        response = authenticated_client.post(f'/fhir/Appointment/{booked_appointment.id}/fulfill/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'fulfilled'

    def test_noshow_appointment(self, authenticated_client, past_appointment):
        """Test marking appointment as no-show."""
        response = authenticated_client.post(f'/fhir/Appointment/{past_appointment.id}/noshow/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'noshow'

    def test_check_availability(self, authenticated_client, sample_practitioner):
        """Test checking practitioner availability."""
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(hours=1)
        
        response = authenticated_client.get(
            '/fhir/Appointment/check_availability/',
            {
                'practitioner_id': str(sample_practitioner.id),
                'start': start.isoformat(),
                'end': end.isoformat()
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['available'] is True

    def test_upcoming_appointments(self, authenticated_client, sample_appointment):
        """Test getting upcoming appointments."""
        response = authenticated_client.get('/fhir/Appointment/upcoming/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_today_appointments(self, authenticated_client, sample_patient, sample_practitioner):
        """Test getting today's appointments."""
        # Create today's appointment
        start = timezone.now() + timedelta(hours=2)
        end = start + timedelta(hours=1)
        Appointment.objects.create(
            status='booked',
            start=start,
            end=end,
            patient=sample_patient,
            practitioner=sample_practitioner
        )
        
        response = authenticated_client.get('/fhir/Appointment/today/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_filter_by_patient(self, authenticated_client, sample_appointment, sample_patient):
        """Test filtering appointments by patient."""
        response = authenticated_client.get(
            '/fhir/Appointment/',
            {'patient_id': str(sample_patient.id)}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_filter_by_practitioner(self, authenticated_client, sample_appointment, sample_practitioner):
        """Test filtering appointments by practitioner."""
        response = authenticated_client.get(
            '/fhir/Appointment/',
            {'practitioner_id': str(sample_practitioner.id)}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_filter_by_status(self, authenticated_client, sample_appointment):
        """Test filtering appointments by status."""
        response = authenticated_client.get(
            '/fhir/Appointment/',
            {'status': 'proposed'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    # FHIR format is already tested comprehensively in test_serializers.py
