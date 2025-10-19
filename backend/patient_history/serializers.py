"""
Serializers for Clinical Records (Patient History).
"""
from rest_framework import serializers
from .models import ClinicalRecord
from datetime import datetime

class ClinicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalRecord
        fields = '__all__'
        read_only_fields = ['id', 'recorded_date', 'updated_at', 'patient_name', 'recorded_by_name']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None

    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None


class FHIRClinicalRecordSerializer(serializers.ModelSerializer):
    """
    FHIR R4 Observation serializer for clinical records.
    Converts Django ClinicalRecord model to FHIR Observation format.
    """

    class Meta:
        model = ClinicalRecord
        fields = '__all__'

    def to_representation(self, instance):
        """
        Convert Django ClinicalRecord to FHIR Observation format.
        """
        # Build base FHIR Observation resource
        fhir_data = {
            'resourceType': 'Observation',
            'id': str(instance.id),
            'status': instance.status or 'final',
            'code': {
                'coding': [
                    {
                        'system': 'http://loinc.org',
                        'code': instance.code or 'unknown',
                        'display': instance.title or 'Clinical Observation'
                    }
                ],
                'text': instance.title or 'Clinical Observation'
            },
            'subject': {
                'reference': f'Patient/{instance.patient.id}',
                'display': instance.patient.get_full_name()
            },
            'effectiveDateTime': instance.recorded_date.isoformat() if instance.recorded_date else None,
            'performer': [
                {
                    'reference': f'Practitioner/{instance.recorded_by.id}',
                    'display': instance.recorded_by.get_full_name()
                }
            ] if instance.recorded_by else [],
            'meta': {
                'lastUpdated': instance.updated_at.isoformat() if instance.updated_at else None
            }
        }

        # Add category if record_type is present
        if instance.record_type:
            fhir_data['category'] = [
                {
                    'coding': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                            'code': instance.record_type.lower(),
                            'display': instance.record_type
                        }
                    ]
                }
            ]

        # Initialize notes array
        notes_list = []

        # Add value if present
        if instance.value_quantity is not None:
            try:
                # Try to convert to float for numeric values
                value = float(instance.value_quantity)
                fhir_data['valueQuantity'] = {
                    'value': value,
                    'unit': instance.value_unit or ''
                }
            except (ValueError, TypeError):
                # If not numeric, store as string in note
                if instance.value_quantity:
                    value_text = f"{instance.value_quantity}"
                    if instance.value_unit:
                        value_text += f" {instance.value_unit}"
                    notes_list.append({'text': f"Value: {value_text}"})

        # Add notes as text
        if instance.notes:
            notes_list.append({'text': instance.notes})

        # Add notes to FHIR data if any exist
        if notes_list:
            fhir_data['note'] = notes_list

        # Add severity as interpretation
        if instance.severity:
            fhir_data['interpretation'] = [
                {
                    'coding': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
                            'code': instance.severity.upper(),
                            'display': instance.severity.capitalize()
                        }
                    ]
                }
            ]

        # Add body site if present
        if instance.body_site:
            fhir_data['bodySite'] = {
                'text': instance.body_site
            }

        return fhir_data

    def to_internal_value(self, data):
        """
        Convert FHIR Observation to Django ClinicalRecord format.
        """
        # Extract patient reference
        subject = data.get('subject', {})
        patient_id = None
        if subject.get('reference'):
            patient_ref = subject['reference'].split('/')[-1]
            try:
                patient_id = int(patient_ref)
            except ValueError:
                raise serializers.ValidationError({'subject': 'Invalid patient reference'})

        # Extract performer reference
        performer_id = None
        performers = data.get('performer', [])
        if performers and len(performers) > 0:
            performer_ref = performers[0].get('reference', '').split('/')[-1]
            try:
                performer_id = int(performer_ref)
            except ValueError:
                raise serializers.ValidationError({'performer': 'Invalid performer reference'})

        # Extract code
        code_obj = data.get('code', {})
        code_text = code_obj.get('text', '')
        code_value = None
        if code_obj.get('coding') and len(code_obj['coding']) > 0:
            code_value = code_obj['coding'][0].get('code')

        # Extract value quantity
        value_quantity = None
        value_unit = None
        if 'valueQuantity' in data:
            value_quantity = data['valueQuantity'].get('value')
            value_unit = data['valueQuantity'].get('unit')

        # Extract category
        record_type = None
        categories = data.get('category', [])
        if categories and len(categories) > 0:
            category_coding = categories[0].get('coding', [])
            if category_coding and len(category_coding) > 0:
                record_type = category_coding[0].get('display')

        # Extract notes
        notes = None
        note_list = data.get('note', [])
        if note_list and len(note_list) > 0:
            notes = note_list[0].get('text')

        # Extract severity from interpretation
        severity = None
        interpretations = data.get('interpretation', [])
        if interpretations and len(interpretations) > 0:
            interp_coding = interpretations[0].get('coding', [])
            if interp_coding and len(interp_coding) > 0:
                severity = interp_coding[0].get('display', '').lower()

        # Extract body site
        body_site = None
        if 'bodySite' in data:
            body_site = data['bodySite'].get('text')

        # Build internal format
        internal_data = {
            'patient': patient_id,
            'recorded_by': performer_id,
            'status': data.get('status', 'final'),
            'title': code_text,
            'code': code_value,
            'record_type': record_type,
            'value_quantity': value_quantity,
            'value_unit': value_unit,
            'notes': notes,
            'severity': severity,
            'body_site': body_site,
        }

        # Extract effective date
        if 'effectiveDateTime' in data:
            try:
                effective_dt = datetime.fromisoformat(data['effectiveDateTime'].replace('Z', '+00:00'))
                internal_data['recorded_date'] = effective_dt.date()
            except (ValueError, AttributeError):
                pass

        # Remove None values
        internal_data = {k: v for k, v in internal_data.items() if v is not None}

        return internal_data
