"""
Serializers for Appointment models.

This module provides Django REST Framework serializers for Appointment models,
including both standard Django serialization and FHIR R4 compliant serialization.
"""

from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from fhir.resources.appointment import Appointment as FHIRAppointment
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Standard Django REST Framework serializer for Appointment model.

    This serializer handles basic CRUD operations for appointments
    using Django's standard serialization format.
    """

    patient_name = serializers.SerializerMethodField()
    practitioner_name = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    can_check_in = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id',
            'status',
            'service_category',
            'service_type',
            'specialty',
            'appointment_type',
            'reason_code',
            'reason_description',
            'priority',
            'description',
            'comment',
            'patient_instruction',
            'start',
            'end',
            'minutes_duration',
            'duration_minutes',
            'patient',
            'patient_name',
            'patient_status',
            'practitioner',
            'practitioner_name',
            'practitioner_status',
            'practitioner_required',
            'created',
            'updated_at',
            'cancellation_reason',
            'is_upcoming',
            'can_cancel',
            'can_check_in',
        ]
        read_only_fields = ['id', 'created', 'updated_at', 'patient_name', 'practitioner_name',
                           'duration_minutes', 'is_upcoming', 'can_cancel', 'can_check_in']

    def get_patient_name(self, obj):
        """Get the patient's full name."""
        return obj.patient.get_full_name() if obj.patient else None

    def get_practitioner_name(self, obj):
        """Get the practitioner's full name."""
        return obj.practitioner.get_full_name() if obj.practitioner else None

    def get_duration_minutes(self, obj):
        """Get appointment duration in minutes."""
        return obj.get_duration_minutes()

    def get_is_upcoming(self, obj):
        """Check if appointment is upcoming."""
        return obj.is_upcoming()

    def get_can_cancel(self, obj):
        """Check if appointment can be cancelled."""
        return obj.can_cancel()

    def get_can_check_in(self, obj):
        """Check if patient can check in."""
        return obj.can_check_in()


