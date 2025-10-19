"""
Tests for Practitioner API endpoints.

Tests FHIR-compliant REST API endpoints with authentication.
"""
import pytest
from practitioners.models import Practitioner


@pytest.mark.django_db
class TestPractitionerListEndpoint:
    """Test cases for GET /fhir/Practitioner/"""

    def test_list_practitioners_empty(self, authenticated_client):
        """Test listing practitioners when database is empty."""
        response = authenticated_client.get('/fhir/Practitioner/')

        assert response.status_code == 200
        assert response.data['resourceType'] == 'Bundle'
        assert response.data['type'] == 'searchset'
        assert response.data['total'] == 0
        assert response.data['entry'] == []

    def test_list_practitioners_with_data(self, authenticated_client, sample_practitioner):
        """Test listing practitioners with existing data."""
        response = authenticated_client.get('/fhir/Practitioner/')

        assert response.status_code == 200
        assert response.data['resourceType'] == 'Bundle'
        assert response.data['total'] == 1
        assert len(response.data['entry']) == 1

        practitioner_resource = response.data['entry'][0]['resource']
        assert practitioner_resource['resourceType'] == 'Practitioner'
        assert practitioner_resource['id'] == str(sample_practitioner.id)
        assert practitioner_resource['name'][0]['family'] == 'Smith'
        assert practitioner_resource['name'][0]['given'] == ['John']

    def test_list_practitioners_requires_authentication(self, api_client):
        """Test that listing practitioners requires authentication."""
        response = api_client.get('/fhir/Practitioner/')

        assert response.status_code == 401

    def test_list_multiple_practitioners(self, authenticated_client):
        """Test listing multiple practitioners."""
        # Create multiple practitioners
        Practitioner.objects.create(
            given_name='John',
            family_name='Doe',
            gender='male',
            specialization='Cardiology',
            qualification='MD',
            email='john@hospital.com',
            phone='+1-555-1001'
        )

        Practitioner.objects.create(
            given_name='Jane',
            family_name='Smith',
            gender='female',
            specialization='Neurology',
            qualification='MD, PhD',
            email='jane@hospital.com',
            phone='+1-555-1002'
        )

        response = authenticated_client.get('/fhir/Practitioner/')

        assert response.status_code == 200
        assert response.data['total'] == 2
        assert len(response.data['entry']) == 2


