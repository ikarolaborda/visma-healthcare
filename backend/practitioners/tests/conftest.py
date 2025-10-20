"""
Shared pytest fixtures for practitioner tests.

Provides authentication and common test utilities.
"""
import pytest
from datetime import date
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from practitioners.models import Practitioner


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
def sample_practitioner_data():
    """Sample practitioner data for testing."""
    return {
        'prefix': 'Dr.',
        'given_name': 'John',
        'family_name': 'Smith',
        'gender': 'male',
        'birth_date': date(1980, 1, 15),
        'npi': '1234567890',
        'license_number': 'MD-98765',
        'specialization': 'General Practice',
        'qualification': 'MD',
        'years_of_experience': 15,
        'email': 'dr.smith@hospital.com',
        'phone': '+1-555-0100',
        'address_line': '456 Medical Center',
        'address_city': 'Boston',
        'address_state': 'MA',
        'address_postal_code': '02101',
        'address_country': 'USA',
        'active': True
    }


@pytest.fixture
def sample_practitioner(db, sample_practitioner_data):
    """Create a sample practitioner for testing."""
    return Practitioner.objects.create(**sample_practitioner_data)


@pytest.fixture
def fhir_practitioner_data():
    """Sample FHIR Practitioner resource for testing."""
    return {
        'resourceType': 'Practitioner',
        'active': True,
        'name': [
            {
                'use': 'official',
                'family': 'Johnson',
                'given': ['Emily'],
                'prefix': ['Dr.']
            }
        ],
        'gender': 'female',
        'birthDate': '1985-03-20',
        'identifier': [
            {
                'system': 'http://hl7.org/fhir/sid/us-npi',
                'value': '9876543210',
                'use': 'official'
            }
        ],
        'telecom': [
            {
                'system': 'email',
                'value': 'dr.johnson@hospital.com',
                'use': 'work'
            },
            {
                'system': 'phone',
                'value': '+1-555-0200',
                'use': 'work'
            }
        ],
        'address': [
            {
                'use': 'work',
                'line': ['789 Healthcare Blvd'],
                'city': 'Chicago',
                'state': 'IL',
                'postalCode': '60601',
                'country': 'USA'
            }
        ],
        'qualification': [
            {
                'code': {
                    'text': 'MD, PhD'
                }
            }
        ],
        'specialization': 'Cardiology',
        'years_of_experience': 12
    }
