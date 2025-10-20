"""
Tests for Practitioner repositories.

Tests repository pattern implementation.
"""
import pytest
from practitioners.models import Practitioner
from practitioners.repositories import PractitionerRepository


@pytest.mark.django_db
class TestPractitionerRepository:
    """Test cases for PractitionerRepository."""

    def test_find_by_npi(self, sample_practitioner):
        """Test finding practitioner by NPI."""
        repo = PractitionerRepository()
        found = repo.find_by_npi('1234567890')

        assert found is not None
        assert found.id == sample_practitioner.id
        assert found.npi == '1234567890'

    def test_find_by_npi_not_found(self):
        """Test finding non-existent NPI."""
        repo = PractitionerRepository()
        found = repo.find_by_npi('9999999999')

        assert found is None

    def test_find_by_specialization(self):
        """Test finding practitioners by specialization."""
        Practitioner.objects.create(
            given_name='John',
            family_name='Doe',
            gender='male',
            specialization='Cardiology',
            qualification='MD',
            email='john@hospital.com',
            phone='+1-555-1111'
        )

        Practitioner.objects.create(
            given_name='Jane',
            family_name='Smith',
            gender='female',
            specialization='Cardiology',
            qualification='MD',
            email='jane@hospital.com',
            phone='+1-555-2222'
        )

        Practitioner.objects.create(
            given_name='Bob',
            family_name='Wilson',
            gender='male',
            specialization='Neurology',
            qualification='MD',
            email='bob@hospital.com',
            phone='+1-555-3333'
        )

        repo = PractitionerRepository()
        cardiologists = repo.find_by_specialization('Cardiology')

        assert len(cardiologists) == 2
        assert all(p.specialization == 'Cardiology' for p in cardiologists)

    def test_find_by_specialization_case_insensitive(self):
        """Test finding practitioners by specialization is case-insensitive."""
        Practitioner.objects.create(
            given_name='Test',
            family_name='Doctor',
            gender='male',
            specialization='Cardiology',
            qualification='MD',
            email='test@hospital.com',
            phone='+1-555-4444'
        )

        repo = PractitionerRepository()
        results = repo.find_by_specialization('cardiology')

        assert len(results) == 1

    def test_find_by_specialization_partial_match(self):
        """Test partial matching on specialization."""
        Practitioner.objects.create(
            given_name='Test',
            family_name='Doctor',
            gender='male',
            specialization='Pediatric Cardiology',
            qualification='MD',
            email='test@hospital.com',
            phone='+1-555-5555'
        )

        repo = PractitionerRepository()
        results = repo.find_by_specialization('Cardio')

        assert len(results) == 1

    def test_find_active_practitioners(self):
        """Test finding only active practitioners."""
        Practitioner.objects.create(
            given_name='Active',
            family_name='Doctor',
            gender='male',
            specialization='General Practice',
            qualification='MD',
            email='active@hospital.com',
            phone='+1-555-6666',
            active=True
        )

        Practitioner.objects.create(
            given_name='Inactive',
            family_name='Doctor',
            gender='female',
            specialization='General Practice',
            qualification='MD',
            email='inactive@hospital.com',
            phone='+1-555-7777',
            active=False
        )

        repo = PractitionerRepository()
        active_practitioners = repo.find_active_practitioners()

        assert len(active_practitioners) == 1
        assert active_practitioners[0].given_name == 'Active'

    def test_find_by_email(self):
        """Test finding practitioner by email."""
        practitioner = Practitioner.objects.create(
            given_name='Test',
            family_name='Doctor',
            gender='male',
            specialization='Surgery',
            qualification='MD',
            email='test.doctor@hospital.com',
            phone='+1-555-8888'
        )

        repo = PractitionerRepository()
        found = repo.find_by_email('test.doctor@hospital.com')

        assert found is not None
        assert found.id == practitioner.id
        assert found.email == 'test.doctor@hospital.com'

    def test_find_by_email_not_found(self):
        """Test finding non-existent email."""
        repo = PractitionerRepository()
        found = repo.find_by_email('nonexistent@hospital.com')

        assert found is None

    def test_search_by_name_given_name(self):
        """Test searching practitioners by given name."""
        Practitioner.objects.create(
            given_name='Sarah',
            family_name='Johnson',
            gender='female',
            specialization='Pediatrics',
            qualification='MD',
            email='sarah@hospital.com',
            phone='+1-555-9991'
        )

        Practitioner.objects.create(
            given_name='Michael',
            family_name='Williams',
            gender='male',
            specialization='Surgery',
            qualification='MD',
            email='michael@hospital.com',
            phone='+1-555-9992'
        )

        repo = PractitionerRepository()
        results = repo.search_by_name('Sarah')

        assert len(results) == 1
        assert results[0].given_name == 'Sarah'

    def test_search_by_name_family_name(self):
        """Test searching practitioners by family name."""
        Practitioner.objects.create(
            given_name='John',
            family_name='Anderson',
            gender='male',
            specialization='Cardiology',
            qualification='MD',
            email='john.anderson@hospital.com',
            phone='+1-555-9993'
        )

        repo = PractitionerRepository()
        results = repo.search_by_name('Anderson')

        assert len(results) == 1
        assert results[0].family_name == 'Anderson'

    def test_search_by_name_case_insensitive(self):
        """Test name search is case-insensitive."""
        Practitioner.objects.create(
            given_name='Jennifer',
            family_name='Martinez',
            gender='female',
            specialization='Neurology',
            qualification='MD',
            email='jennifer@hospital.com',
            phone='+1-555-9994'
        )

        repo = PractitionerRepository()
        results = repo.search_by_name('jennifer')

        assert len(results) == 1

    def test_search_by_name_partial_match(self):
        """Test partial name matching."""
        Practitioner.objects.create(
            given_name='Christopher',
            family_name='Brown',
            gender='male',
            specialization='Orthopedics',
            qualification='MD',
            email='chris@hospital.com',
            phone='+1-555-9995'
        )

        repo = PractitionerRepository()
        results = repo.search_by_name('Chris')

        assert len(results) == 1

    def test_search_by_name_only_active(self):
        """Test name search returns only active practitioners."""
        Practitioner.objects.create(
            given_name='Active',
            family_name='Smith',
            gender='male',
            specialization='General Practice',
            qualification='MD',
            email='active.smith@hospital.com',
            phone='+1-555-9996',
            active=True
        )

        Practitioner.objects.create(
            given_name='Inactive',
            family_name='Smith',
            gender='female',
            specialization='General Practice',
            qualification='MD',
            email='inactive.smith@hospital.com',
            phone='+1-555-9997',
            active=False
        )

        repo = PractitionerRepository()
        results = repo.search_by_name('Smith')

        assert len(results) == 1
        assert results[0].given_name == 'Active'

    def test_create_practitioner(self):
        """Test creating a practitioner via repository."""
        repo = PractitionerRepository()
        practitioner = repo.create(
            given_name='New',
            family_name='Doctor',
            gender='other',
            specialization='General Practice',
            qualification='MD',
            email='new@hospital.com',
            phone='+1-555-9998'
        )

        assert practitioner.id is not None
        assert practitioner.given_name == 'New'

        # Verify in database
        assert Practitioner.objects.filter(email='new@hospital.com').exists()

    def test_update_practitioner(self, sample_practitioner):
        """Test updating a practitioner via repository."""
        repo = PractitionerRepository()
        updated = repo.update(
            sample_practitioner.id,
            specialization='Updated Specialization'
        )

        assert updated.specialization == 'Updated Specialization'

        # Verify in database
        sample_practitioner.refresh_from_db()
        assert sample_practitioner.specialization == 'Updated Specialization'

    def test_delete_practitioner(self, sample_practitioner):
        """Test deleting a practitioner via repository."""
        practitioner_id = sample_practitioner.id

        repo = PractitionerRepository()
        result = repo.delete(practitioner_id)

        assert result is True
        # Verify deletion
        assert not Practitioner.objects.filter(id=practitioner_id).exists()

    def test_get_all(self):
        """Test getting all practitioners."""
        Practitioner.objects.create(
            given_name='First',
            family_name='Doctor',
            gender='male',
            specialization='Cardiology',
            qualification='MD',
            email='first@hospital.com',
            phone='+1-555-1001'
        )

        Practitioner.objects.create(
            given_name='Second',
            family_name='Doctor',
            gender='female',
            specialization='Neurology',
            qualification='MD',
            email='second@hospital.com',
            phone='+1-555-1002'
        )

        repo = PractitionerRepository()
        all_practitioners = list(repo.get_all())

        assert len(all_practitioners) == 2
