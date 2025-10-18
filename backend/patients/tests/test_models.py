"""
Unit tests for Patient model.
"""
import pytest
from django.core.exceptions import ValidationError
from patients.models import Patient
from patients.factories import PatientFactory, CompletePatientFactory
from datetime import date


@pytest.mark.django_db
class TestPatientModel:
    """Test Patient model functionality."""

    def test_create_patient_success(self):
        """Test creating a patient with valid data."""
        patient = Patient.objects.create(
            family_name='Doe',
            given_name='John',
            gender='male',
            birth_date=date(1990, 1, 1),
            email='john.doe@example.com'
        )

        assert patient.id is not None
        assert patient.family_name == 'Doe'
        assert patient.given_name == 'John'
        assert patient.gender == 'male'
        assert patient.active is True

    def test_patient_str_representation(self):
        """Test patient string representation."""
        patient = Patient.objects.create(
            family_name='Smith',
            given_name='Jane',
            gender='female',
            birth_date=date(1985, 5, 15)
        )

        expected = f"Jane Smith ({patient.id})"
        assert str(patient) == expected

    def test_get_full_name_with_middle_name(self):
        """Test get_full_name method with middle name."""
        patient = Patient.objects.create(
            family_name='Johnson',
            given_name='Michael',
            middle_name='Robert',
            gender='male',
            birth_date=date(1992, 3, 20)
        )

        assert patient.get_full_name() == 'Michael Robert Johnson'

    def test_get_full_name_without_middle_name(self):
        """Test get_full_name method without middle name."""
        patient = Patient.objects.create(
            family_name='Williams',
            given_name='Sarah',
            gender='female',
            birth_date=date(1988, 7, 10)
        )

        assert patient.get_full_name() == 'Sarah Williams'

    def test_get_address_complete(self):
        """Test get_address method with complete address."""
        patient = Patient.objects.create(
            family_name='Brown',
            given_name='David',
            gender='male',
            birth_date=date(1995, 11, 5),
            address_line='123 Main St',
            address_city='New York',
            address_state='NY',
            address_postal_code='10001',
            address_country='USA'
        )

        expected = '123 Main St, New York, NY, 10001, USA'
        assert patient.get_address() == expected

    def test_get_address_partial(self):
        """Test get_address method with partial address."""
        patient = Patient.objects.create(
            family_name='Davis',
            given_name='Emily',
            gender='female',
            birth_date=date(1993, 9, 25),
            address_city='Los Angeles',
            address_state='CA'
        )

        expected = 'Los Angeles, CA'
        assert patient.get_address() == expected

    def test_patient_gender_choices(self):
        """Test patient gender field accepts valid choices."""
        valid_genders = ['male', 'female', 'other', 'unknown']

        for gender in valid_genders:
            patient = Patient.objects.create(
                family_name='Test',
                given_name='User',
                gender=gender,
                birth_date=date(1990, 1, 1)
            )
            assert patient.gender == gender

    def test_patient_email_validation(self):
        """Test email field validation."""
        with pytest.raises(ValidationError):
            patient = Patient(
                family_name='Test',
                given_name='User',
                gender='male',
                birth_date=date(1990, 1, 1),
                email='invalid-email'
            )
            patient.full_clean()

    def test_patient_default_active_status(self):
        """Test patient default active status is True."""
        patient = Patient.objects.create(
            family_name='Active',
            given_name='Test',
            gender='male',
            birth_date=date(1990, 1, 1)
        )

        assert patient.active is True

    def test_patient_ordering(self):
        """Test patients are ordered by created_at descending."""
        patient1 = Patient.objects.create(
            family_name='First',
            given_name='Test',
            gender='male',
            birth_date=date(1990, 1, 1)
        )
        patient2 = Patient.objects.create(
            family_name='Second',
            given_name='Test',
            gender='female',
            birth_date=date(1991, 1, 1)
        )

        patients = Patient.objects.all()
        assert patients[0] == patient2  # Most recent first
        assert patients[1] == patient1


@pytest.mark.django_db
class TestPatientModelWithFactories:
    """Additional tests using factories for more realistic data."""

    def test_factory_creates_valid_patient(self):
        """Test that factory creates a valid patient."""
        patient = PatientFactory()
        patient.full_clean()  # Should not raise
        assert patient.id is not None

    def test_multiple_patients_have_unique_data(self):
        """Test that multiple factory patients have unique data."""
        patients = PatientFactory.create_batch(5)

        # All should have unique IDs
        ids = [p.id for p in patients]
        assert len(ids) == len(set(ids))

        # All should have different emails (if present)
        emails = [p.email for p in patients if p.email]
        assert len(emails) == len(set(emails))

    def test_complete_patient_has_all_fields(self):
        """Test CompletePatientFactory populates all fields."""
        patient = CompletePatientFactory()

        assert patient.given_name
        assert patient.middle_name  # Should be present
        assert patient.family_name
        assert patient.email
        assert patient.phone
        assert patient.address_line
        assert patient.address_city
        assert patient.address_state
