"""
Application Layer: Data provider for fetching report data.
Implements IReportDataProvider interface.
"""
from typing import Any, Dict, List
from datetime import datetime
from django.db.models import Q

from .interfaces import IReportDataProvider
from patients.models import Patient
from practitioners.models import Practitioner
from appointments.models import Appointment
from prescriptions.models import Prescription
from billing.models import Invoice
from patient_history.models import ClinicalRecord


class DjangoReportDataProvider(IReportDataProvider):
    """
    Concrete implementation of data provider using Django ORM.
    Fetches data from database models.
    """

    def get_data(self, report_type: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data for report based on type and filters.

        Args:
            report_type: Type of report (patients, appointments, etc.)
            filters: Filtering parameters

        Returns:
            List of data records as dictionaries
        """
        data_fetcher = {
            'patients': self._get_patients_data,
            'practitioners': self._get_practitioners_data,
            'appointments': self._get_appointments_data,
            'prescriptions': self._get_prescriptions_data,
            'invoices': self._get_invoices_data,
            'clinical_records': self._get_clinical_records_data,
        }

        fetcher = data_fetcher.get(report_type)
        if not fetcher:
            raise ValueError(f"Unsupported report type: {report_type}")

        return fetcher(filters)

    def get_field_definitions(self, report_type: str) -> List[Dict[str, str]]:
        """Get field definitions for report type."""
        definitions = {
            'patients': [
                {'name': 'id', 'label': 'ID', 'type': 'string'},
                {'name': 'full_name', 'label': 'Full Name', 'type': 'string'},
                {'name': 'gender', 'label': 'Gender', 'type': 'string'},
                {'name': 'birth_date', 'label': 'Birth Date', 'type': 'date'},
                {'name': 'email', 'label': 'Email', 'type': 'string'},
                {'name': 'phone', 'label': 'Phone', 'type': 'string'},
                {'name': 'active', 'label': 'Status', 'type': 'boolean'},
            ],
            'practitioners': [
                {'name': 'id', 'label': 'ID', 'type': 'string'},
                {'name': 'full_name', 'label': 'Full Name', 'type': 'string'},
                {'name': 'specialization', 'label': 'Specialization', 'type': 'string'},
                {'name': 'email', 'label': 'Email', 'type': 'string'},
                {'name': 'phone', 'label': 'Phone', 'type': 'string'},
                {'name': 'active', 'label': 'Status', 'type': 'boolean'},
            ],
            'appointments': [
                {'name': 'id', 'label': 'ID', 'type': 'string'},
                {'name': 'patient_name', 'label': 'Patient', 'type': 'string'},
                {'name': 'practitioner_name', 'label': 'Practitioner', 'type': 'string'},
                {'name': 'start', 'label': 'Start Time', 'type': 'datetime'},
                {'name': 'status', 'label': 'Status', 'type': 'string'},
                {'name': 'reason_code', 'label': 'Reason', 'type': 'string'},
            ],
        }
        return definitions.get(report_type, [])

    def _get_patients_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch patients data with filters."""
        queryset = Patient.objects.all()

        # Apply filters
        if filters.get('active') is not None:
            queryset = queryset.filter(active=filters['active'])

        if filters.get('gender'):
            queryset = queryset.filter(gender=filters['gender'])

        # Date range filtering
        if filters.get('created_from'):
            queryset = queryset.filter(created_at__gte=filters['created_from'])
        if filters.get('created_to'):
            queryset = queryset.filter(created_at__lte=filters['created_to'])

        # Convert to list of dicts
        data = []
        for patient in queryset:
            data.append({
                'id': str(patient.id),
                'full_name': patient.get_full_name(),
                'gender': patient.gender,
                'birth_date': patient.birth_date.isoformat() if patient.birth_date else '',
                'email': patient.email or '',
                'phone': patient.phone or '',
                'active': 'Active' if patient.active else 'Inactive',
                'created_at': patient.created_at.isoformat() if patient.created_at else '',
            })

        return data

    def _get_practitioners_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch practitioners data with filters."""
        queryset = Practitioner.objects.all()

        # Apply filters
        if filters.get('active') is not None:
            queryset = queryset.filter(active=filters['active'])

        if filters.get('specialization'):
            queryset = queryset.filter(specialization__icontains=filters['specialization'])

        # Convert to list of dicts
        data = []
        for practitioner in queryset:
            data.append({
                'id': str(practitioner.id),
                'full_name': practitioner.get_full_name(),
                'specialization': practitioner.specialization or '',
                'email': practitioner.email or '',
                'phone': practitioner.phone or '',
                'active': 'Active' if practitioner.active else 'Inactive',
            })

        return data

    def _get_appointments_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch appointments data with filters."""
        queryset = Appointment.objects.select_related('patient', 'practitioner').all()

        # Apply filters
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        if filters.get('start_date'):
            queryset = queryset.filter(start__gte=filters['start_date'])

        if filters.get('end_date'):
            queryset = queryset.filter(start__lte=filters['end_date'])

        if filters.get('patient_id'):
            queryset = queryset.filter(patient_id=filters['patient_id'])

        if filters.get('practitioner_id'):
            queryset = queryset.filter(practitioner_id=filters['practitioner_id'])

        # Convert to list of dicts
        data = []
        for appointment in queryset:
            data.append({
                'id': str(appointment.id),
                'patient_name': appointment.patient.get_full_name() if appointment.patient else 'Unknown',
                'practitioner_name': appointment.practitioner.get_full_name() if appointment.practitioner else 'Unknown',
                'start': appointment.start.isoformat() if appointment.start else '',
                'end': appointment.end.isoformat() if appointment.end else '',
                'duration': f"{appointment.minutes_duration} min" if appointment.minutes_duration else '',
                'status': appointment.status,
                'reason_code': appointment.reason_code or '',
            })

        return data

    def _get_prescriptions_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch prescriptions data with filters."""
        queryset = Prescription.objects.select_related('patient', 'prescriber').all()

        # Apply filters
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        if filters.get('patient_id'):
            queryset = queryset.filter(patient_id=filters['patient_id'])

        if filters.get('practitioner_id'):
            queryset = queryset.filter(prescriber_id=filters['practitioner_id'])

        # Convert to list of dictionaries
        data = []
        for prescription in queryset:
            data.append({
                'id': str(prescription.id),
                'medication': prescription.medication_name or '',
                'patient_name': prescription.patient.get_full_name() if prescription.patient else 'Unknown',
                'prescriber_name': prescription.prescriber.get_full_name() if prescription.prescriber else 'Unknown',
                'status': prescription.status,
                'dosage': prescription.dosage_text or '',
                'authored_on': prescription.authored_on.isoformat() if prescription.authored_on else '',
            })

        return data

    def _get_invoices_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch invoices data with filters."""
        queryset = Invoice.objects.select_related('patient').all()

        # Apply filters
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        if filters.get('patient_id'):
            queryset = queryset.filter(patient_id=filters['patient_id'])

        # Convert to list of dicts
        data = []
        for invoice in queryset:
            data.append({
                'id': str(invoice.id),
                'patient_name': invoice.patient.get_full_name() if invoice.patient else 'Unknown',
                'total_amount': str(invoice.total_gross) if invoice.total_gross else '0',
                'status': invoice.status,
                'issue_date': invoice.issue_date.isoformat() if invoice.issue_date else '',
            })

        return data

    def _get_clinical_records_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch clinical records data with filters."""
        queryset = ClinicalRecord.objects.select_related('patient').all()

        # Apply filters
        if filters.get('patient_id'):
            queryset = queryset.filter(patient_id=filters['patient_id'])

        if filters.get('record_type'):
            queryset = queryset.filter(record_type=filters['record_type'])

        # Convert to list of dicts
        data = []
        for record in queryset:
            data.append({
                'id': str(record.id),
                'patient_name': record.patient.get_full_name() if record.patient else 'Unknown',
                'record_type': record.record_type or '',
                'recorded_date': record.recorded_date.isoformat() if record.recorded_date else '',
                'title': record.title or '',
                'status': record.status or '',
            })

        return data
