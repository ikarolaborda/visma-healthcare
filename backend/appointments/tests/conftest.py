"""
Shared pytest fixtures for appointment tests.

Provides authentication and common test utilities.
"""
import pytest
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from patients.models import Patient
from practitioners.models import Practitioner
from appointments.models import Appointment


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user for authentication."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPassword123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """
    Create an authenticated API client with JWT token.

    This fixture automatically adds the JWT Bearer token to all requests,
    allowing tests to access protected endpoints.
    """
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def sample_patient(db):
    """Create a sample patient for testing."""
    from datetime import date
    return Patient.objects.create(
        given_name='Jane',
        family_name='Doe',
        gender='female',
        birth_date=date(1990, 5, 15),
        email='jane.doe@example.com',
        phone='+1-555-0123',
        address_line='123 Main St',
        address_city='Boston',
        address_state='MA',
        address_postal_code='02101',
        address_country='USA',
        active=True
    )


@pytest.fixture
def sample_practitioner(db):
    """Create a sample practitioner for testing."""
    from datetime import date
    return Practitioner.objects.create(
        prefix='Dr.',
        given_name='John',
        family_name='Smith',
        gender='male',
        birth_date=date(1980, 1, 15),
        npi='1234567890',
        license_number='MD-98765',
        specialization='General Practice',
        qualification='MD',
        years_of_experience=15,
        email='dr.smith@hospital.com',
        phone='+1-555-0100',
        address_line='456 Medical Center',
        address_city='Boston',
        address_state='MA',
        address_postal_code='02101',
        address_country='USA',
        active=True
    )


@pytest.fixture
def sample_appointment_data(sample_patient, sample_practitioner):
    """Sample appointment data for testing."""
    start_time = timezone.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    return {
        'status': 'proposed',
        'service_category': 'General Medicine',
        'service_type': 'Consultation',
        'specialty': 'General Practice',
        'appointment_type': 'Routine',
        'reason_code': 'Annual Checkup',
        'reason_description': 'Annual physical examination',
        'priority': 5,
        'description': 'Annual physical examination appointment',
        'comment': 'Patient requested morning appointment',
        'patient_instruction': 'Please arrive 15 minutes early',
        'start': start_time,
        'end': end_time,
        'minutes_duration': 60,
        'patient': sample_patient,
        'patient_status': 'needs-action',
        'practitioner': sample_practitioner,
        'practitioner_status': 'needs-action',
        'practitioner_required': 'required'
    }


@pytest.fixture
def sample_appointment(db, sample_appointment_data):
    """Create a sample appointment for testing."""
    return Appointment.objects.create(**sample_appointment_data)


@pytest.fixture
def booked_appointment(db, sample_appointment_data):
    """Create a booked appointment for testing."""
    data = sample_appointment_data.copy()
    data['status'] = 'booked'
    data['patient_status'] = 'accepted'
    data['practitioner_status'] = 'accepted'
    return Appointment.objects.create(**data)


@pytest.fixture
def past_appointment(db, sample_patient, sample_practitioner):
    """Create a past appointment for testing."""
    start_time = timezone.now() - timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    return Appointment.objects.create(
        status='booked',
        start=start_time,
        end=end_time,
        minutes_duration=60,
        patient=sample_patient,
        practitioner=sample_practitioner
    )


@pytest.fixture
def fhir_appointment_data(sample_patient, sample_practitioner):
    """Sample FHIR Appointment resource for testing."""
    start_time = timezone.now() + timedelta(days=2)
    end_time = start_time + timedelta(hours=1)
    
    return {
        'resourceType': 'Appointment',
        'status': 'proposed',
        'serviceCategory': [{'text': 'General Medicine'}],
        'serviceType': [{'text': 'Consultation'}],
        'specialty': [{'text': 'General Practice'}],
        'appointmentType': {'text': 'Routine'},
        'reasonCode': [{'text': 'Follow-up'}],
        'priority': 5,
        'description': 'Follow-up appointment',
        'comment': 'Patient requested afternoon slot',
        'patientInstruction': 'Bring previous test results',
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
        'minutesDuration': 60,
        'participant': [
            {
                'actor': {
                    'reference': f'Patient/{sample_patient.id}',
                    'display': sample_patient.get_full_name()
                },
                'status': 'needs-action'
            },
            {
                'actor': {
                    'reference': f'Practitioner/{sample_practitioner.id}',
                    'display': sample_practitioner.get_full_name()
                },
                'required': 'required',
                'status': 'needs-action'
            }
        ]
    }
