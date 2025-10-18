"""
Feature/Integration tests for complete patient management workflows.

Tests end-to-end user scenarios and complete application flows.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from patients.models import Patient
from patients.factories import (
    PatientFactory,
    create_test_scenarios,
    create_diverse_patient_cohort,
)
import json


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


@pytest.mark.django_db
class TestPatientRegistrationWorkflow:
    """Test complete patient registration workflow."""

    def test_complete_patient_registration_flow(self, authenticated_client):
        """
        Test complete flow: Create patient -> Verify creation -> Retrieve -> Verify data.
        """
        # Step 1: Create a new patient
        patient_data = {
            'resourceType': 'Patient',
            'active': True,
            'name': [{
                'use': 'official',
                'family': 'TestPatient',
                'given': ['Integration']
            }],
            'gender': 'male',
            'birthDate': '1990-05-15',
            'address': [{
                'use': 'home',
                'line': ['456 Test Ave'],
                'city': 'Test City',
                'state': 'TC',
                'postalCode': '12345',
                'country': 'USA'
            }],
            'telecom': [
                {
                    'system': 'email',
                    'value': 'integration.test@example.com',
                    'use': 'home'
                }
            ]
        }

        response = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(patient_data),
            content_type='application/json'
        )

        # Step 2: Verify creation was successful
        assert response.status_code == status.HTTP_201_CREATED
        created_data = response.json()
        patient_id = created_data['id']
        assert patient_id is not None

        # Step 3: Retrieve the patient
        response = authenticated_client.get(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_200_OK

        # Step 4: Verify all data matches
        retrieved_data = response.json()
        assert retrieved_data['name'][0]['family'] == 'TestPatient'
        assert retrieved_data['name'][0]['given'][0] == 'Integration'
        assert retrieved_data['gender'] == 'male'
        assert retrieved_data['birthDate'] == '1990-05-15'
        assert retrieved_data['address'][0]['city'] == 'Test City'

        # Step 5: Verify in database
        patient = Patient.objects.get(id=patient_id)
        assert patient.family_name == 'TestPatient'
        assert patient.given_name == 'Integration'


@pytest.mark.django_db
class TestPatientUpdateWorkflow:
    """Test patient update workflows."""

    def test_update_patient_contact_information(self, authenticated_client):
        """Test updating patient contact information."""
        # Step 1: Create initial patient
        patient = PatientFactory(
            email='old.email@example.com',
            phone='+1-555-111-1111'
        )

        # Step 2: Update email and phone
        update_data = {
            'resourceType': 'Patient',
            'name': [{
                'use': 'official',
                'family': patient.family_name,
                'given': [patient.given_name]
            }],
            'gender': patient.gender,
            'birthDate': patient.birth_date.isoformat(),
            'telecom': [
                {
                    'system': 'email',
                    'value': 'new.email@example.com',
                    'use': 'home'
                },
                {
                    'system': 'phone',
                    'value': '+1-555-222-2222',
                    'use': 'home'
                }
            ]
        }

        response = authenticated_client.put(
            f'/fhir/Patient/{patient.id}/',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        # Step 3: Verify update was successful
        assert response.status_code == status.HTTP_200_OK
        updated_data = response.json()

        # Find email and phone in telecom
        telecom_dict = {t['system']: t['value'] for t in updated_data['telecom']}
        assert telecom_dict['email'] == 'new.email@example.com'
        assert telecom_dict['phone'] == '+1-555-222-2222'

        # Step 4: Verify in database
        patient.refresh_from_db()
        assert patient.email == 'new.email@example.com'
        assert patient.phone == '+1-555-222-2222'

    def test_update_patient_address(self, authenticated_client):
        """Test updating patient address."""
        patient = PatientFactory()
        original_city = patient.address_city

        update_data = {
            'resourceType': 'Patient',
            'name': [{
                'family': patient.family_name,
                'given': [patient.given_name]
            }],
            'gender': patient.gender,
            'birthDate': patient.birth_date.isoformat(),
            'address': [{
                'use': 'home',
                'line': ['New Address Line'],
                'city': 'New City',
                'state': 'NC',
                'postalCode': '99999',
                'country': 'USA'
            }]
        }

        response = authenticated_client.put(
            f'/fhir/Patient/{patient.id}/',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_200_OK

        patient.refresh_from_db()
        assert patient.address_city == 'New City'
        assert patient.address_city != original_city


@pytest.mark.django_db
class TestPatientSearchWorkflow:
    """Test patient search and listing workflows."""

    def test_list_all_patients(self, authenticated_client):
        """Test listing all patients in FHIR Bundle format."""
        # Create diverse patient population
        patients = create_diverse_patient_cohort(count=20)

        response = authenticated_client.get('/fhir/Patient/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['resourceType'] == 'Bundle'
        assert data['type'] == 'searchset'
        assert data['total'] == 20
        assert len(data['entry']) == 20

        # Verify each entry has required structure
        for entry in data['entry']:
            assert 'resource' in entry
            resource = entry['resource']
            assert resource['resourceType'] == 'Patient'
            assert 'id' in resource
            assert 'name' in resource

    def test_empty_patient_list(self, authenticated_client):
        """Test listing patients when database is empty."""
        response = authenticated_client.get('/fhir/Patient/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['resourceType'] == 'Bundle'
        assert data['total'] == 0
        assert data['entry'] == []


@pytest.mark.django_db
class TestPatientDeletionWorkflow:
    """Test patient deletion workflows."""

    def test_delete_patient_complete_flow(self, authenticated_client):
        """Test complete deletion flow: Create -> Verify -> Delete -> Verify gone."""
        # Step 1: Create patient
        patient = PatientFactory()
        patient_id = patient.id

        # Step 2: Verify patient exists
        response = authenticated_client.get(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_200_OK

        # Step 3: Delete patient
        response = authenticated_client.delete(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Step 4: Verify patient is gone
        response = authenticated_client.get(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Step 5: Verify not in database
        assert not Patient.objects.filter(id=patient_id).exists()

    def test_delete_nonexistent_patient(self, authenticated_client):
        """Test deleting a patient that doesn't exist."""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = authenticated_client.delete(f'/fhir/Patient/{fake_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDataValidationWorkflow:
    """Test FHIR data validation workflows."""

    def test_invalid_fhir_resource_type(self, authenticated_client):
        """Test rejection of invalid FHIR resource type."""
        invalid_data = {
            'resourceType': 'Observation',  # Wrong type
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

    def test_missing_required_fields(self, authenticated_client):
        """Test validation of required FHIR fields."""
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

    def test_invalid_gender_code(self, authenticated_client):
        """Test rejection of invalid gender code."""
        invalid_data = {
            'resourceType': 'Patient',
            'name': [{'family': 'Test', 'given': ['User']}],
            'gender': 'invalid_gender',  # Not a valid FHIR gender code
            'birthDate': '1990-01-01'
        }

        response = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestBulkOperationsWorkflow:
    """Test bulk operations and data integrity."""

    def test_create_multiple_patients_data_integrity(self, authenticated_client):
        """Test creating multiple patients maintains data integrity."""
        # Create 10 patients via API
        created_ids = []

        for i in range(10):
            patient_data = {
                'resourceType': 'Patient',
                'name': [{
                    'family': f'Patient{i}',
                    'given': [f'Test{i}']
                }],
                'gender': 'male' if i % 2 == 0 else 'female',
                'birthDate': f'199{i % 10}-01-01'
            }

            response = authenticated_client.post(
                '/fhir/Patient/',
                data=json.dumps(patient_data),
                content_type='application/json'
            )

            assert response.status_code == status.HTTP_201_CREATED
            created_ids.append(response.json()['id'])

        # Verify all are unique
        assert len(created_ids) == len(set(created_ids))

        # Verify all exist in database
        assert Patient.objects.count() == 10

        # Verify each can be retrieved
        for patient_id in created_ids:
            response = authenticated_client.get(f'/fhir/Patient/{patient_id}/')
            assert response.status_code == status.HTTP_200_OK

    def test_list_large_patient_population(self, authenticated_client):
        """Test listing large patient population."""
        # Create 50 patients
        create_diverse_patient_cohort(count=50)

        response = authenticated_client.get('/fhir/Patient/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['total'] == 50
        assert len(data['entry']) == 50


@pytest.mark.django_db
class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_patient_lifecycle_complete(self, authenticated_client):
        """Test complete patient lifecycle: Create -> Update -> Retrieve -> Delete."""
        # Create
        patient_data = {
            'resourceType': 'Patient',
            'name': [{'family': 'Lifecycle', 'given': ['Test']}],
            'gender': 'female',
            'birthDate': '1995-03-20',
            'telecom': [{'system': 'email', 'value': 'lifecycle@test.com'}]
        }

        response = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(patient_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        patient_id = response.json()['id']

        # Update
        patient_data['telecom'][0]['value'] = 'updated@test.com'
        response = authenticated_client.put(
            f'/fhir/Patient/{patient_id}/',
            data=json.dumps(patient_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_200_OK

        # Retrieve and verify
        response = authenticated_client.get(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        email = next(t['value'] for t in data['telecom'] if t['system'] == 'email')
        assert email == 'updated@test.com'

        # Delete
        response = authenticated_client.delete(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify gone
        response = authenticated_client.get(f'/fhir/Patient/{patient_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_patients_same_name(self, authenticated_client):
        """Test system handles multiple patients with same name."""
        patient_data = {
            'resourceType': 'Patient',
            'name': [{'family': 'Smith', 'given': ['John']}],
            'gender': 'male',
            'birthDate': '1990-01-01'
        }

        # Create first patient
        response1 = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(patient_data),
            content_type='application/json'
        )
        assert response1.status_code == status.HTTP_201_CREATED
        id1 = response1.json()['id']

        # Create second patient with same name but different birth date
        patient_data['birthDate'] = '1991-01-01'
        response2 = authenticated_client.post(
            '/fhir/Patient/',
            data=json.dumps(patient_data),
            content_type='application/json'
        )
        assert response2.status_code == status.HTTP_201_CREATED
        id2 = response2.json()['id']

        # Verify they have different IDs
        assert id1 != id2

        # Verify both exist
        assert Patient.objects.count() == 2
