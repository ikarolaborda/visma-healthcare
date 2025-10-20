"""
Tests for Patient factories.

Ensures that factories generate valid, realistic patient data.
"""
import pytest
from datetime import date, timedelta
from patients.models import Patient
from patients.factories import (
    PatientFactory,
    PediatricPatientFactory,
    AdultPatientFactory,
    GeriatricPatientFactory,
    MinimalPatientFactory,
    CompletePatientFactory,
    InactivePatientFactory,
    create_diverse_patient_cohort,
    create_test_scenarios,
    create_patients_by_age_range,
)


@pytest.mark.django_db
class TestPatientFactory:
    """Test PatientFactory generates valid patients."""

    def test_creates_valid_patient(self):
        """Test factory creates a valid patient with all required fields."""
        patient = PatientFactory()

        assert patient.id is not None
        assert patient.given_name
        assert patient.family_name
        assert patient.gender in ['male', 'female', 'other', 'unknown']
        assert patient.birth_date
        assert isinstance(patient.birth_date, date)
        assert patient.active is not None

    def test_creates_multiple_patients(self):
        """Test creating multiple patients in batch."""
        patients = PatientFactory.create_batch(10)

        assert len(patients) == 10
        assert Patient.objects.count() == 10

        # Verify all patients are unique
        patient_ids = [p.id for p in patients]
        assert len(patient_ids) == len(set(patient_ids))

    def test_patient_has_realistic_address(self):
        """Test patient has realistic US address."""
        patient = PatientFactory()

        assert patient.address_line
        assert patient.address_city
        assert patient.address_state
        assert len(patient.address_state) == 2  # State abbreviation
        assert patient.address_postal_code
        assert patient.address_country == 'USA'

    def test_patient_has_contact_info(self):
        """Test patient has email and phone."""
        patient = PatientFactory()

        assert patient.email
        assert '@' in patient.email
        assert patient.phone

    def test_gender_distribution(self):
        """Test gender distribution is realistic."""
        patients = PatientFactory.create_batch(100)

        gender_counts = {}
        for patient in patients:
            gender_counts[patient.gender] = gender_counts.get(patient.gender, 0) + 1

        # Male and female should be most common
        assert gender_counts.get('male', 0) > 20
        assert gender_counts.get('female', 0) > 20

    def test_can_override_attributes(self):
        """Test factory allows overriding specific attributes."""
        patient = PatientFactory(
            given_name='John',
            family_name='Doe',
            gender='male'
        )

        assert patient.given_name == 'John'
        assert patient.family_name == 'Doe'
        assert patient.gender == 'male'


@pytest.mark.django_db
class TestAgeSpecificFactories:
    """Test age-specific patient factories."""

    def _calculate_age(self, birth_date):
        """Helper to calculate age."""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def test_pediatric_factory_creates_minors(self):
        """Test pediatric factory creates patients under 18."""
        patients = PediatricPatientFactory.create_batch(20)

        for patient in patients:
            age = self._calculate_age(patient.birth_date)
            assert age < 18, f"Pediatric patient has age {age}"

    def test_adult_factory_creates_adults(self):
        """Test adult factory creates patients aged 18-64."""
        patients = AdultPatientFactory.create_batch(20)

        for patient in patients:
            age = self._calculate_age(patient.birth_date)
            assert 18 <= age < 65, f"Adult patient has age {age}"

    def test_geriatric_factory_creates_elderly(self):
        """Test geriatric factory creates patients 65+."""
        patients = GeriatricPatientFactory.create_batch(20)

        for patient in patients:
            age = self._calculate_age(patient.birth_date)
            assert age >= 65, f"Geriatric patient has age {age}"


