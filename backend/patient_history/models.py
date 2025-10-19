"""
Patient History (Clinical Record) models.

Combines FHIR Condition and Observation concepts for tracking
patient medical history, diagnoses, and clinical observations.
"""

import uuid
from django.db import models
from patients.models import Patient
from practitioners.models import Practitioner


class ClinicalRecord(models.Model):
    """
    Clinical Record model for tracking patient medical history.

    Combines aspects of FHIR Condition and Observation resources.
    """

    # Record type choices
    RECORD_TYPE_CHOICES = [
        ('condition', 'Condition/Diagnosis'),
        ('observation', 'Clinical Observation'),
        ('allergy', 'Allergy'),
        ('procedure', 'Procedure'),
        ('family-history', 'Family History'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('recurrence', 'Recurrence'),
        ('relapse', 'Relapse'),
        ('inactive', 'Inactive'),
        ('remission', 'Remission'),
        ('resolved', 'Resolved'),
    ]

    # Severity choices
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life-threatening', 'Life Threatening'),
    ]

    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Patient and Practitioner
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='clinical_records',
        help_text='Patient this record belongs to'
    )
    recorded_by = models.ForeignKey(
        Practitioner,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_clinical_records',
        help_text='Practitioner who recorded this'
    )

    # Condition/Observation details
    title = models.CharField(
        max_length=500,
        help_text='Title or name of the condition/observation'
    )
    code = models.CharField(
        max_length=100,
        blank=True,
        help_text='Medical code (ICD-10, SNOMED, LOINC)'
    )
    category = models.CharField(
        max_length=200,
        blank=True,
        help_text='Category (e.g., vital-signs, laboratory, imaging)'
    )

    # Clinical details
    description = models.TextField(
        blank=True,
        help_text='Detailed description'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        blank=True,
        help_text='Severity of condition'
    )
    body_site = models.CharField(
        max_length=200,
        blank=True,
        help_text='Body site affected'
    )

    # Value (for observations)
    value_quantity = models.CharField(
        max_length=100,
        blank=True,
        help_text='Measured value (e.g., 120/80, 98.6°F)'
    )
    value_unit = models.CharField(
        max_length=50,
        blank=True,
        help_text='Unit of measurement'
    )

    # Timing
    onset_date = models.DateField(
        null=True,
        blank=True,
        help_text='When condition started'
    )
    resolution_date = models.DateField(
        null=True,
        blank=True,
        help_text='When condition resolved'
    )
    recorded_date = models.DateTimeField(
        auto_now_add=True,
        help_text='When this record was created'
    )

    # Additional information
    notes = models.TextField(
        blank=True,
        help_text='Additional clinical notes'
    )

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-recorded_date']
        indexes = [
            models.Index(fields=['patient', '-recorded_date']),
            models.Index(fields=['record_type', 'status']),
        ]
        verbose_name = 'Clinical Record'
        verbose_name_plural = 'Clinical Records'

    def __str__(self):
        """String representation."""
        return f"{self.get_record_type_display()}: {self.title} - {self.patient.get_full_name()}"

    def is_active(self):
        """Check if record is currently active."""
        return self.status in ['active', 'recurrence', 'relapse']
