"""
Tests for Practitioner serializers.

Tests both standard and FHIR serialization.
"""
import pytest
from datetime import date
from practitioners.models import Practitioner
from practitioners.serializers import PractitionerSerializer, FHIRPractitionerSerializer


@pytest.mark.django_db
class TestPractitionerSerializer:
    """Test cases for PractitionerSerializer."""

    def test_serialize_practitioner(self, sample_practitioner):
        """Test serializing a practitioner instance."""
        serializer = PractitionerSerializer(sample_practitioner)
        data = serializer.data

        assert data['id'] == str(sample_practitioner.id)
        assert data['given_name'] == 'John'
        assert data['family_name'] == 'Smith'
        assert data['full_name'] == 'Dr. John Smith'
        assert data['credentials'] == 'Dr. John Smith, MD'
        assert data['specialization'] == 'General Practice'

    def test_deserialize_valid_data(self):
        """Test deserializing valid practitioner data."""
        data = {
            'prefix': 'Dr.',
            'given_name': 'Jane',
            'family_name': 'Doe',
            'gender': 'female',
            'specialization': 'Pediatrics',
            'qualification': 'MD',
            'email': 'jane.doe@hospital.com',
            'phone': '+1-555-9999'
        }

        serializer = PractitionerSerializer(data=data)
        assert serializer.is_valid()

        practitioner = serializer.save()
        assert practitioner.given_name == 'Jane'
        assert practitioner.family_name == 'Doe'
        assert practitioner.specialization == 'Pediatrics'

    def test_read_only_fields(self, sample_practitioner):
        """Test that read-only fields cannot be modified."""
        serializer = PractitionerSerializer(sample_practitioner)
        data = serializer.data

        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'full_name' in data
        assert 'credentials' in data


