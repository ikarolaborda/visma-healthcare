"""
Serializers for Clinical Records (Patient History).
"""
from rest_framework import serializers
from .models import ClinicalRecord

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
