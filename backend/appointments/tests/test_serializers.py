"""
Tests for Appointment serializers.
"""
import pytest
from rest_framework.exceptions import ValidationError
from appointments.serializers import AppointmentSerializer, FHIRAppointmentSerializer


@pytest.mark.django_db
class TestAppointmentSerializer:
    """Test standard Appointment serializer."""

    def test_serialize_appointment(self, sample_appointment):
        """Test serializing an appointment."""
        serializer = AppointmentSerializer(sample_appointment)
        data = serializer.data
        
        assert data['id'] == str(sample_appointment.id)
        assert data['status'] == sample_appointment.status
        assert data['patient_name'] == sample_appointment.patient.get_full_name()
        assert data['practitioner_name'] == sample_appointment.practitioner.get_full_name()
        assert data['duration_minutes'] == 60

    def test_computed_fields(self, sample_appointment):
        """Test computed fields in serializer."""
        serializer = AppointmentSerializer(sample_appointment)
        data = serializer.data
        
        assert 'is_upcoming' in data
        assert 'can_cancel' in data
        assert 'can_check_in' in data
        assert isinstance(data['is_upcoming'], bool)


@pytest.mark.django_db
class TestFHIRAppointmentSerializer:
    """Test FHIR Appointment serializer."""

    def test_to_representation(self, sample_appointment):
        """Test converting Django appointment to FHIR format."""
        serializer = FHIRAppointmentSerializer(sample_appointment)
        data = serializer.data
        
        assert data['resourceType'] == 'Appointment'
        assert data['id'] == str(sample_appointment.id)
        assert data['status'] == sample_appointment.status
        assert 'participant' in data
        assert len(data['participant']) == 2  # Patient and practitioner

    def test_to_representation_participants(self, sample_appointment):
        """Test participant structure in FHIR format."""
        serializer = FHIRAppointmentSerializer(sample_appointment)
        data = serializer.data
        
        participants = data['participant']
        patient_participant = next(p for p in participants if 'Patient' in p['actor']['reference'])
        practitioner_participant = next(p for p in participants if 'Practitioner' in p['actor']['reference'])
        
        assert f'Patient/{sample_appointment.patient.id}' in patient_participant['actor']['reference']
        assert f'Practitioner/{sample_appointment.practitioner.id}' in practitioner_participant['actor']['reference']

    def test_to_internal_value(self, fhir_appointment_data):
        """Test converting FHIR format to Django data."""
        serializer = FHIRAppointmentSerializer()
        internal_data = serializer.to_internal_value(fhir_appointment_data)
        
        assert internal_data['status'] == 'proposed'
        assert 'patient_id' in internal_data
        assert 'practitioner_id' in internal_data
        assert 'start' in internal_data
        assert 'end' in internal_data

    def test_to_internal_value_invalid_resource_type(self, fhir_appointment_data):
        """Test validation fails for invalid resource type."""
        fhir_appointment_data['resourceType'] = 'Patient'
        serializer = FHIRAppointmentSerializer()
        
        with pytest.raises(ValidationError, match='Resource must be of type Appointment'):
            serializer.to_internal_value(fhir_appointment_data)

    def test_to_internal_value_missing_status(self, fhir_appointment_data):
        """Test validation fails when status is missing."""
        del fhir_appointment_data['status']
        serializer = FHIRAppointmentSerializer()
        
        with pytest.raises(ValidationError, match='Status is required'):
            serializer.to_internal_value(fhir_appointment_data)

    def test_to_internal_value_missing_participant(self, fhir_appointment_data):
        """Test validation fails when participants are missing."""
        del fhir_appointment_data['participant']
        serializer = FHIRAppointmentSerializer()
        
        with pytest.raises(ValidationError, match='At least one participant is required'):
            serializer.to_internal_value(fhir_appointment_data)

    def test_to_internal_value_missing_patient(self, fhir_appointment_data):
        """Test validation fails when patient participant is missing."""
        # Remove patient participant
        fhir_appointment_data['participant'] = [
            p for p in fhir_appointment_data['participant']
            if 'Practitioner' in p['actor']['reference']
        ]
        serializer = FHIRAppointmentSerializer()
        
        with pytest.raises(ValidationError, match='Patient participant is required'):
            serializer.to_internal_value(fhir_appointment_data)

    def test_create_from_fhir(self, fhir_appointment_data):
        """Test creating appointment from FHIR data."""
        serializer = FHIRAppointmentSerializer(data=fhir_appointment_data)
        assert serializer.is_valid(raise_exception=True)
        
        appointment = serializer.save()
        assert appointment.id is not None
        assert appointment.status == 'proposed'

    def test_service_fields_extraction(self, fhir_appointment_data):
        """Test extracting service information from FHIR data."""
        serializer = FHIRAppointmentSerializer()
        internal_data = serializer.to_internal_value(fhir_appointment_data)
        
        assert internal_data['service_category'] == 'General Medicine'
        assert internal_data['service_type'] == 'Consultation'
        assert internal_data['specialty'] == 'General Practice'
        assert internal_data['appointment_type'] == 'Routine'

    def test_cancellation_reason(self, sample_appointment):
        """Test cancellation reason in FHIR format."""
        sample_appointment.status = 'cancelled'
        sample_appointment.cancellation_reason = 'Patient requested cancellation'
        sample_appointment.save()
        
        serializer = FHIRAppointmentSerializer(sample_appointment)
        data = serializer.data
        
        assert 'cancelationReason' in data
        assert data['cancelationReason']['text'] == 'Patient requested cancellation'