@pytest.mark.django_db
class TestFHIRPractitionerSerializer:
    """Test cases for FHIRPractitionerSerializer."""

    def test_to_representation(self, sample_practitioner):
        """Test converting practitioner to FHIR representation."""
        serializer = FHIRPractitionerSerializer(sample_practitioner)
        data = serializer.data

        assert data['resourceType'] == 'Practitioner'
        assert data['id'] == str(sample_practitioner.id)
        assert data['active'] is True
        assert data['name'][0]['family'] == 'Smith'
        assert data['name'][0]['given'] == ['John']
        assert data['name'][0]['prefix'] == ['Dr.']
        assert data['gender'] == 'male'
        assert data['specialization'] == 'General Practice'
        assert data['years_of_experience'] == 15

    def test_to_representation_identifiers(self, sample_practitioner):
        """Test FHIR identifier conversion."""
        serializer = FHIRPractitionerSerializer(sample_practitioner)
        data = serializer.data

        assert 'identifier' in data
        assert len(data['identifier']) == 2

        # Check NPI identifier
        npi_id = next((i for i in data['identifier'] if i['system'] == 'http://hl7.org/fhir/sid/us-npi'), None)
        assert npi_id is not None
        assert npi_id['value'] == '1234567890'

        # Check license identifier
        license_id = next((i for i in data['identifier'] if 'license' in i['system']), None)
        assert license_id is not None
        assert license_id['value'] == 'MD-98765'

    def test_to_representation_telecom(self, sample_practitioner):
        """Test FHIR telecom (contact points) conversion."""
        serializer = FHIRPractitionerSerializer(sample_practitioner)
        data = serializer.data

        assert 'telecom' in data
        assert len(data['telecom']) == 2

        # Check email
        email_contact = next((t for t in data['telecom'] if t['system'] == 'email'), None)
        assert email_contact is not None
        assert email_contact['value'] == 'dr.smith@hospital.com'

        # Check phone
        phone_contact = next((t for t in data['telecom'] if t['system'] == 'phone'), None)
        assert phone_contact is not None
        assert phone_contact['value'] == '+1-555-0100'

    def test_to_representation_address(self, sample_practitioner):
        """Test FHIR address conversion."""
        serializer = FHIRPractitionerSerializer(sample_practitioner)
        data = serializer.data

        assert 'address' in data
        assert len(data['address']) == 1

        address = data['address'][0]
        assert address['line'] == ['456 Medical Center']
        assert address['city'] == 'Boston'
        assert address['state'] == 'MA'
        assert address['postalCode'] == '02101'
        assert address['country'] == 'USA'

    def test_to_representation_without_optional_fields(self):
        """Test FHIR representation with minimal fields."""
        practitioner = Practitioner.objects.create(
            given_name='Jane',
            family_name='Doe',
            gender='female',
            specialization='Cardiology',
            qualification='MD',
            email='jane@hospital.com',
            phone='+1-555-7777'
        )

        serializer = FHIRPractitionerSerializer(practitioner)
        data = serializer.data

        assert data['resourceType'] == 'Practitioner'
        assert data['name'][0]['family'] == 'Doe'
        assert data['name'][0]['given'] == ['Jane']
        assert 'prefix' not in data['name'][0]
        assert 'identifier' not in data or len(data['identifier']) == 0

    def test_to_internal_value_valid_fhir_data(self, fhir_practitioner_data):
        """Test converting valid FHIR data to internal representation."""
        serializer = FHIRPractitionerSerializer(data=fhir_practitioner_data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert validated_data['family_name'] == 'Johnson'
        assert validated_data['given_name'] == 'Emily'
        assert validated_data['gender'] == 'female'
        assert validated_data['specialization'] == 'Cardiology'
        assert validated_data['qualification'] == 'MD, PhD'
        assert validated_data['email'] == 'dr.johnson@hospital.com'
        assert validated_data['phone'] == '+1-555-0200'

    def test_to_internal_value_creates_practitioner(self, fhir_practitioner_data):
        """Test creating practitioner from FHIR data."""
        serializer = FHIRPractitionerSerializer(data=fhir_practitioner_data)
        assert serializer.is_valid()

        practitioner = serializer.save()
        assert practitioner.id is not None
        assert practitioner.given_name == 'Emily'
        assert practitioner.family_name == 'Johnson'
        assert practitioner.specialization == 'Cardiology'

    def test_to_internal_value_invalid_resource_type(self):
        """Test validation error for invalid resource type."""
        invalid_data = {
            'resourceType': 'Patient',
            'name': [{'family': 'Smith', 'given': ['John']}]
        }

        serializer = FHIRPractitionerSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'resourceType' in serializer.errors

    def test_to_internal_value_missing_name(self):
        """Test validation error when name is missing."""
        invalid_data = {
            'resourceType': 'Practitioner',
            'active': True
        }

        serializer = FHIRPractitionerSerializer(data=invalid_data)
        assert not serializer.is_valid()

    def test_to_internal_value_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        incomplete_data = {
            'resourceType': 'Practitioner',
            'name': [{'family': 'Smith', 'given': ['John']}]
        }

        serializer = FHIRPractitionerSerializer(data=incomplete_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors or 'specialization' in serializer.errors

    def test_update_practitioner(self, sample_practitioner, fhir_practitioner_data):
        """Test updating a practitioner from FHIR data."""
        fhir_practitioner_data['name'][0]['family'] = 'UpdatedLastName'
        fhir_practitioner_data['specialization'] = 'Neurology'

        serializer = FHIRPractitionerSerializer(sample_practitioner, data=fhir_practitioner_data)
        assert serializer.is_valid()

        updated_practitioner = serializer.save()
        assert updated_practitioner.id == sample_practitioner.id
        assert updated_practitioner.family_name == 'UpdatedLastName'
        assert updated_practitioner.specialization == 'Neurology'

    def test_birth_date_conversion(self, fhir_practitioner_data):
        """Test birth date string to date conversion."""
        serializer = FHIRPractitionerSerializer(data=fhir_practitioner_data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert 'birth_date' in validated_data
        assert isinstance(validated_data['birth_date'], date)
        assert validated_data['birth_date'] == date(1985, 3, 20)

    def test_npi_extraction(self, fhir_practitioner_data):
        """Test NPI extraction from FHIR identifiers."""
        serializer = FHIRPractitionerSerializer(data=fhir_practitioner_data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert validated_data['npi'] == '9876543210'

    def test_address_extraction(self, fhir_practitioner_data):
        """Test address extraction from FHIR data."""
        serializer = FHIRPractitionerSerializer(data=fhir_practitioner_data)
        assert serializer.is_valid()

        validated_data = serializer.validated_data
        assert validated_data['address_line'] == '789 Healthcare Blvd'
        assert validated_data['address_city'] == 'Chicago'
        assert validated_data['address_state'] == 'IL'
        assert validated_data['address_postal_code'] == '60601'
        assert validated_data['address_country'] == 'USA'
