"""
Integration tests for Patient API endpoints.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from patients.models import Patient
from patients.factories import PatientFactory, create_diverse_patient_cohort
from datetime import date
import json


@pytest.fixture
def sample_patient_data():
    """Sample FHIR Patient data for testing."""
    return {
        'resourceType': 'Patient',
        'name': [
            {
                'use': 'official',
                'family': 'Doe',
                'given': ['John', 'Michael']
            }
        ],
        'gender': 'male',
        'birthDate': '1990-01-01',
        'address': [
            {
                'use': 'home',
                'line': ['123 Main St'],
                'city': 'New York',
                'state': 'NY',
                'postalCode': '10001',
                'country': 'USA'
            }
        ],
        'telecom': [
            {
                'system': 'email',
                'value': 'john.doe@example.com',
                'use': 'home'
            },
            {
                'system': 'phone',
                'value': '+1-555-123-4567',
                'use': 'home'
            }
        ]
    }


@pytest.fixture
def sample_patient():
    """Create a sample patient in the database using factory."""
    return PatientFactory(
        family_name='Smith',
        given_name='Jane',
        gender='female',
        birth_date=date(1985, 5, 15),
        email='jane.smith@example.com',
        phone='+1-555-987-6543'
    )


@pytest.mark.django_db
class TestPatientListEndpoint:
    """Test GET /fhir/Patient/ endpoint."""

    def test_list_patients_empty(self, authenticated_client):
        """Test listing patients when database is empty."""
        response = authenticated_client.get('/fhir/Patient/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['resourceType'] == 'Bundle'
        assert data['type'] == 'searchset'
        assert data['total'] == 0
        assert data['entry'] == []

    def test_list_patients_with_data(self, authenticated_client, sample_patient):
        """Test listing patients with existing data."""
        response = authenticated_client.get('/fhir/Patient/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['resourceType'] == 'Bundle'
        assert data['total'] == 1
        assert len(data['entry']) == 1

        patient_resource = data['entry'][0]['resource']
        assert patient_resource['resourceType'] == 'Patient'
        assert patient_resource['id'] == str(sample_patient.id)


@pytest.mark.django_db
class TestPatientCreateEndpoint:
    """Test POST /fhir/Patient/ endpoint."""

    def test_create_patient_success(self, authenticated_client, sample_patient_data):
        """Test creating a patient with valid FHIR data."""
        response = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(sample_patient_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['resourceType'] == 'Patient'
        assert 'id' in data
        assert data['name'][0]['family'] == 'Doe'
        assert data['gender'] == 'male'

        # Verify in database
        patient = Patient.objects.get(id=data['id'])
        assert patient.family_name == 'Doe'
        assert patient.given_name == 'John'

    def test_create_patient_invalid_resource_type(self, authenticated_client):
        """Test creating a patient with invalid resource type."""
        invalid_data = {
            'resourceType': 'Observation',
            'name': [{'family': 'Test', 'given': ['User']}],
            'gender': 'male',
            'birthDate': '1990-01-01'
        }

        response = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_patient_missing_required_fields(self, authenticated_client):
        """Test creating a patient without required fields."""
        invalid_data = {
            'resourceType': 'Patient',
            'name': [{'family': 'Test'}]
            # Missing gender and birthDate
        }

        response = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPatientRetrieveEndpoint:
    """Test GET /fhir/Patient/{id}/ endpoint."""

    def test_retrieve_patient_success(self, authenticated_client, sample_patient):
        """Test retrieving a patient by ID."""
        response = authenticated_client.get(f'/fhir/Patient/{sample_patient.id}/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['resourceType'] == 'Patient'
        assert data['id'] == str(sample_patient.id)
        assert data['name'][0]['family'] == 'Smith'
        assert data['name'][0]['given'][0] == 'Jane'

    def test_retrieve_patient_not_found(self, authenticated_client):
        """Test retrieving a non-existent patient."""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = authenticated_client.get(f'/fhir/Patient/{fake_id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPatientUpdateEndpoint:
    """Test PUT /fhir/Patient/{id}/ endpoint."""

    def test_update_patient_success(self, authenticated_client, sample_patient, sample_patient_data):
        """Test updating a patient with valid data."""
        sample_patient_data['name'][0]['family'] = 'Updated'

        response = authenticated_client.put(
            f'/fhir/Patient/{sample_patient.id}/',
            data=json.dumps(sample_patient_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'][0]['family'] == 'Updated'

        # Verify in database
        sample_patient.refresh_from_db()
        assert sample_patient.family_name == 'Updated'

    def test_update_patient_not_found(self, authenticated_client, sample_patient_data):
        """Test updating a non-existent patient."""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = authenticated_client.put(
            f'/fhir/Patient/{fake_id}/',
            data=json.dumps(sample_patient_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPatientDeleteEndpoint:
    """Test DELETE /fhir/Patient/{id}/ endpoint."""

    def test_delete_patient_success(self, authenticated_client, sample_patient):
        """Test deleting a patient."""
        patient_id = sample_patient.id
        response = authenticated_client.delete(f'/fhir/Patient/{patient_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted from database
        assert not Patient.objects.filter(id=patient_id).exists()

    def test_delete_patient_not_found(self, authenticated_client):
        """Test deleting a non-existent patient."""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = authenticated_client.delete(f'/fhir/Patient/{fake_id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
