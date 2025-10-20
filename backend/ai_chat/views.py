from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import os

from appointments.models import Appointment
from prescriptions.models import Prescription
from practitioners.models import Practitioner
from billing.models import Invoice
from patients.models import Patient
from patient_history.models import ClinicalRecord

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from django.core.cache import cache
import hashlib


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    Handle AI chat requests with predefined prompts
    """
    prompt = request.data.get('prompt', '').strip()

    if not prompt:
        return Response(
            {'error': 'Prompt is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Process the prompt and generate response
    try:
        response_text = process_prompt(prompt)
        return Response({'response': response_text})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def process_prompt(prompt: str) -> str:
    """
    Process the prompt and generate response using AI with comprehensive database context.
    """
    # Check Redis cache first (1 hour TTL for database context)
    cache_key = f"ai_chat:{hashlib.md5(prompt.encode()).hexdigest()}"
    cached_response = cache.get(cache_key)

    if cached_response:
        return cached_response

    # Build comprehensive database context
    db_context = build_database_context()

    # Use OpenAI to generate a natural language response
    openai_api_key = os.environ.get('OPENAI_API_KEY')

    if openai_api_key and OpenAI:
        try:
            client = OpenAI(api_key=openai_api_key)

            system_prompt = """You are an AI assistant for a FHIR R4-compliant Healthcare Patient Management System.

SYSTEM OVERVIEW:
This is a comprehensive healthcare management platform built with Django REST Framework (backend) and Vue 3 (frontend). The system manages patient information, practitioner schedules, appointments, prescriptions, clinical records, and billing operations - all compliant with FHIR R4 standards.

AVAILABLE FHIR RESOURCES:
1. Patient - FHIR Patient resources containing demographics (name, gender, birth date), contact information (phone, email via telecom), addresses, and active/inactive status
2. Practitioner - Healthcare providers with specializations, qualifications, contact details, and FHIR-compliant name structures
3. Appointment - Scheduled appointments linking patients with practitioners, including status (proposed, pending, booked, arrived, fulfilled, cancelled), start/end times, appointment type, and reasons
4. Prescription (MedicationRequest) - FHIR MedicationRequest resources with medication names, dosage instructions, status (active, on-hold, cancelled, completed), authored dates, and prescriber information
5. Invoice - Billing records with status (issued, balanced, paid, cancelled), line items, totals, and payment tracking
6. ClinicalRecord - Patient clinical history including diagnoses, observations, procedures, and encounter notes

DATA STRUCTURE NOTES:
- All resources use FHIR R4 format with nested structures
- HumanName: {use, prefix[], given[], family}
- Address: {use, line[], city, state, postalCode, country}
- ContactPoint (telecom): {system, value, use}
- All resources have resourceType, id, and standard FHIR metadata

YOUR ROLE:
Answer user questions about their healthcare data clearly and concisely. Use the database statistics provided to give accurate, data-driven responses. When asked about trends, patterns, or specific metrics, refer to the current database state. Keep responses professional, helpful, and under 150 words unless more detail is explicitly requested.

IMPORTANT:
- Base all answers on the provided database statistics
- If data is not available in the context, clearly state that
- Provide actionable insights when relevant
- Use medical terminology appropriately but remain accessible
- Format numbers and dates clearly"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"{db_context}\n\nUser Question: {prompt}\n\nProvide a clear, data-driven answer based on the statistics above."
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

            # Cache the response for 1 hour (3600 seconds)
            cache.set(cache_key, ai_response, 3600)

            return ai_response
        except Exception as e:
            # Fallback to database context if OpenAI fails
            print(f"OpenAI API Error: {str(e)}")
            fallback = f"I encountered an issue processing your request with AI. Here's the current database overview:\n\n{db_context}"
            # Cache the fallback response for 30 minutes
            cache.set(cache_key, fallback, 1800)
            return fallback
    else:
        # If no OpenAI key, return database context
        fallback = f"AI features require OpenAI API configuration. Here's the current database overview:\n\n{db_context}"
        # Cache the fallback response for 30 minutes
        cache.set(cache_key, fallback, 1800)
        return fallback


