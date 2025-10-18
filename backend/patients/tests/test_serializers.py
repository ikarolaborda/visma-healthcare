"""
Comprehensive tests for FHIR Patient serializers.

Tests serialization, deserialization, and FHIR compliance.
"""
import pytest
from datetime import date
from patients.models import Patient
from patients.serializers import FHIRPatientSerializer, PatientSerializer
from patients.factories import PatientFactory, MinimalPatientFactory, CompletePatientFactory
from rest_framework.exceptions import ValidationError


@pytest.mark.django_db
class TestPatientSerializer:
    """Test standard Django REST Framework Patient serializer."""

    def test_serialize_patient(self):
        """Test serializing a patient to dict."""
        patient = PatientFactory()
        serializer = PatientSerializer(patient)
        data = serializer.data

        assert data['id'] == str(patient.id)
        assert data['given_name'] == patient.given_name
        assert data['family_name'] == patient.family_name
        assert data['gender'] == patient.gender
        assert data['email'] == patient.email

    def test_deserialize_patient(self):
        """Test deserializing dict to create patient."""
        data = {
            'given_name': 'John',
            'family_name': 'Doe',
            'gender': 'male',
            'birth_date': '1990-01-15',
            'email': 'john.doe@example.com'
        }

        serializer = PatientSerializer(data=data)
        assert serializer.is_valid()

        patient = serializer.save()
        assert patient.given_name == 'John'
        assert patient.family_name == 'Doe'


