"""
Tests for Practitioner services.

Tests service layer business logic and validation.
"""
import pytest
from django.core.exceptions import ValidationError
from practitioners.models import Practitioner
from practitioners.services import PractitionerService


@pytest.mark.django_db
class TestPractitionerService:
    """Test cases for PractitionerService."""

    def test_create_practitioner_success(self):
        """Test creating a practitioner through service."""
        service = PractitionerService()
        practitioner = service.create({
            'given_name': 'John',
            'family_name': 'Doe',
            'gender': 'male',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'john.doe@hospital.com',
            'phone': '+1-555-1234'
        })

        assert practitioner.id is not None
        assert practitioner.given_name == 'John'
        assert practitioner.family_name == 'Doe'

    def test_create_practitioner_missing_given_name(self):
        """Test validation error when given name is missing."""
        service = PractitionerService()

        with pytest.raises(ValidationError, match='Given name is required'):
            service.create({
                'family_name': 'Doe',
                'gender': 'male',
                'specialization': 'Cardiology',
                'qualification': 'MD',
                'email': 'test@hospital.com',
                'phone': '+1-555-1234'
            })

    def test_create_practitioner_missing_family_name(self):
        """Test validation error when family name is missing."""
        service = PractitionerService()

        with pytest.raises(ValidationError, match='Family name is required'):
            service.create({
                'given_name': 'John',
                'gender': 'male',
                'specialization': 'Cardiology',
                'qualification': 'MD',
                'email': 'test@hospital.com',
                'phone': '+1-555-1234'
            })

    def test_create_practitioner_missing_email(self):
        """Test validation error when email is missing."""
        service = PractitionerService()

        with pytest.raises(ValidationError, match='Email is required'):
            service.create({
                'given_name': 'John',
                'family_name': 'Doe',
                'gender': 'male',
                'specialization': 'Cardiology',
                'qualification': 'MD',
                'phone': '+1-555-1234'
            })

    def test_create_practitioner_missing_specialization(self):
        """Test validation error when specialization is missing."""
        service = PractitionerService()

        with pytest.raises(ValidationError, match='Specialization is required'):
            service.create({
                'given_name': 'John',
                'family_name': 'Doe',
                'gender': 'male',
                'qualification': 'MD',
                'email': 'test@hospital.com',
                'phone': '+1-555-1234'
            })

    def test_create_practitioner_duplicate_npi(self):
        """Test validation error for duplicate NPI."""
        service = PractitionerService()

        # Create first practitioner
        service.create({
            'given_name': 'First',
            'family_name': 'Doctor',
            'gender': 'male',
            'npi': '1234567890',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'first@hospital.com',
            'phone': '+1-555-1001'
        })

        # Try to create second with same NPI
        with pytest.raises(ValidationError, match='NPI 1234567890 already exists'):
            service.create({
                'given_name': 'Second',
                'family_name': 'Doctor',
                'gender': 'female',
                'npi': '1234567890',
                'specialization': 'Neurology',
                'qualification': 'MD',
                'email': 'second@hospital.com',
                'phone': '+1-555-1002'
            })

    def test_create_practitioner_duplicate_email(self):
        """Test validation error for duplicate email."""
        service = PractitionerService()

        # Create first practitioner
        service.create({
            'given_name': 'First',
            'family_name': 'Doctor',
            'gender': 'male',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'duplicate@hospital.com',
            'phone': '+1-555-2001'
        })

        # Try to create second with same email
        with pytest.raises(ValidationError, match='email duplicate@hospital.com already exists'):
            service.create({
                'given_name': 'Second',
                'family_name': 'Doctor',
                'gender': 'female',
                'specialization': 'Neurology',
                'qualification': 'MD',
                'email': 'duplicate@hospital.com',
                'phone': '+1-555-2002'
            })

    def test_update_practitioner_success(self, sample_practitioner):
        """Test updating a practitioner through service."""
        service = PractitionerService()
        updated = service.update(
            sample_practitioner.id,
            {
                'specialization': 'Updated Specialization',
                'years_of_experience': 20
            }
        )

        assert updated.specialization == 'Updated Specialization'
        assert updated.years_of_experience == 20

    def test_update_practitioner_duplicate_npi(self):
        """Test validation error when updating to duplicate NPI."""
        service = PractitionerService()

        # Create two practitioners
        p1 = service.create({
            'given_name': 'First',
            'family_name': 'Doctor',
            'gender': 'male',
            'npi': '1111111111',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'first@hospital.com',
            'phone': '+1-555-3001'
        })

        service.create({
            'given_name': 'Second',
            'family_name': 'Doctor',
            'gender': 'female',
            'npi': '2222222222',
            'specialization': 'Neurology',
            'qualification': 'MD',
            'email': 'second@hospital.com',
            'phone': '+1-555-3002'
        })

        # Try to update first to have second's NPI
        with pytest.raises(ValidationError, match='NPI 2222222222 already exists'):
            service.update(p1.id, {'npi': '2222222222'})

    def test_update_practitioner_duplicate_email(self):
        """Test validation error when updating to duplicate email."""
        service = PractitionerService()

        # Create two practitioners
        p1 = service.create({
            'given_name': 'First',
            'family_name': 'Doctor',
            'gender': 'male',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'first@hospital.com',
            'phone': '+1-555-4001'
        })

        service.create({
            'given_name': 'Second',
            'family_name': 'Doctor',
            'gender': 'female',
            'specialization': 'Neurology',
            'qualification': 'MD',
            'email': 'second@hospital.com',
            'phone': '+1-555-4002'
        })

        # Try to update first to have second's email
        with pytest.raises(ValidationError, match='email second@hospital.com already exists'):
            service.update(p1.id, {'email': 'second@hospital.com'})

    def test_find_by_specialization(self):
        """Test finding practitioners by specialization."""
        service = PractitionerService()

        service.create({
            'given_name': 'Cardiologist',
            'family_name': 'One',
            'gender': 'male',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'cardio1@hospital.com',
            'phone': '+1-555-5001'
        })

        service.create({
            'given_name': 'Cardiologist',
            'family_name': 'Two',
            'gender': 'female',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'cardio2@hospital.com',
            'phone': '+1-555-5002'
        })

        cardiologists = service.find_by_specialization('Cardiology')
        assert len(cardiologists) == 2

    def test_search_practitioners(self):
        """Test searching practitioners by query."""
        service = PractitionerService()

        service.create({
            'given_name': 'Sarah',
            'family_name': 'Johnson',
            'gender': 'female',
            'specialization': 'Pediatrics',
            'qualification': 'MD',
            'email': 'sarah@hospital.com',
            'phone': '+1-555-6001'
        })

        service.create({
            'given_name': 'Michael',
            'family_name': 'Williams',
            'gender': 'male',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'michael@hospital.com',
            'phone': '+1-555-6002'
        })

        # Search by name
        results = service.search_practitioners('Sarah')
        assert len(results) == 1
        assert results[0].given_name == 'Sarah'

        # Search by specialization
        results = service.search_practitioners('Cardiology')
        assert len(results) == 1
        assert results[0].specialization == 'Cardiology'

    def test_deactivate_practitioner(self, sample_practitioner):
        """Test deactivating a practitioner."""
        service = PractitionerService()
        assert sample_practitioner.active is True

        result = service.deactivate_practitioner(sample_practitioner.id)
        assert result is True

        # Verify in database
        sample_practitioner.refresh_from_db()
        assert sample_practitioner.active is False

    def test_get_by_id(self, sample_practitioner):
        """Test getting practitioner by ID."""
        service = PractitionerService()
        found = service.get_by_id(sample_practitioner.id)

        assert found is not None
        assert found.id == sample_practitioner.id

    def test_get_by_id_not_found(self):
        """Test getting non-existent practitioner."""
        from uuid import uuid4
        service = PractitionerService()
        found = service.get_by_id(uuid4())

        assert found is None

    def test_delete_practitioner(self, sample_practitioner):
        """Test deleting a practitioner."""
        practitioner_id = sample_practitioner.id
        service = PractitionerService()

        result = service.delete(practitioner_id)
        assert result is True

        # Verify deletion
        assert not Practitioner.objects.filter(id=practitioner_id).exists()

    def test_get_all_practitioners(self):
        """Test getting all practitioners."""
        service = PractitionerService()

        service.create({
            'given_name': 'First',
            'family_name': 'Doctor',
            'gender': 'male',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'email': 'first@hospital.com',
            'phone': '+1-555-7001'
        })

        service.create({
            'given_name': 'Second',
            'family_name': 'Doctor',
            'gender': 'female',
            'specialization': 'Neurology',
            'qualification': 'MD',
            'email': 'second@hospital.com',
            'phone': '+1-555-7002'
        })

        all_practitioners = list(service.get_all())
        assert len(all_practitioners) == 2

    def test_validate_update_with_existing_npi_same_instance(self, sample_practitioner):
        """Test that updating with the same NPI doesn't raise error."""
        service = PractitionerService()

        # Update with same NPI should not raise error
        updated = service.update(
            sample_practitioner.id,
            {
                'npi': sample_practitioner.npi,
                'specialization': 'Updated Specialization'
            }
        )

        assert updated.npi == sample_practitioner.npi
        assert updated.specialization == 'Updated Specialization'

    def test_validate_update_with_existing_email_same_instance(self, sample_practitioner):
        """Test that updating with the same email doesn't raise error."""
        service = PractitionerService()

        # Update with same email should not raise error
        updated = service.update(
            sample_practitioner.id,
            {
                'email': sample_practitioner.email,
                'specialization': 'Updated Specialization'
            }
        )

        assert updated.email == sample_practitioner.email
        assert updated.specialization == 'Updated Specialization'
