"""
Enhanced API tests using factories for realistic test scenarios.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from patients.factories import (
    PatientFactory,
    PediatricPatientFactory,
    GeriatricPatientFactory,
    create_diverse_patient_cohort,
)


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


@pytest.mark.django_db
class TestPatientAPIWithRealisticData:
    """Test API with realistic factory-generated data."""

    def test_list_diverse_patient_population(self, authenticated_client):
        """Test listing a diverse patient population."""
        # Create diverse cohort
        create_diverse_patient_cohort(count=30)

        response = authenticated_client.get('/fhir/Patient/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['total'] == 30
        assert len(data['entry']) == 30

        # Verify we have diverse ages
        birth_dates = [entry['resource']['birthDate'] for entry in data['entry']]
        assert len(set(birth_dates)) > 20  # Should have varied birth dates

    def test_retrieve_pediatric_patient(self, authenticated_client):
        """Test retrieving a pediatric patient."""
        patient = PediatricPatientFactory()

        response = authenticated_client.get(f'/fhir/Patient/{patient.id}/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['resourceType'] == 'Patient'

        # Calculate age - should be under 18
        from datetime import date
        birth_date = date.fromisoformat(data['birthDate'])
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        assert age < 18

    def test_retrieve_geriatric_patient(self, authenticated_client):
        """Test retrieving a geriatric patient."""
        patient = GeriatricPatientFactory()

        response = authenticated_client.get(f'/fhir/Patient/{patient.id}/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Calculate age - should be 65 or older
        from datetime import date
        birth_date = date.fromisoformat(data['birthDate'])
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        assert age >= 65

    def test_delete_multiple_patients(self, authenticated_client):
        """Test deleting multiple patients in sequence."""
        patients = PatientFactory.create_batch(5)

        for patient in patients:
            response = authenticated_client.delete(f'/fhir/Patient/{patient.id}/')
            assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify all are deleted
        response = authenticated_client.get('/fhir/Patient/')
        data = response.json()
        assert data['total'] == 0

    def test_api_handles_realistic_names(self, authenticated_client):
        """Test API properly handles realistic names with various formats."""
        patients = PatientFactory.create_batch(10)

        for patient in patients:
            response = authenticated_client.get(f'/fhir/Patient/{patient.id}/')
            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            name = data['name'][0]

            # Verify name structure
            assert 'family' in name
            assert 'given' in name
            assert isinstance(name['given'], list)
            assert len(name['given']) >= 1


@pytest.mark.django_db
class TestPerformanceWithFactories:
    """Test API performance with larger datasets."""

    def test_list_large_patient_set(self, authenticated_client):
        """Test listing performance with 100 patients."""
        create_diverse_patient_cohort(count=100)

        response = authenticated_client.get('/fhir/Patient/')
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['total'] == 100

    def test_sequential_creates(self, authenticated_client):
        """Test creating multiple patients sequentially."""
        import json

        for i in range(5):
            patient = PatientFactory.build()  # Build without saving

            patient_data = {
                'resourceType': 'Patient',
                'name': [{
                    'family': patient.family_name,
                    'given': [patient.given_name]
                }],
                'gender': patient.gender,
                'birthDate': patient.birth_date.isoformat()
            }

            response = authenticated_client.post(
                '/fhir/Patient/',
                data=json.dumps(patient_data),
                content_type='application/json'
            )

            assert response.status_code == status.HTTP_201_CREATED

        # Verify all were created
        response = authenticated_client.get('/fhir/Patient/')
        data = response.json()
        assert data['total'] == 5