def get_practitioner_name(practitioner: Practitioner) -> str:
    """Extract practitioner name"""
    return practitioner.get_full_name()


def build_database_context() -> str:
    """
    Build comprehensive context about current database state for AI assistant.
    """
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Basic counts
    total_patients = Patient.objects.count()
    active_patients = Patient.objects.filter(active=True).count()
    total_practitioners = Practitioner.objects.count()
    active_practitioners = Practitioner.objects.filter(active=True).count()

    # Appointment statistics
    total_appointments = Appointment.objects.count()
    recent_appointments_7d = Appointment.objects.filter(created__gte=seven_days_ago).count()
    recent_appointments_30d = Appointment.objects.filter(created__gte=thirty_days_ago).count()
    upcoming_appointments = Appointment.objects.filter(
        start__gte=timezone.now(),
        status__in=['proposed', 'pending', 'booked']
    ).count()

    # Prescription statistics
    total_prescriptions = Prescription.objects.count()
    recent_prescriptions_7d = Prescription.objects.filter(authored_on__gte=seven_days_ago).count()
    recent_prescriptions_30d = Prescription.objects.filter(authored_on__gte=thirty_days_ago).count()
    active_prescriptions = Prescription.objects.filter(status='active').count()

    # Billing statistics
    total_invoices = Invoice.objects.count()
    pending_payments = Invoice.objects.filter(Q(status='issued') | Q(status='balanced')).count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    cancelled_invoices = Invoice.objects.filter(status='cancelled').count()

    # Clinical records
    total_clinical_records = ClinicalRecord.objects.count()
    recent_records_7d = ClinicalRecord.objects.filter(created_at__gte=seven_days_ago).count()

    # Most active data
    top_specialties = Appointment.objects.values('practitioner__specialization').annotate(
        count=Count('id')
    ).order_by('-count')[:3]

    top_medications = Prescription.objects.filter(
        authored_on__gte=thirty_days_ago
    ).values('medication_name').annotate(
        count=Count('id')
    ).order_by('-count')[:3]

    context = f"""
DATABASE STATISTICS (as of {timezone.now().strftime('%Y-%m-%d %H:%M')}):

PATIENTS:
- Total patients: {total_patients}
- Active patients: {active_patients}
- Inactive patients: {total_patients - active_patients}

PRACTITIONERS:
- Total practitioners: {total_practitioners}
- Active practitioners: {active_practitioners}
- Inactive practitioners: {total_practitioners - active_practitioners}

APPOINTMENTS:
- Total appointments: {total_appointments}
- Last 7 days: {recent_appointments_7d}
- Last 30 days: {recent_appointments_30d}
- Upcoming scheduled: {upcoming_appointments}

PRESCRIPTIONS (MedicationRequests):
- Total prescriptions: {total_prescriptions}
- Last 7 days: {recent_prescriptions_7d}
- Last 30 days: {recent_prescriptions_30d}
- Active prescriptions: {active_prescriptions}

BILLING (Invoices):
- Total invoices: {total_invoices}
- Pending payments: {pending_payments}
- Paid invoices: {paid_invoices}
- Cancelled invoices: {cancelled_invoices}

CLINICAL RECORDS:
- Total clinical records: {total_clinical_records}
- Last 7 days: {recent_records_7d}

TOP SPECIALTIES (by appointment count):
"""

    for i, specialty in enumerate(top_specialties, 1):
        spec_name = specialty['practitioner__specialization'] or 'General Practice'
        spec_count = specialty['count']
        context += f"{i}. {spec_name}: {spec_count} appointments\n"

    if not top_specialties:
        context += "No specialty data available\n"

    context += "\nTOP MEDICATIONS (last 30 days):\n"

    for i, med in enumerate(top_medications, 1):
        med_name = med['medication_name']
        med_count = med['count']
        context += f"{i}. {med_name}: {med_count} prescriptions\n"

    if not top_medications:
        context += "No medication data available\n"

    return context.strip()
