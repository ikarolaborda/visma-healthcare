"""
Serializers for common models.
"""
from rest_framework import serializers
from .models import ClinicSettings


class ClinicSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for ClinicSettings model.
    """
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = ClinicSettings
        fields = [
            'id',
            'clinic_name',
            'clinic_address',
            'clinic_phone',
            'clinic_email',
            'clinic_website',
            'logo',
            'logo_url',
            'primary_color',
            'secondary_color',
            'report_header_text',
            'report_footer_text',
            'include_logo_in_reports',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_logo_url(self, obj):
        """Get full URL for logo if it exists."""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
