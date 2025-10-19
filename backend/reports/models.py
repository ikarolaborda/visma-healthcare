"""
Reports models for tracking generated reports.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Report(models.Model):
    """
    Model to track generated reports.
    Stores metadata and file path for generated reports.
    """

    # Report types
    TYPE_PATIENTS = 'patients'
    TYPE_PRACTITIONERS = 'practitioners'
    TYPE_APPOINTMENTS = 'appointments'
    TYPE_PRESCRIPTIONS = 'prescriptions'
    TYPE_INVOICES = 'invoices'
    TYPE_CLINICAL_RECORDS = 'clinical_records'

    REPORT_TYPE_CHOICES = [
        (TYPE_PATIENTS, 'Patients Report'),
        (TYPE_PRACTITIONERS, 'Practitioners Report'),
        (TYPE_APPOINTMENTS, 'Appointments Report'),
        (TYPE_PRESCRIPTIONS, 'Prescriptions Report'),
        (TYPE_INVOICES, 'Invoices Report'),
        (TYPE_CLINICAL_RECORDS, 'Clinical Records Report'),
    ]

    # Output formats
    FORMAT_PDF = 'pdf'
    FORMAT_CSV = 'csv'
    FORMAT_TXT = 'txt'
    FORMAT_JSON = 'json'

    FORMAT_CHOICES = [
        (FORMAT_PDF, 'PDF'),
        (FORMAT_CSV, 'CSV'),
        (FORMAT_TXT, 'Plain Text'),
        (FORMAT_JSON, 'JSON'),
    ]

    # Report statuses
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Report parameters stored as JSON
    filters = models.JSONField(default=dict, blank=True)

    # File storage
    file = models.FileField(
        upload_to='reports/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'csv', 'txt', 'json'])]
    )
    file_size = models.IntegerField(null=True, blank=True, help_text='File size in bytes')

    # Metadata
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    record_count = models.IntegerField(default=0, help_text='Number of records in report')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['report_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.format.upper()} ({self.status})"

    def get_filename(self):
        """Generate filename for the report."""
        if self.file:
            return self.file.name.split('/')[-1]
        timestamp = self.created_at.strftime('%Y%m%d_%H%M%S')
        return f"{self.report_type}_{timestamp}.{self.format}"

    def mark_processing(self):
        """Mark report as processing."""
        self.status = self.STATUS_PROCESSING
        self.save(update_fields=['status', 'updated_at'])

    def mark_completed(self, file_path, record_count):
        """Mark report as completed."""
        from django.utils import timezone
        self.status = self.STATUS_COMPLETED
        self.file = file_path
        self.record_count = record_count
        self.completed_at = timezone.now()
        if self.file:
            self.file_size = self.file.size
        self.save(update_fields=['status', 'file', 'record_count', 'completed_at', 'file_size', 'updated_at'])

    def mark_failed(self, error_message):
        """Mark report as failed."""
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
