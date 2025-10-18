"""
Django management command to seed the database with realistic patient data.

Usage:
    python manage.py seed_patients --count 50
    python manage.py seed_patients --count 100 --clear
    python manage.py seed_patients --scenarios
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from patients.models import Patient
from patients.factories import (
    PatientFactory,
    create_diverse_patient_cohort,
    create_test_scenarios,
    PediatricPatientFactory,
    AdultPatientFactory,
    GeriatricPatientFactory,
)


class Command(BaseCommand):
    help = 'Seeds the database with realistic patient data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of random patients to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing patients before seeding'
        )
        parser.add_argument(
            '--scenarios',
            action='store_true',
            help='Create test scenario patients instead of random patients'
        )
        parser.add_argument(
            '--diverse',
            action='store_true',
            help='Create a diverse cohort with realistic age distribution'
        )
        parser.add_argument(
            '--pediatric',
            type=int,
            help='Create specified number of pediatric patients (under 18)'
        )
        parser.add_argument(
            '--adult',
            type=int,
            help='Create specified number of adult patients (18-64)'
        )
        parser.add_argument(
            '--geriatric',
            type=int,
            help='Create specified number of geriatric patients (65+)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        scenarios = options['scenarios']
        diverse = options['diverse']
        pediatric = options.get('pediatric')
        adult = options.get('adult')
        geriatric = options.get('geriatric')

        # Clear existing data if requested
        if clear:
            existing_count = Patient.objects.count()
            Patient.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {existing_count} existing patients')
            )

        created_patients = []

        try:
            # Create test scenarios
            if scenarios:
                scenario_patients = create_test_scenarios()
                created_patients.extend(scenario_patients.values())
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {len(scenario_patients)} test scenario patients:'
                    )
                )
                for name, patient in scenario_patients.items():
                    self.stdout.write(f'  - {name}: {patient}')

            # Create diverse cohort
            elif diverse:
                patients = create_diverse_patient_cohort(count)
                created_patients.extend(patients)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {len(patients)} patients with diverse demographics'
                    )
                )

                # Show distribution
                pediatric_count = sum(1 for p in patients if self._calculate_age(p.birth_date) < 18)
                adult_count = sum(1 for p in patients if 18 <= self._calculate_age(p.birth_date) < 65)
                geriatric_count = sum(1 for p in patients if self._calculate_age(p.birth_date) >= 65)

                self.stdout.write(f'  - Pediatric (0-17): {pediatric_count}')
                self.stdout.write(f'  - Adult (18-64): {adult_count}')
                self.stdout.write(f'  - Geriatric (65+): {geriatric_count}')

            # Create specific age groups
            elif pediatric or adult or geriatric:
                if pediatric:
                    patients = PediatricPatientFactory.create_batch(pediatric)
                    created_patients.extend(patients)
                    self.stdout.write(
                        self.style.SUCCESS(f'Created {pediatric} pediatric patients')
                    )

                if adult:
                    patients = AdultPatientFactory.create_batch(adult)
                    created_patients.extend(patients)
                    self.stdout.write(
                        self.style.SUCCESS(f'Created {adult} adult patients')
                    )

                if geriatric:
                    patients = GeriatricPatientFactory.create_batch(geriatric)
                    created_patients.extend(patients)
                    self.stdout.write(
                        self.style.SUCCESS(f'Created {geriatric} geriatric patients')
                    )

            # Create random patients
            else:
                patients = PatientFactory.create_batch(count)
                created_patients.extend(patients)
                self.stdout.write(
                    self.style.SUCCESS(f'Created {count} random patients')
                )

            # Summary statistics
            self._print_summary(created_patients)

        except Exception as e:
            raise CommandError(f'Error seeding patients: {str(e)}')

    def _calculate_age(self, birth_date):
        """Calculate age from birth date."""
        from datetime import date
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def _print_summary(self, patients):
        """Print summary statistics about created patients."""
        if not patients:
            return

        total = len(patients)

        # Gender distribution
        gender_counts = {}
        for patient in patients:
            gender_counts[patient.gender] = gender_counts.get(patient.gender, 0) + 1

        # Active status
        active_count = sum(1 for p in patients if p.active)
        inactive_count = total - active_count

        # Contact info
        with_email = sum(1 for p in patients if p.email)
        with_phone = sum(1 for p in patients if p.phone)

        self.stdout.write('\n' + self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Total patients created: {total}')
        self.stdout.write(f'  Total patients in database: {Patient.objects.count()}')
        self.stdout.write('\n  Gender distribution:')
        for gender, count in gender_counts.items():
            percentage = (count / total) * 100
            self.stdout.write(f'    - {gender}: {count} ({percentage:.1f}%)')

        self.stdout.write(f'\n  Active: {active_count}')
        self.stdout.write(f'  Inactive: {inactive_count}')
        self.stdout.write(f'\n  With email: {with_email}')
        self.stdout.write(f'  With phone: {with_phone}')
