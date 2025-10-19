#!/usr/bin/env python3
"""
Comprehensive data seeding script for healthcare application
Creates realistic, production-like data for all entities
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from patients.models import Patient
from practitioners.models import Practitioner
from appointments.models import Appointment
from prescriptions.models import Prescription
from patient_history.models import ClinicalRecord
from billing.models import Invoice

# Realistic patient data
PATIENT_DATA = [
    {"given": "Sarah", "family": "Anderson", "gender": "female", "birth_date": "1985-03-15", "email": "sarah.anderson@email.com", "phone": "+1-555-0101"},
    {"given": "Michael", "family": "Chen", "gender": "male", "birth_date": "1972-11-20", "email": "michael.chen@email.com", "phone": "+1-555-0102"},
    {"given": "Jennifer", "family": "Martinez", "gender": "female", "birth_date": "1990-07-08", "email": "jennifer.martinez@email.com", "phone": "+1-555-0103"},
    {"given": "Robert", "family": "Johnson", "gender": "male", "birth_date": "1965-05-12", "email": "robert.johnson@email.com", "phone": "+1-555-0104"},
    {"given": "Emily", "family": "Williams", "gender": "female", "birth_date": "1988-09-25", "email": "emily.williams@email.com", "phone": "+1-555-0105"},
    {"given": "David", "family": "Taylor", "gender": "male", "birth_date": "1978-02-14", "email": "david.taylor@email.com", "phone": "+1-555-0106"},
    {"given": "Jessica", "family": "Brown", "gender": "female", "birth_date": "1995-12-03", "email": "jessica.brown@email.com", "phone": "+1-555-0107"},
    {"given": "Christopher", "family": "Davis", "gender": "male", "birth_date": "1982-06-30", "email": "christopher.davis@email.com", "phone": "+1-555-0108"},
    {"given": "Amanda", "family": "Wilson", "gender": "female", "birth_date": "1991-04-18", "email": "amanda.wilson@email.com", "phone": "+1-555-0109"},
    {"given": "James", "family": "Moore", "gender": "male", "birth_date": "1970-08-22", "email": "james.moore@email.com", "phone": "+1-555-0110"},
    {"given": "Lisa", "family": "Garcia", "gender": "female", "birth_date": "1987-01-09", "email": "lisa.garcia@email.com", "phone": "+1-555-0111"},
    {"given": "Daniel", "family": "Rodriguez", "gender": "male", "birth_date": "1993-10-15", "email": "daniel.rodriguez@email.com", "phone": "+1-555-0112"},
    {"given": "Maria", "family": "Lopez", "gender": "female", "birth_date": "1968-03-28", "email": "maria.lopez@email.com", "phone": "+1-555-0113"},
    {"given": "Matthew", "family": "Lee", "gender": "male", "birth_date": "1984-07-11", "email": "matthew.lee@email.com", "phone": "+1-555-0114"},
    {"given": "Laura", "family": "White", "gender": "female", "birth_date": "1992-05-06", "email": "laura.white@email.com", "phone": "+1-555-0115"},
]

# Realistic practitioner data
PRACTITIONER_DATA = [
    {"prefix": "Dr.", "given": "Elizabeth", "family": "Thompson", "gender": "female", "specialization": "Cardiology", "qualification": "MD, FACC", "npi": "1234567890", "license": "MD-001", "email": "dr.thompson@hospital.com", "phone": "+1-555-0201", "years_exp": 15},
    {"prefix": "Dr.", "given": "Richard", "family": "Martinez", "gender": "male", "specialization": "Pediatrics", "qualification": "MD, FAAP", "npi": "2345678901", "license": "MD-002", "email": "dr.martinez@hospital.com", "phone": "+1-555-0202", "years_exp": 12},
    {"prefix": "Dr.", "given": "Susan", "family": "Anderson", "gender": "female", "specialization": "Internal Medicine", "qualification": "MD, FACP", "npi": "3456789012", "license": "MD-003", "email": "dr.anderson@hospital.com", "phone": "+1-555-0203", "years_exp": 18},
    {"prefix": "Dr.", "given": "Thomas", "family": "Wilson", "gender": "male", "specialization": "Orthopedics", "qualification": "MD, FAAOS", "npi": "4567890123", "license": "MD-004", "email": "dr.wilson@hospital.com", "phone": "+1-555-0204", "years_exp": 20},
    {"prefix": "Dr.", "given": "Patricia", "family": "Davis", "gender": "female", "specialization": "Dermatology", "qualification": "MD, FAAD", "npi": "5678901234", "license": "MD-005", "email": "dr.davis@hospital.com", "phone": "+1-555-0205", "years_exp": 14},
    {"prefix": "Dr.", "given": "John", "family": "Miller", "gender": "male", "specialization": "Neurology", "qualification": "MD, FAAN", "npi": "6789012345", "license": "MD-006", "email": "dr.miller@hospital.com", "phone": "+1-555-0206", "years_exp": 16},
    {"prefix": "Dr.", "given": "Karen", "family": "Moore", "gender": "female", "specialization": "Endocrinology", "qualification": "MD, FACE", "npi": "7890123456", "license": "MD-007", "email": "dr.moore@hospital.com", "phone": "+1-555-0207", "years_exp": 11},
    {"prefix": "Dr.", "given": "Kevin", "family": "Taylor", "gender": "male", "specialization": "General Surgery", "qualification": "MD, FACS", "npi": "8901234567", "license": "MD-008", "email": "dr.taylor@hospital.com", "phone": "+1-555-0208", "years_exp": 22},
]

# Common medications
MEDICATIONS = [
    {"name": "Lisinopril", "strength": "10mg", "dosage": "Take 1 tablet by mouth once daily", "route": "oral"},
    {"name": "Metformin", "strength": "500mg", "dosage": "Take 1 tablet by mouth twice daily with meals", "route": "oral"},
    {"name": "Atorvastatin", "strength": "20mg", "dosage": "Take 1 tablet by mouth once daily at bedtime", "route": "oral"},
    {"name": "Levothyroxine", "strength": "50mcg", "dosage": "Take 1 tablet by mouth once daily in the morning", "route": "oral"},
    {"name": "Omeprazole", "strength": "20mg", "dosage": "Take 1 capsule by mouth once daily before breakfast", "route": "oral"},
    {"name": "Amlodipine", "strength": "5mg", "dosage": "Take 1 tablet by mouth once daily", "route": "oral"},
    {"name": "Metoprolol", "strength": "25mg", "dosage": "Take 1 tablet by mouth twice daily", "route": "oral"},
    {"name": "Albuterol", "strength": "90mcg", "dosage": "Inhale 2 puffs every 4-6 hours as needed", "route": "inhalation"},
    {"name": "Gabapentin", "strength": "300mg", "dosage": "Take 1 capsule by mouth three times daily", "route": "oral"},
    {"name": "Sertraline", "strength": "50mg", "dosage": "Take 1 tablet by mouth once daily", "route": "oral"},
]

# Common conditions
CONDITIONS = [
    {"title": "Hypertension (High Blood Pressure)", "type": "condition", "severity": "moderate", "code": "I10"},
    {"title": "Type 2 Diabetes Mellitus", "type": "condition", "severity": "moderate", "code": "E11.9"},
    {"title": "Hyperlipidemia", "type": "condition", "severity": "mild", "code": "E78.5"},
    {"title": "Asthma", "type": "condition", "severity": "mild", "code": "J45.909"},
    {"title": "Chronic Back Pain", "type": "condition", "severity": "moderate", "code": "M54.5"},
    {"title": "Depression", "type": "condition", "severity": "moderate", "code": "F33.1"},
    {"title": "Gastroesophageal Reflux Disease (GERD)", "type": "condition", "severity": "mild", "code": "K21.9"},
    {"title": "Hypothyroidism", "type": "condition", "severity": "mild", "code": "E03.9"},
]

OBSERVATIONS = [
    {"title": "Blood Pressure Reading", "type": "observation", "value": "120/80", "unit": "mmHg"},
    {"title": "Blood Glucose Level", "type": "observation", "value": "95", "unit": "mg/dL"},
    {"title": "Weight Measurement", "type": "observation", "value": "165", "unit": "lbs"},
    {"title": "Height Measurement", "type": "observation", "value": "68", "unit": "inches"},
    {"title": "Body Temperature", "type": "observation", "value": "98.6", "unit": "°F"},
    {"title": "Heart Rate", "type": "observation", "value": "72", "unit": "bpm"},
    {"title": "Cholesterol Total", "type": "observation", "value": "185", "unit": "mg/dL"},
]

def clear_existing_data():
    """Clear all existing data"""
    print("Clearing existing data...")
    Invoice.objects.all().delete()
    ClinicalRecord.objects.all().delete()
    Prescription.objects.all().delete()
    Appointment.objects.all().delete()
    Practitioner.objects.all().delete()
    Patient.objects.all().delete()
    print("✓ Existing data cleared")

def seed_patients():
    """Seed realistic patient data"""
    print("\nSeeding patients...")
    patients = []

    for data in PATIENT_DATA:
        patient = Patient.objects.create(
            given_name=data["given"],
            family_name=data["family"],
            gender=data["gender"],
            birth_date=data["birth_date"],
            email=data["email"],
            phone=data["phone"],
            address_line="123 Main Street",
            address_city="Boston",
            address_state="MA",
            address_postal_code="02101",
            address_country="USA",
            active=True
        )
        patients.append(patient)
        print(f"  ✓ Created patient: {data['given']} {data['family']}")

    return patients

def seed_practitioners():
    """Seed realistic practitioner data"""
    print("\nSeeding practitioners...")
    practitioners = []

    for data in PRACTITIONER_DATA:
        practitioner = Practitioner.objects.create(
            prefix=data["prefix"],
            given_name=data["given"],
            family_name=data["family"],
            gender=data["gender"],
            birth_date=datetime.now().date() - timedelta(days=365*40),  # About 40 years old
            npi=data["npi"],
            license_number=data["license"],
            specialization=data["specialization"],
            qualification=data["qualification"],
            years_of_experience=data["years_exp"],
            email=data["email"],
            phone=data["phone"],
            address_line="456 Hospital Drive",
            address_city="Boston",
            address_state="MA",
            address_postal_code="02102",
            address_country="USA",
            active=True
        )
        practitioners.append(practitioner)
        print(f"  ✓ Created practitioner: Dr. {data['given']} {data['family']} ({data['specialization']})")

    return practitioners

def seed_appointments(patients, practitioners):
    """Seed realistic appointments"""
    print("\nSeeding appointments...")
    appointments = []
    statuses = ['booked', 'booked', 'booked', 'arrived', 'fulfilled', 'cancelled']
    appointment_types = ['checkup', 'follow-up', 'consultation', 'emergency', 'procedure']

    # Create appointments for the past 30 days and next 30 days
    for i in range(50):
        patient = random.choice(patients)
        practitioner = random.choice(practitioners)

        # Random date within past 30 days or next 30 days
        days_offset = random.randint(-30, 30)
        start_date = datetime.now() + timedelta(days=days_offset)

        # Random time between 8 AM and 5 PM
        hour = random.randint(8, 16)
        start_date = start_date.replace(hour=hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)

        # Duration: 30 or 60 minutes
        duration = random.choice([30, 60])
        end_date = start_date + timedelta(minutes=duration)

        # Past appointments more likely to be fulfilled
        if days_offset < 0:
            status = random.choice(['fulfilled', 'fulfilled', 'arrived', 'cancelled'])
        else:
            status = random.choice(['booked', 'booked', 'pending'])

        appointment = Appointment.objects.create(
            patient=patient,
            practitioner=practitioner,
            status=status,
            appointment_type=random.choice(appointment_types),
            start=start_date,
            end=end_date,
            minutes_duration=duration,
            description=f"{random.choice(['Annual', 'Follow-up', 'Initial', 'Routine'])} {practitioner.specialization} {random.choice(appointment_types)}",
            reason_code=f"Visit for {practitioner.specialization.lower()}",
            priority=random.randint(1, 5)
        )
        appointments.append(appointment)

    print(f"  ✓ Created {len(appointments)} appointments")
    return appointments

def seed_prescriptions(patients, practitioners):
    """Seed realistic prescriptions"""
    print("\nSeeding prescriptions...")
    prescriptions = []

    for i in range(40):
        patient = random.choice(patients)
        practitioner = random.choice(practitioners)
        medication = random.choice(MEDICATIONS)

        prescription = Prescription.objects.create(
            patient=patient,
            prescriber=practitioner,
            medication_name=medication["name"],
            strength=medication["strength"],
            dosage_text=medication["dosage"],
            dosage_route=medication["route"],
            dosage_frequency="As directed",
            dose_quantity="1",
            quantity=random.choice([30, 60, 90]),
            refills=random.randint(0, 3),
            status=random.choice(['active', 'active', 'active', 'completed']),
            validity_start=datetime.now().date(),
            validity_end=datetime.now().date() + timedelta(days=random.choice([90, 180, 365]))
        )
        prescriptions.append(prescription)

    print(f"  ✓ Created {len(prescriptions)} prescriptions")
    return prescriptions

def seed_clinical_records(patients, practitioners):
    """Seed realistic clinical records"""
    print("\nSeeding clinical records...")
    records = []

    # Seed conditions
    for i in range(30):
        patient = random.choice(patients)
        practitioner = random.choice(practitioners)
        condition = random.choice(CONDITIONS)

        record = ClinicalRecord.objects.create(
            patient=patient,
            recorded_by=practitioner,
            record_type=condition["type"],
            title=condition["title"],
            code=condition["code"],
            severity=condition.get("severity"),
            status=random.choice(['active', 'active', 'resolved']),
            recorded_date=datetime.now().date() - timedelta(days=random.randint(1, 365)),
            notes=f"Patient diagnosed with {condition['title'].lower()}. Treatment plan initiated."
        )
        records.append(record)

    # Seed observations
    for i in range(40):
        patient = random.choice(patients)
        practitioner = random.choice(practitioners)
        observation = random.choice(OBSERVATIONS)

        record = ClinicalRecord.objects.create(
            patient=patient,
            recorded_by=practitioner,
            record_type=observation["type"],
            title=observation["title"],
            value_quantity=observation["value"],
            value_unit=observation["unit"],
            status='active',
            recorded_date=datetime.now().date() - timedelta(days=random.randint(1, 30)),
            notes=f"Routine {observation['title'].lower()} recorded during visit."
        )
        records.append(record)

    print(f"  ✓ Created {len(records)} clinical records")
    return records

def seed_invoices(patients, appointments):
    """Seed realistic invoices"""
    print("\nSeeding invoices...")
    invoices = []

    # Create invoices for completed appointments
    fulfilled_appointments = [apt for apt in appointments if apt.status in ['fulfilled', 'arrived']]

    for i, appointment in enumerate(fulfilled_appointments[:30]):
        # Generate realistic amounts
        base_amount = Decimal(random.choice(['75.00', '150.00', '225.00', '350.00', '500.00']))
        total_net = base_amount
        total_gross = total_net * Decimal('1.08')  # 8% tax

        # Some invoices are paid, some partially paid, some unpaid
        payment_status = random.choice(['paid', 'paid', 'partial', 'unpaid'])
        if payment_status == 'paid':
            amount_paid = total_gross
            status = 'paid'
        elif payment_status == 'partial':
            amount_paid = total_gross * Decimal(random.choice(['0.25', '0.5', '0.75']))
            status = 'issued'
        else:
            amount_paid = Decimal('0.00')
            status = random.choice(['issued', 'draft'])

        invoice = Invoice.objects.create(
            invoice_number=f"INV-2025-{str(i+1).zfill(4)}",
            patient=appointment.patient,
            appointment=appointment,
            status=status,
            issue_date=appointment.start.date(),
            due_date=appointment.start.date() + timedelta(days=30),
            total_net=total_net,
            total_gross=total_gross,
            amount_paid=amount_paid,
            service_description=f"{appointment.appointment_type} with {appointment.practitioner.get_full_name()}",
            notes=f"Invoice for {appointment.appointment_type} appointment with {appointment.practitioner.get_full_name()}"
        )
        invoices.append(invoice)

    print(f"  ✓ Created {len(invoices)} invoices")
    return invoices

def main():
    """Main seeding function"""
    print("=" * 60)
    print("Healthcare Application - Realistic Data Seeding")
    print("=" * 60)

    try:
        # Clear existing data
        clear_existing_data()

        # Seed data in order
        patients = seed_patients()
        practitioners = seed_practitioners()
        appointments = seed_appointments(patients, practitioners)
        prescriptions = seed_prescriptions(patients, practitioners)
        records = seed_clinical_records(patients, practitioners)
        invoices = seed_invoices(patients, appointments)

        # Summary
        print("\n" + "=" * 60)
        print("SEEDING SUMMARY")
        print("=" * 60)
        print(f"  Patients:         {len(patients)}")
        print(f"  Practitioners:    {len(practitioners)}")
        print(f"  Appointments:     {len(appointments)}")
        print(f"  Prescriptions:    {len(prescriptions)}")
        print(f"  Clinical Records: {len(records)}")
        print(f"  Invoices:         {len(invoices)}")
        print("=" * 60)
        print("✓ Data seeding completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