@pytest.mark.django_db
class TestFHIRPatientSerializer:
    """Test FHIR-compliant Patient serializer."""

    def test_serialize_complete_patient_to_fhir(self):
        """Test converting complete patient to FHIR format."""
        patient = CompletePatientFactory(
            given_name='John',
            middle_name='Michael',
            family_name='Doe',
            gender='male',
            birth_date=date(1990, 1, 15),
            email='john.doe@example.com',
            phone='+1-555-123-4567'
        )

        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        # Verify FHIR structure
        assert data['resourceType'] == 'Patient'
        assert data['id'] == str(patient.id)
        assert data['active'] is True
        assert data['gender'] == 'male'
        assert data['birthDate'] == '1990-01-15'

        # Verify HumanName structure
        assert len(data['name']) == 1
        name = data['name'][0]
        assert name['use'] == 'official'
        assert name['family'] == 'Doe'
        assert name['given'] == ['John', 'Michael']

        # Verify Address structure
        assert len(data['address']) == 1
        address = data['address'][0]
        assert address['use'] == 'home'
        assert patient.address_city in str(address)

        # Verify ContactPoint (telecom)
        assert len(data['telecom']) == 2
        email_contact = next(c for c in data['telecom'] if c['system'] == 'email')
        assert email_contact['value'] == 'john.doe@example.com'

    def test_serialize_minimal_patient_to_fhir(self):
        """Test converting minimal patient to FHIR format."""
        patient = MinimalPatientFactory(
            given_name='Jane',
            family_name='Smith',
            gender='female',
            birth_date=date(1985, 6, 20)
        )

        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        assert data['resourceType'] == 'Patient'
        assert data['id'] == str(patient.id)
        assert data['gender'] == 'female'
        assert data['birthDate'] == '1985-06-20'

        # Minimal patient should have name but no address or telecom
        assert 'name' in data
        assert 'address' not in data or len(data.get('address', [])) == 0
        assert 'telecom' not in data or len(data.get('telecom', [])) == 0

    def test_deserialize_fhir_to_patient(self):
        """Test converting FHIR Patient resource to Django model."""
        fhir_data = {
            'resourceType': 'Patient',
            'name': [{
                'use': 'official',
                'family': 'Doe',
                'given': ['John', 'Michael']
            }],
            'gender': 'male',
            'birthDate': '1990-01-15',
            'address': [{
                'use': 'home',
                'line': ['123 Main St'],
                'city': 'New York',
                'state': 'NY',
                'postalCode': '10001',
                'country': 'USA'
            }],
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

        serializer = FHIRPatientSerializer(data=fhir_data)
        assert serializer.is_valid()

        patient = serializer.save()
        assert patient.given_name == 'John'
        assert patient.middle_name == 'Michael'
        assert patient.family_name == 'Doe'
        assert patient.gender == 'male'
        assert patient.birth_date == date(1990, 1, 15)
        assert patient.email == 'john.doe@example.com'
        assert patient.phone == '+1-555-123-4567'
        assert patient.address_line == '123 Main St'
        assert patient.address_city == 'New York'

    def test_deserialize_invalid_resource_type(self):
        """Test rejection of non-Patient FHIR resources."""
        fhir_data = {
            'resourceType': 'Observation',  # Wrong resource type
            'name': [{
                'family': 'Doe',
                'given': ['John']
            }],
            'gender': 'male',
            'birthDate': '1990-01-15'
        }

        serializer = FHIRPatientSerializer(data=fhir_data)
        assert not serializer.is_valid()
        assert 'resourceType' in serializer.errors

    def test_deserialize_missing_required_fields(self):
        """Test validation of required FHIR fields."""
        fhir_data = {
            'resourceType': 'Patient',
            'name': [{
                'family': 'Doe'
                # Missing 'given' name
            }]
            # Missing gender and birthDate
        }

        serializer = FHIRPatientSerializer(data=fhir_data)
        assert not serializer.is_valid()

    def test_roundtrip_conversion(self):
        """Test patient survives serialize-deserialize cycle."""
        # Create original patient
        original = CompletePatientFactory()

        # Serialize to FHIR
        serializer1 = FHIRPatientSerializer(original)
        fhir_data = serializer1.data

        # Deserialize back to patient
        serializer2 = FHIRPatientSerializer(data=fhir_data)
        assert serializer2.is_valid()
        restored = serializer2.save()

        # Compare key fields (excluding auto-generated ID and timestamps)
        assert restored.given_name == original.given_name
        assert restored.family_name == original.family_name
        assert restored.middle_name == original.middle_name
        assert restored.gender == original.gender
        assert restored.birth_date == original.birth_date
        assert restored.email == original.email


@pytest.mark.django_db
class TestFHIRCompliance:
    """Test FHIR R4 compliance of serialization."""

    def test_humanname_structure(self):
        """Test HumanName follows FHIR structure."""
        patient = PatientFactory(
            given_name='John',
            middle_name='Michael',
            family_name='Doe'
        )

        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        name = data['name'][0]
        assert 'use' in name
        assert 'family' in name
        assert 'given' in name
        assert isinstance(name['given'], list)

    def test_address_structure(self):
        """Test Address follows FHIR structure."""
        patient = PatientFactory()
        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        if 'address' in data and data['address']:
            address = data['address'][0]
            assert 'use' in address

            # Optional fields should be present when data exists
            if patient.address_line:
                assert 'line' in address
                assert isinstance(address['line'], list)

    def test_contactpoint_structure(self):
        """Test ContactPoint follows FHIR structure."""
        patient = PatientFactory(
            email='test@example.com',
            phone='+1-555-123-4567'
        )

        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        assert 'telecom' in data
        for contact in data['telecom']:
            assert 'system' in contact
            assert 'value' in contact
            assert contact['system'] in ['email', 'phone', 'fax', 'pager', 'url', 'sms', 'other']

    def test_gender_codes(self):
        """Test gender uses FHIR administrative gender codes."""
        valid_genders = ['male', 'female', 'other', 'unknown']

        for gender in valid_genders:
            patient = PatientFactory(gender=gender)
            serializer = FHIRPatientSerializer(patient)
            data = serializer.data

            assert data['gender'] == gender

    def test_date_format(self):
        """Test dates use FHIR date format (YYYY-MM-DD)."""
        patient = PatientFactory(birth_date=date(1990, 1, 15))
        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        assert data['birthDate'] == '1990-01-15'


@pytest.mark.django_db
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_patient_with_no_middle_name(self):
        """Test patient without middle name serializes correctly."""
        patient = PatientFactory(
            given_name='John',
            middle_name=None,
            family_name='Doe'
        )

        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        name = data['name'][0]
        assert len(name['given']) == 1
        assert name['given'][0] == 'John'

    def test_patient_with_no_email(self):
        """Test patient without email serializes correctly."""
        patient = PatientFactory(email=None, phone='+1-555-123-4567')
        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        # Should have phone but not email
        telecom_systems = [c['system'] for c in data.get('telecom', [])]
        assert 'phone' in telecom_systems
        assert 'email' not in telecom_systems

    def test_patient_with_no_address(self):
        """Test patient without address serializes correctly."""
        patient = MinimalPatientFactory()
        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        # Address should not be present or be empty
        assert 'address' not in data or len(data['address']) == 0

    def test_inactive_patient(self):
        """Test inactive patient has active=false."""
        patient = PatientFactory(active=False)
        serializer = FHIRPatientSerializer(patient)
        data = serializer.data

        assert data['active'] is False

    def test_update_existing_patient(self):
        """Test updating existing patient via serializer."""
        patient = PatientFactory()
        original_id = patient.id

        fhir_data = {
            'resourceType': 'Patient',
            'name': [{
                'use': 'official',
                'family': 'Updated',
                'given': ['NewName']
            }],
            'gender': 'other',
            'birthDate': '1995-05-20'
        }

        serializer = FHIRPatientSerializer(patient, data=fhir_data)
        assert serializer.is_valid()

        updated_patient = serializer.save()
        assert updated_patient.id == original_id  # Same patient
        assert updated_patient.family_name == 'Updated'
        assert updated_patient.given_name == 'NewName'
