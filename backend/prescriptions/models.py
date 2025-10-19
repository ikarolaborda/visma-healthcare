"""
Prescription (MedicationRequest) models.

FHIR R4-compliant MedicationRequest resource implementation for managing
medication prescriptions.
"""

import uuid
from django.db import models
from patients.models import Patient
from practitioners.models import Practitioner


class Prescription(models.Model):
    """
    Prescription model conforming to FHIR MedicationRequest resource structure.

    Represents an order or request for both supply of the medication and the
    instructions for administration of the medication to a patient.

    FHIR R4 Reference: https://hl7.org/fhir/R4/medicationrequest.html
    """

    # Status choices based on FHIR MedicationRequestStatus value set
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on-hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('entered-in-error', 'Entered in Error'),
        ('stopped', 'Stopped'),
        ('draft', 'Draft'),
        ('unknown', 'Unknown'),
    ]

    # Intent choices
    INTENT_CHOICES = [
        ('proposal', 'Proposal'),
        ('plan', 'Plan'),
        ('order', 'Order'),
        ('original-order', 'Original Order'),
        ('reflex-order', 'Reflex Order'),
        ('filler-order', 'Filler Order'),
        ('instance-order', 'Instance Order'),
        ('option', 'Option'),
    ]

    # Priority choices
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('asap', 'ASAP'),
        ('stat', 'STAT'),
    ]

    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    intent = models.CharField(max_length=20, choices=INTENT_CHOICES, default='order')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='routine', blank=True)

    # Medication information
    medication_name = models.CharField(
        max_length=500,
        help_text='Name of the medication'
    )
    medication_code = models.CharField(
        max_length=100,
        blank=True,
        help_text='Code identifying the medication (e.g., RxNorm, SNOMED)'
    )
    medication_form = models.CharField(
        max_length=200,
        blank=True,
        help_text='Form of medication (e.g., tablet, capsule, liquid)'
    )
    strength = models.CharField(
        max_length=100,
        blank=True,
        help_text='Strength of medication (e.g., 500mg)'
    )

    # Participants
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        help_text='Patient for whom medication is prescribed'
    )
    prescriber = models.ForeignKey(
        Practitioner,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        help_text='Practitioner who prescribed the medication'
    )

    # Dosage instructions
    dosage_text = models.TextField(
        help_text='Free text dosage instructions',
        blank=True
    )
    dosage_route = models.CharField(
        max_length=200,
        blank=True,
        help_text='Route of administration (e.g., oral, IV)'
    )
    dosage_frequency = models.CharField(
        max_length=200,
        blank=True,
        help_text='Frequency of administration (e.g., twice daily, every 4 hours)'
    )
    dose_quantity = models.CharField(
        max_length=100,
        blank=True,
        help_text='Amount of medication per dose (e.g., 1 tablet, 5 mL)'
    )

    # Dispense request
    quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Amount to be dispensed'
    )
    quantity_unit = models.CharField(
        max_length=50,
        blank=True,
        help_text='Unit for quantity (e.g., tablets, mL, boxes)'
    )
    refills = models.PositiveIntegerField(
        default=0,
        help_text='Number of refills authorized'
    )
    dispense_interval_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Expected days supply per dispense'
    )

    # Timing
    authored_on = models.DateTimeField(
        auto_now_add=True,
        help_text='When prescription was initially written'
    )
    validity_start = models.DateField(
        blank=True,
        null=True,
        help_text='Start date of prescription validity'
    )
    validity_end = models.DateField(
        blank=True,
        null=True,
        help_text='End date of prescription validity'
    )

    # Additional information
    reason = models.TextField(
        blank=True,
        help_text='Reason or indication for prescription'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the prescription'
    )

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-authored_on']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['patient', '-authored_on']),
            models.Index(fields=['prescriber', '-authored_on']),
        ]
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'

    def __str__(self):
        """String representation of prescription."""
        return f"{self.medication_name} for {self.patient.get_full_name()} - {self.status}"

    def is_active(self):
        """Check if prescription is currently active."""
        from django.utils import timezone
        today = timezone.now().date()

        if self.status not in ['active', 'on-hold']:
            return False

        if self.validity_start and today < self.validity_start:
            return False

        if self.validity_end and today > self.validity_end:
            return False

        return True

    def can_refill(self):
        """Check if prescription can be refilled."""
        return self.status == 'active' and self.refills > 0

    def get_full_dosage_instructions(self):
        """Get comprehensive dosage instructions."""
        parts = []
        if self.dose_quantity:
            parts.append(self.dose_quantity)
        if self.dosage_route:
            parts.append(f"via {self.dosage_route}")
        if self.dosage_frequency:
            parts.append(self.dosage_frequency)

        full_instructions = ' '.join(parts) if parts else ''

        if self.dosage_text:
            full_instructions = f"{full_instructions}\n{self.dosage_text}" if full_instructions else self.dosage_text

        return full_instructions.strip()
