"""
Serializers for Invoices (Billing).
"""
from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance_due', 'patient_name', 'is_paid', 'is_overdue']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None

    def get_is_paid(self, obj):
        return obj.is_paid()

    def get_is_overdue(self, obj):
        return obj.is_overdue()