@pytest.mark.django_db
class TestPractitionerCreateEndpoint:
    """Test cases for POST /fhir/Practitioner/"""

    def test_create_practitioner_success(self, authenticated_client, fhir_practitioner_data):
        """Test creating a new practitioner with valid FHIR data."""
        response = authenticated_client.post(
            '/fhir/Practitioner/',
            data=fhir_practitioner_data,
            format='json'
        )

        assert response.status_code == 201, f"Error: {response.data}"
        assert response.data['resourceType'] == 'Practitioner'
        assert response.data['name'][0]['family'] == 'Johnson'
        assert response.data['name'][0]['given'] == ['Emily']
        assert response.data['specialization'] == 'Cardiology'

        # Verify in database
        assert Practitioner.objects.filter(
            family_name='Johnson',
            given_name='Emily'
        ).exists()

    def test_create_practitioner_requires_authentication(self, api_client, fhir_practitioner_data):
        """Test that creating requires authentication."""
        response = api_client.post(
            '/fhir/Practitioner/',
            data=fhir_practitioner_data,
            format='json'
        )

        assert response.status_code == 401

    def test_create_practitioner_invalid_resource_type(self, authenticated_client):
        """Test creating with invalid resource type."""
        invalid_data = {
            'resourceType': 'Patient',  # Wrong resource type
            'name': [{'family': 'Test', 'given': ['Test']}]
        }

        response = authenticated_client.post(
            '/fhir/Practitioner/',
            data=invalid_data,
            format='json'
        )

        assert response.status_code == 400
        assert 'resourceType' in response.data

    def test_create_practitioner_missing_required_fields(self, authenticated_client):
        """Test creating without required fields."""
        incomplete_data = {
            'resourceType': 'Practitioner',
            'name': [{'family': 'Test', 'given': ['Test']}]
            # Missing email, phone, specialization, qualification
        }

        response = authenticated_client.post(
            '/fhir/Practitioner/',
            data=incomplete_data,
            format='json'
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestPractitionerRetrieveEndpoint:
    """Test cases for GET /fhir/Practitioner/{id}/"""

    def test_retrieve_practitioner_success(self, authenticated_client, sample_practitioner):
        """Test retrieving a specific practitioner."""
        response = authenticated_client.get(f'/fhir/Practitioner/{sample_practitioner.id}/')

        assert response.status_code == 200
        assert response.data['resourceType'] == 'Practitioner'
        assert response.data['id'] == str(sample_practitioner.id)
        assert response.data['name'][0]['family'] == 'Smith'
        assert response.data['specialization'] == 'General Practice'

    def test_retrieve_practitioner_not_found(self, authenticated_client):
        """Test retrieving non-existent practitioner."""
        from uuid import uuid4
        fake_id = uuid4()

        response = authenticated_client.get(f'/fhir/Practitioner/{fake_id}/')

        assert response.status_code == 404

    def test_retrieve_practitioner_requires_authentication(self, api_client, sample_practitioner):
        """Test that retrieving requires authentication."""
        response = api_client.get(f'/fhir/Practitioner/{sample_practitioner.id}/')

        assert response.status_code == 401


@pytest.mark.django_db
class TestPractitionerUpdateEndpoint:
    """Test cases for PUT /fhir/Practitioner/{id}/"""

    def test_update_practitioner_success(self, authenticated_client, sample_practitioner, fhir_practitioner_data):
        """Test updating an existing practitioner."""
        # Modify the FHIR data
        fhir_practitioner_data['name'][0]['family'] = 'UpdatedName'
        fhir_practitioner_data['specialization'] = 'Updated Specialization'

        response = authenticated_client.put(
            f'/fhir/Practitioner/{sample_practitioner.id}/',
            data=fhir_practitioner_data,
            format='json'
        )

        assert response.status_code == 200
        assert response.data['name'][0]['family'] == 'UpdatedName'
        assert response.data['specialization'] == 'Updated Specialization'

        # Verify in database
        sample_practitioner.refresh_from_db()
        assert sample_practitioner.family_name == 'UpdatedName'
        assert sample_practitioner.specialization == 'Updated Specialization'

    def test_update_practitioner_not_found(self, authenticated_client, fhir_practitioner_data):
        """Test updating non-existent practitioner."""
        from uuid import uuid4
        fake_id = uuid4()

        response = authenticated_client.put(
            f'/fhir/Practitioner/{fake_id}/',
            data=fhir_practitioner_data,
            format='json'
        )

        assert response.status_code == 404

    def test_update_practitioner_requires_authentication(self, api_client, sample_practitioner, fhir_practitioner_data):
        """Test that updating requires authentication."""
        response = api_client.put(
            f'/fhir/Practitioner/{sample_practitioner.id}/',
            data=fhir_practitioner_data,
            format='json'
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestPractitionerDeleteEndpoint:
    """Test cases for DELETE /fhir/Practitioner/{id}/"""

    def test_delete_practitioner_success(self, authenticated_client, sample_practitioner):
        """Test deleting a practitioner."""
        practitioner_id = sample_practitioner.id

        response = authenticated_client.delete(f'/fhir/Practitioner/{practitioner_id}/')

        assert response.status_code == 204

        # Verify deleted from database
        assert not Practitioner.objects.filter(id=practitioner_id).exists()

    def test_delete_practitioner_not_found(self, authenticated_client):
        """Test deleting non-existent practitioner."""
        from uuid import uuid4
        fake_id = uuid4()

        response = authenticated_client.delete(f'/fhir/Practitioner/{fake_id}/')

        assert response.status_code == 404

    def test_delete_practitioner_requires_authentication(self, api_client, sample_practitioner):
        """Test that deleting requires authentication."""
        response = api_client.delete(f'/fhir/Practitioner/{sample_practitioner.id}/')

        assert response.status_code == 401


@pytest.mark.django_db
class TestPractitionerSearchEndpoint:
    """Test cases for GET /fhir/Practitioner/search/"""

    def test_search_by_name(self, authenticated_client):
        """Test searching practitioners by name."""
        Practitioner.objects.create(
            given_name='Sarah',
            family_name='Johnson',
            gender='female',
            specialization='Cardiology',
            qualification='MD',
            email='sarah@hospital.com',
            phone='+1-555-2001'
        )

        Practitioner.objects.create(
            given_name='Michael',
            family_name='Smith',
            gender='male',
            specialization='Neurology',
            qualification='MD',
            email='michael@hospital.com',
            phone='+1-555-2002'
        )

        response = authenticated_client.get('/fhir/Practitioner/search/?query=Sarah')

        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['entry'][0]['resource']['name'][0]['given'] == ['Sarah']

    def test_search_by_specialization(self, authenticated_client):
        """Test searching by specialization."""
        Practitioner.objects.create(
            given_name='John',
            family_name='Doe',
            gender='male',
            specialization='Cardiology',
            qualification='MD',
            email='john@hospital.com',
            phone='+1-555-3001'
        )

        Practitioner.objects.create(
            given_name='Jane',
            family_name='Smith',
            gender='female',
            specialization='Neurology',
            qualification='MD',
            email='jane@hospital.com',
            phone='+1-555-3002'
        )

        response = authenticated_client.get('/fhir/Practitioner/search/?query=Cardiology')

        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['entry'][0]['resource']['specialization'] == 'Cardiology'

    def test_search_no_query_parameter(self, authenticated_client):
        """Test search without query parameter."""
        response = authenticated_client.get('/fhir/Practitioner/search/')

        assert response.status_code == 400
        assert 'error' in response.data

    def test_search_no_results(self, authenticated_client):
        """Test search with no matching results."""
        response = authenticated_client.get('/fhir/Practitioner/search/?query=NonExistent')

        assert response.status_code == 200
        assert response.data['total'] == 0
        assert response.data['entry'] == []

    def test_search_only_active_practitioners(self, authenticated_client):
        """Test that search only returns active practitioners."""
        # Create active practitioner
        Practitioner.objects.create(
            given_name='Active',
            family_name='Doctor',
            gender='male',
            specialization='General Practice',
            qualification='MD',
            email='active@hospital.com',
            phone='+1-555-4001',
            active=True
        )

        # Create inactive practitioner
        Practitioner.objects.create(
            given_name='Inactive',
            family_name='Doctor',
            gender='female',
            specialization='General Practice',
            qualification='MD',
            email='inactive@hospital.com',
            phone='+1-555-4002',
            active=False
        )

        response = authenticated_client.get('/fhir/Practitioner/search/?query=Doctor')

        assert response.status_code == 200
        assert response.data['total'] == 1
        assert response.data['entry'][0]['resource']['name'][0]['given'] == ['Active']