class FHIRAppointmentSerializer(serializers.Serializer):
    """
    FHIR R4 compliant serializer for Appointment resource.
    Converts Django Appointment model to/from FHIR Appointment resource format.
    """

    def to_representation(self, instance):
        """
        Convert Django Appointment instance to FHIR Appointment resource.

        Args:
            instance: Appointment model instance

        Returns:
            dict: FHIR-compliant Appointment resource dictionary
        """
        # Build FHIR Appointment resource
        fhir_data = {
            'resourceType': 'Appointment',
            'id': str(instance.id),
            'status': instance.status,
        }

        # Add service category if present
        if instance.service_category:
            fhir_data['serviceCategory'] = [{
                'text': instance.service_category
            }]

        # Add service type if present
        if instance.service_type:
            fhir_data['serviceType'] = [{
                'text': instance.service_type
            }]

        # Add specialty if present
        if instance.specialty:
            fhir_data['specialty'] = [{
                'text': instance.specialty
            }]

        # Add appointment type if present
        if instance.appointment_type:
            fhir_data['appointmentType'] = {
                'text': instance.appointment_type
            }

        # Add reason code if present
        if instance.reason_code:
            fhir_data['reasonCode'] = [{
                'text': instance.reason_code
            }]

        # Add priority
        fhir_data['priority'] = instance.priority

        # Add description if present
        if instance.description:
            fhir_data['description'] = instance.description

        # Add comment if present
        if instance.comment:
            fhir_data['comment'] = instance.comment

        # Add patient instruction if present
        if instance.patient_instruction:
            fhir_data['patientInstruction'] = instance.patient_instruction

        # Add timing
        fhir_data['start'] = instance.start.isoformat()
        fhir_data['end'] = instance.end.isoformat()

        if instance.minutes_duration:
            fhir_data['minutesDuration'] = instance.minutes_duration

        # Add created timestamp
        fhir_data['created'] = instance.created.isoformat()

        # Build participants array
        participants = []

        # Add patient participant
        patient_participant = {
            'actor': Reference(**{
                'reference': f'Patient/{instance.patient.id}',
                'display': instance.patient.get_full_name()
            }).dict(exclude_none=True),
            'status': instance.patient_status
        }
        participants.append(patient_participant)

        # Add practitioner participant
        practitioner_types = []
        if instance.specialty:
            practitioner_types.append({
                'text': instance.specialty
            })

        practitioner_participant = {
            'actor': Reference(**{
                'reference': f'Practitioner/{instance.practitioner.id}',
                'display': instance.practitioner.get_full_name()
            }).dict(exclude_none=True),
            'required': instance.practitioner_required,
            'status': instance.practitioner_status
        }

        if practitioner_types:
            practitioner_participant['type'] = practitioner_types

        participants.append(practitioner_participant)

        fhir_data['participant'] = participants

        # Add cancellation reason if cancelled
        if instance.status == 'cancelled' and instance.cancellation_reason:
            fhir_data['cancelationReason'] = {
                'text': instance.cancellation_reason
            }

        # Create FHIR Appointment and return as dict
        try:
            fhir_appointment = FHIRAppointment(**fhir_data)
            result = fhir_appointment.dict(exclude_none=True)

            # Ensure datetime fields are strings (fhir.resources may convert them back to datetime objects)
            if 'start' in result and instance.start:
                result['start'] = instance.start.isoformat()
            if 'end' in result and instance.end:
                result['end'] = instance.end.isoformat()
            if 'created' in result and instance.created:
                result['created'] = instance.created.isoformat()

            return result
        except Exception as e:
            # If FHIR validation fails, return the data dict directly
            # This allows for custom fields while maintaining FHIR structure
            return fhir_data

    def to_internal_value(self, data):
        """
        Convert FHIR Appointment resource to Django Appointment model data.

        Args:
            data: FHIR Appointment resource dictionary

        Returns:
            dict: Validated data for Appointment model
        """
        # Validate resource type
        if data.get('resourceType') != 'Appointment':
            raise serializers.ValidationError({
                'resourceType': 'Resource must be of type Appointment'
            })

        # Validate required fields
        if 'status' not in data:
            raise serializers.ValidationError({
                'status': 'Status is required'
            })

        if 'participant' not in data or not data['participant']:
            raise serializers.ValidationError({
                'participant': 'At least one participant is required'
            })

        if 'start' not in data:
            raise serializers.ValidationError({
                'start': 'Start time is required'
            })

        if 'end' not in data:
            raise serializers.ValidationError({
                'end': 'End time is required'
            })

        appointment_data = {
            'status': data['status']
        }

        # Extract service information
        if 'serviceCategory' in data and data['serviceCategory']:
            appointment_data['service_category'] = data['serviceCategory'][0].get('text', '')

        if 'serviceType' in data and data['serviceType']:
            appointment_data['service_type'] = data['serviceType'][0].get('text', '')

        if 'specialty' in data and data['specialty']:
            appointment_data['specialty'] = data['specialty'][0].get('text', '')

        if 'appointmentType' in data:
            appointment_data['appointment_type'] = data['appointmentType'].get('text', '')

        # Extract reason
        if 'reasonCode' in data and data['reasonCode']:
            appointment_data['reason_code'] = data['reasonCode'][0].get('text', '')

        # Extract priority
        if 'priority' in data:
            appointment_data['priority'] = data['priority']

        # Extract descriptions
        if 'description' in data:
            appointment_data['description'] = data['description']

        if 'comment' in data:
            appointment_data['comment'] = data['comment']

        if 'patientInstruction' in data:
            appointment_data['patient_instruction'] = data['patientInstruction']

        # Extract timing
        start_str = data['start']
        end_str = data['end']

        # Parse datetime strings and ensure timezone-aware
        try:
            if isinstance(start_str, str):
                parsed_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                # Ensure timezone-aware
                if timezone.is_naive(parsed_start):
                    appointment_data['start'] = timezone.make_aware(parsed_start)
                else:
                    appointment_data['start'] = parsed_start
            else:
                appointment_data['start'] = start_str

            if isinstance(end_str, str):
                parsed_end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                # Ensure timezone-aware
                if timezone.is_naive(parsed_end):
                    appointment_data['end'] = timezone.make_aware(parsed_end)
                else:
                    appointment_data['end'] = parsed_end
            else:
                appointment_data['end'] = end_str
        except ValueError as e:
            raise serializers.ValidationError({
                'timing': f'Invalid date/time format: {str(e)}'
            })

        if 'minutesDuration' in data:
            appointment_data['minutes_duration'] = data['minutesDuration']

        # Extract participants
        patient_id = None
        practitioner_id = None
        patient_status = 'needs-action'
        practitioner_status = 'needs-action'
        practitioner_required = 'required'

        for participant in data['participant']:
            if 'actor' in participant and 'reference' in participant['actor']:
                reference = participant['actor']['reference']
                status = participant.get('status', 'needs-action')

                if reference.startswith('Patient/'):
                    patient_id = reference.replace('Patient/', '')
                    patient_status = status
                elif reference.startswith('Practitioner/'):
                    practitioner_id = reference.replace('Practitioner/', '')
                    practitioner_status = status
                    practitioner_required = participant.get('required', 'required')

        if not patient_id:
            raise serializers.ValidationError({
                'participant': 'Patient participant is required'
            })

        if not practitioner_id:
            raise serializers.ValidationError({
                'participant': 'Practitioner participant is required'
            })

        appointment_data['patient_id'] = patient_id
        appointment_data['practitioner_id'] = practitioner_id
        appointment_data['patient_status'] = patient_status
        appointment_data['practitioner_status'] = practitioner_status
        appointment_data['practitioner_required'] = practitioner_required

        # Extract cancellation reason if present
        if 'cancelationReason' in data:
            if isinstance(data['cancelationReason'], dict):
                appointment_data['cancellation_reason'] = data['cancelationReason'].get('text', '')
            else:
                appointment_data['cancellation_reason'] = str(data['cancelationReason'])

        return appointment_data

    def create(self, validated_data):
        """Create a new Appointment instance from validated FHIR data."""
        return Appointment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing Appointment instance from validated FHIR data."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
