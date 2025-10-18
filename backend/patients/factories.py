"""
Factory classes for generating realistic test data.

Uses factory_boy and Faker to create realistic patient instances
for testing and database seeding.
"""
import factory
from factory import fuzzy
from faker import Faker
from datetime import date, timedelta
import random

from .models import Patient

fake = Faker()


class PatientFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Patient instances with realistic data.

    Usage:
        # Create a patient with random data
        patient = PatientFactory()

        # Create a patient with specific attributes
        patient = PatientFactory(given_name='John', family_name='Doe')

        # Create multiple patients
        patients = PatientFactory.create_batch(10)

        # Create a pediatric patient (under 18)
        patient = PatientFactory(birth_date=fake.date_of_birth(minimum_age=0, maximum_age=17))
    """

    class Meta:
        model = Patient

    # Name fields
    family_name = factory.LazyAttribute(lambda x: fake.last_name())
    given_name = factory.LazyAttribute(lambda x: fake.first_name())
    middle_name = factory.LazyAttribute(
        lambda x: fake.first_name() if random.random() > 0.3 else None
    )

    # Gender - realistic distribution
    gender = factory.LazyAttribute(
        lambda x: random.choices(
            ['male', 'female', 'other', 'unknown'],
            weights=[48, 48, 3, 1]
        )[0]
    )

    # Birth date - realistic age distribution
    birth_date = factory.LazyAttribute(
        lambda x: fake.date_of_birth(minimum_age=0, maximum_age=100)
    )

    # Address fields - realistic US addresses
    address_line = factory.LazyAttribute(lambda x: fake.street_address())
    address_city = factory.LazyAttribute(lambda x: fake.city())
    address_state = factory.LazyAttribute(lambda x: fake.state_abbr())
    address_postal_code = factory.LazyAttribute(lambda x: fake.postcode())
    address_country = 'USA'

    # Contact information
    email = factory.LazyAttribute(
        lambda obj: f"{obj.given_name.lower()}.{obj.family_name.lower()}@{fake.free_email_domain()}"
    )
    phone = factory.LazyAttribute(lambda x: fake.phone_number())

    # Status
    active = factory.LazyAttribute(lambda x: random.random() > 0.05)  # 95% active


class PediatricPatientFactory(PatientFactory):
    """Factory for creating pediatric patients (under 18 years old)."""

    birth_date = factory.LazyAttribute(
        lambda x: fake.date_of_birth(minimum_age=0, maximum_age=17)
    )


class AdultPatientFactory(PatientFactory):
    """Factory for creating adult patients (18-64 years old)."""

    birth_date = factory.LazyAttribute(
        lambda x: fake.date_of_birth(minimum_age=18, maximum_age=64)
    )


class GeriatricPatientFactory(PatientFactory):
    """Factory for creating geriatric patients (65+ years old)."""

    birth_date = factory.LazyAttribute(
        lambda x: fake.date_of_birth(minimum_age=65, maximum_age=100)
    )


class MinimalPatientFactory(PatientFactory):
    """
    Factory for creating patients with only required fields.
    Useful for testing edge cases with minimal data.
    """

    middle_name = None
    address_line = None
    address_city = None
    address_state = None
    address_postal_code = None
    address_country = None
    email = None
    phone = None


class CompletePatientFactory(PatientFactory):
    """
    Factory for creating patients with all fields populated.
    Ensures no None values for optional fields.
    """

    middle_name = factory.LazyAttribute(lambda x: fake.first_name())
    email = factory.LazyAttribute(
        lambda obj: f"{obj.given_name.lower()}.{obj.family_name.lower()}@{fake.free_email_domain()}"
    )
    phone = factory.LazyAttribute(lambda x: fake.phone_number())


class InactivePatientFactory(PatientFactory):
    """Factory for creating inactive patients."""

    active = False


# Helper functions for generating patient cohorts

def create_diverse_patient_cohort(count=50):
    """
    Create a diverse cohort of patients with various demographics.

    Args:
        count: Total number of patients to create

    Returns:
        List of Patient instances
    """
    patients = []

    # Calculate distribution
    pediatric_count = int(count * 0.20)  # 20% pediatric
    adult_count = int(count * 0.60)      # 60% adult
    geriatric_count = int(count * 0.20)  # 20% geriatric

    # Create patients
    patients.extend(PediatricPatientFactory.create_batch(pediatric_count))
    patients.extend(AdultPatientFactory.create_batch(adult_count))
    patients.extend(GeriatricPatientFactory.create_batch(geriatric_count))

    return patients


def create_test_scenarios():
    """
    Create a set of patients covering common test scenarios.

    Returns:
        Dictionary mapping scenario names to Patient instances
    """
    return {
        'complete_adult': CompletePatientFactory(
            given_name='John',
            middle_name='Michael',
            family_name='Doe',
            gender='male',
            birth_date=date(1990, 1, 15)
        ),
        'minimal_patient': MinimalPatientFactory(
            given_name='Jane',
            family_name='Smith',
            gender='female',
            birth_date=date(1985, 6, 20)
        ),
        'pediatric': PediatricPatientFactory(
            given_name='Emily',
            family_name='Johnson',
            gender='female'
        ),
        'geriatric': GeriatricPatientFactory(
            given_name='Robert',
            family_name='Williams',
            gender='male'
        ),
        'inactive': InactivePatientFactory(
            given_name='Inactive',
            family_name='Patient',
            gender='unknown'
        ),
        'no_email': PatientFactory(
            given_name='NoEmail',
            family_name='Person',
            email=None,
            gender='other'
        ),
        'no_phone': PatientFactory(
            given_name='NoPhone',
            family_name='Person',
            phone=None,
            gender='male'
        ),
    }


def create_patients_by_state(state_abbr, count=10):
    """
    Create patients all residing in a specific state.

    Args:
        state_abbr: Two-letter state abbreviation (e.g., 'CA', 'NY')
        count: Number of patients to create

    Returns:
        List of Patient instances
    """
    return PatientFactory.create_batch(count, address_state=state_abbr)


def create_patients_by_age_range(min_age, max_age, count=10):
    """
    Create patients within a specific age range.

    Args:
        min_age: Minimum age in years
        max_age: Maximum age in years
        count: Number of patients to create

    Returns:
        List of Patient instances
    """
    patients = []
    for _ in range(count):
        birth_date = fake.date_of_birth(minimum_age=min_age, maximum_age=max_age)
        patients.append(PatientFactory(birth_date=birth_date))
    return patients
