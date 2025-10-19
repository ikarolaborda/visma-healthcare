"""
Serializers for Prescription (MedicationRequest) models.
"""

from rest_framework import serializers
from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Django REST Framework serializer for Prescription model.
    """

    patient_name = serializers.SerializerMethodField()
    prescriber_name = serializers.SerializerMethodField()
    full_dosage_instructions = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            'id',
            'status',
            'intent',
            'priority',
            'medication_name',
            'medication_code',
            'medication_form',
            'strength',
            'patient',
            'patient_name',
            'prescriber',
            'prescriber_name',
            'dosage_text',
            'dosage_route',
            'dosage_frequency',
            'dose_quantity',
            'quantity',
            'quantity_unit',
            'refills',
            'dispense_interval_days',
            'authored_on',
            'validity_start',
            'validity_end',
            'reason',
            'notes',
            'updated_at',
            'full_dosage_instructions',
        ]
        read_only_fields = ['id', 'authored_on', 'updated_at', 'patient_name', 'prescriber_name', 'full_dosage_instructions']

    def get_patient_name(self, obj):
        """Get the patient's full name."""
        return obj.patient.get_full_name() if obj.patient else None

    def get_prescriber_name(self, obj):
        """Get the prescriber's full name."""
        return obj.prescriber.get_full_name() if obj.prescriber else None

    def get_full_dosage_instructions(self, obj):
        """Get comprehensive dosage instructions."""
        return obj.get_full_dosage_instructions()