@pytest.mark.django_db
class TestSpecializedFactories:
    """Test specialized patient factories."""

    def test_minimal_factory_only_required_fields(self):
        """Test minimal factory creates patient with only required fields."""
        patient = MinimalPatientFactory()

        # Required fields should be present
        assert patient.given_name
        assert patient.family_name
        assert patient.gender
        assert patient.birth_date

        # Optional fields should be None
        assert patient.middle_name is None
        assert patient.email is None
        assert patient.phone is None
        assert patient.address_line is None

    def test_complete_factory_all_fields_populated(self):
        """Test complete factory populates all fields."""
        patient = CompletePatientFactory()

        assert patient.given_name
        assert patient.middle_name
        assert patient.family_name
        assert patient.gender
        assert patient.birth_date
        assert patient.email
        assert patient.phone
        assert patient.address_line
        assert patient.address_city
        assert patient.address_state
        assert patient.address_postal_code
        assert patient.address_country

    def test_inactive_factory_creates_inactive_patient(self):
        """Test inactive factory creates inactive patient."""
        patient = InactivePatientFactory()

        assert patient.active is False


@pytest.mark.django_db
class TestHelperFunctions:
    """Test factory helper functions."""

    def test_create_diverse_cohort(self):
        """Test creating diverse patient cohort."""
        patients = create_diverse_patient_cohort(count=50)

        assert len(patients) == 50
        assert Patient.objects.count() == 50

        # Check we have patients of various ages
        ages = [self._calculate_age(p.birth_date) for p in patients]
        assert min(ages) < 18  # Has pediatric patients
        assert max(ages) >= 65  # Has geriatric patients
        assert any(18 <= age < 65 for age in ages)  # Has adult patients

    def test_create_test_scenarios(self):
        """Test creating test scenario patients."""
        scenarios = create_test_scenarios()

        assert 'complete_adult' in scenarios
        assert 'minimal_patient' in scenarios
        assert 'pediatric' in scenarios
        assert 'geriatric' in scenarios
        assert 'inactive' in scenarios

        # Verify specific characteristics
        assert scenarios['complete_adult'].given_name == 'John'
        assert scenarios['minimal_patient'].email is None
        assert scenarios['inactive'].active is False

    def test_create_patients_by_age_range(self):
        """Test creating patients in specific age range."""
        patients = create_patients_by_age_range(min_age=30, max_age=40, count=10)

        assert len(patients) == 10

        for patient in patients:
            age = self._calculate_age(patient.birth_date)
            assert 30 <= age <= 40, f"Patient age {age} not in range 30-40"

    def _calculate_age(self, birth_date):
        """Helper to calculate age."""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )


@pytest.mark.django_db
class TestDataRealism:
    """Test that generated data is realistic and valid."""

    def test_names_are_realistic(self):
        """Test generated names are realistic."""
        patients = PatientFactory.create_batch(10)

        for patient in patients:
            # Names should not be empty or contain numbers
            assert patient.given_name.isalpha() or ' ' in patient.given_name
            assert patient.family_name.isalpha() or '-' in patient.family_name

    def test_email_format_is_valid(self):
        """Test email addresses have valid format."""
        patients = PatientFactory.create_batch(10)

        for patient in patients:
            if patient.email:
                assert '@' in patient.email
                assert '.' in patient.email.split('@')[1]

    def test_state_abbreviations_are_valid(self):
        """Test state abbreviations are 2 letters."""
        patients = PatientFactory.create_batch(20)

        for patient in patients:
            if patient.address_state:
                assert len(patient.address_state) == 2
                assert patient.address_state.isupper()

    def test_birth_dates_are_in_past(self):
        """Test all birth dates are in the past."""
        patients = PatientFactory.create_batch(20)
        today = date.today()

        for patient in patients:
            assert patient.birth_date < today

    def test_birth_dates_are_reasonable(self):
        """Test birth dates are within reasonable range (0-100 years ago)."""
        patients = PatientFactory.create_batch(20)
        today = date.today()
        # Account for leap years: 100 years = ~36525 days (365.25 * 100)
        min_date = today - timedelta(days=int(365.25 * 100) + 1)  # 100 years ago with buffer

        for patient in patients:
            assert min_date <= patient.birth_date <= today
