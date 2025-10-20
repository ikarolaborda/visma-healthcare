"""
Serializers for Reports API.
"""
from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    filename = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'user',
            'user_email',
            'report_type',
            'report_type_display',
            'format',
            'format_display',
            'status',
            'status_display',
            'title',
            'description',
            'filters',
            'file',
            'file_size',
            'filename',
            'download_url',
            'record_count',
            'created_at',
            'updated_at',
            'completed_at',
            'error_message',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'file',
            'file_size',
            'filename',
            'record_count',
            'created_at',
            'updated_at',
            'completed_at',
            'error_message',
        ]

    def get_filename(self, obj):
        """Get report filename."""
        return obj.get_filename()

    def get_download_url(self, obj):
        """Get download URL if file exists."""
        if obj.file and obj.status == Report.STATUS_COMPLETED:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class ReportCreateSerializer(serializers.Serializer):
    """
    Serializer for creating reports with enhanced filter options.
    """
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPE_CHOICES)
    format = serializers.ChoiceField(choices=Report.FORMAT_CHOICES)
    title = serializers.CharField(required=False, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)

    # Enhanced filter fields
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    practitioner_id = serializers.UUIDField(required=False, allow_null=True)
    patient_id = serializers.UUIDField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True)
    billing_type = serializers.CharField(required=False, allow_blank=True)
    include_inactive = serializers.BooleanField(required=False, default=False)

    # Legacy filters field for backward compatibility
    filters = serializers.JSONField(required=False, default=dict)

    def validate_filters(self, value):
        """Validate filters structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filters must be a JSON object")
        return value

    def validate(self, attrs):
        """
        Combine individual filter fields into the filters dict.
        """
        # Build filters dict from individual fields
        filters = attrs.get('filters', {})

        if attrs.get('date_from'):
            filters['date_from'] = attrs['date_from'].isoformat()
        if attrs.get('date_to'):
            filters['date_to'] = attrs['date_to'].isoformat()
        if attrs.get('practitioner_id'):
            filters['practitioner_id'] = str(attrs['practitioner_id'])
        if attrs.get('patient_id'):
            filters['patient_id'] = str(attrs['patient_id'])
        if attrs.get('status'):
            filters['status'] = attrs['status']
        if attrs.get('billing_type'):
            filters['billing_type'] = attrs['billing_type']
        if 'include_inactive' in attrs:
            filters['include_inactive'] = attrs['include_inactive']

        attrs['filters'] = filters
        return attrs


class ReportFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering reports list.
    """
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPE_CHOICES, required=False)
    format = serializers.ChoiceField(choices=Report.FORMAT_CHOICES, required=False)
    status = serializers.ChoiceField(choices=Report.STATUS_CHOICES, required=False)
    created_from = serializers.DateTimeField(required=False)
    created_to = serializers.DateTimeField(required=False)
