"""
Tests for Practitioner models.

Tests model creation, validation, and helper methods.
"""
import pytest
from datetime import date
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from practitioners.models import Practitioner


@pytest.mark.django_db
class TestPractitionerModel:
    """Test cases for Practitioner model."""

    def test_create_practitioner_with_all_fields(self, sample_practitioner_data):
        """Test creating a practitioner with all fields."""
        practitioner = Practitioner.objects.create(**sample_practitioner_data)

        assert practitioner.id is not None
        assert practitioner.prefix == 'Dr.'
        assert practitioner.given_name == 'John'
        assert practitioner.family_name == 'Smith'
        assert practitioner.gender == 'male'
        assert practitioner.birth_date == date(1980, 1, 15)
        assert practitioner.npi == '1234567890'
        assert practitioner.license_number == 'MD-98765'
        assert practitioner.specialization == 'General Practice'
        assert practitioner.qualification == 'MD'
        assert practitioner.years_of_experience == 15
        assert practitioner.email == 'dr.smith@hospital.com'
        assert practitioner.phone == '+1-555-0100'
        assert practitioner.active is True
        assert practitioner.created_at is not None
        assert practitioner.updated_at is not None

    def test_create_practitioner_minimal_fields(self):
        """Test creating practitioner with minimal required fields."""
        practitioner = Practitioner.objects.create(
            given_name='Jane',
            family_name='Doe',
            gender='female',
            specialization='Pediatrics',
            qualification='MD',
            email='dr.doe@hospital.com',
            phone='+1-555-0300'
        )

        assert practitioner.id is not None
        assert practitioner.given_name == 'Jane'
        assert practitioner.family_name == 'Doe'
        assert practitioner.active is True  # Default value

    def test_npi_uniqueness(self, sample_practitioner_data):
        """Test that NPI must be unique."""
        Practitioner.objects.create(**sample_practitioner_data)

        # Try to create another practitioner with same NPI
        duplicate_data = sample_practitioner_data.copy()
        duplicate_data['email'] = 'different@hospital.com'

        with pytest.raises(IntegrityError):
            Practitioner.objects.create(**duplicate_data)

    def test_str_representation(self, sample_practitioner):
        """Test string representation of practitioner."""
        expected = "Dr. John Smith - General Practice"
        assert str(sample_practitioner) == expected

    def test_str_representation_without_prefix(self):
        """Test string representation without prefix."""
        practitioner = Practitioner.objects.create(
            given_name='Jane',
            family_name='Doe',
            gender='female',
            specialization='Neurology',
            qualification='MD',
            email='dr.doe@hospital.com',
            phone='+1-555-0400'
        )

        expected = "Jane Doe - Neurology"
        assert str(practitioner) == expected

    def test_get_full_name_with_prefix(self, sample_practitioner):
        """Test get_full_name method with prefix."""
        expected = "Dr. John Smith"
        assert sample_practitioner.get_full_name() == expected

    def test_get_full_name_with_middle_name(self):
        """Test get_full_name with middle name."""
        practitioner = Practitioner.objects.create(
            prefix='Dr.',
            given_name='John',
            middle_name='Michael',
            family_name='Smith',
            gender='male',
            specialization='Surgery',
            qualification='MD',
            email='dr.jmsmith@hospital.com',
            phone='+1-555-0500'
        )

        expected = "Dr. John Michael Smith"
        assert practitioner.get_full_name() == expected

    def test_get_address(self, sample_practitioner):
        """Test get_address method."""
        expected = "456 Medical Center, Boston, MA, 02101, USA"
        assert sample_practitioner.get_address() == expected

    def test_get_address_partial(self):
        """Test get_address with partial address."""
        practitioner = Practitioner.objects.create(
            given_name='Jane',
            family_name='Doe',
            gender='female',
            specialization='Pediatrics',
            qualification='MD',
            email='dr.doe@hospital.com',
            phone='+1-555-0600',
            address_city='New York',
            address_state='NY'
        )

        expected = "New York, NY"
        assert practitioner.get_address() == expected

    def test_get_credentials_with_prefix_and_qualification(self, sample_practitioner):
        """Test get_credentials method."""
        expected = "Dr. John Smith, MD"
        assert sample_practitioner.get_credentials() == expected

    def test_get_credentials_without_prefix(self):
        """Test get_credentials without prefix."""
        practitioner = Practitioner.objects.create(
            given_name='Jane',
            family_name='Doe',
            gender='female',
            specialization='Pediatrics',
            qualification='MD, PhD',
            email='dr.doe@hospital.com',
            phone='+1-555-0700'
        )

        expected = "Jane Doe, MD, PhD"
        assert practitioner.get_credentials() == expected

    def test_active_default_true(self):
        """Test that active field defaults to True."""
        practitioner = Practitioner.objects.create(
            given_name='Test',
            family_name='Doctor',
            gender='other',
            specialization='General Practice',
            qualification='MD',
            email='test@hospital.com',
            phone='+1-555-0800'
        )

        assert practitioner.active is True

    def test_ordering_by_created_at(self):
        """Test that practitioners are ordered by created_at descending."""
        p1 = Practitioner.objects.create(
            given_name='First',
            family_name='Doctor',
            gender='male',
            specialization='General Practice',
            qualification='MD',
            email='first@hospital.com',
            phone='+1-555-0901'
        )

        p2 = Practitioner.objects.create(
            given_name='Second',
            family_name='Doctor',
            gender='female',
            specialization='Cardiology',
            qualification='MD',
            email='second@hospital.com',
            phone='+1-555-0902'
        )

        practitioners = list(Practitioner.objects.all())
        assert practitioners[0].id == p2.id  # Most recent first
        assert practitioners[1].id == p1.id
