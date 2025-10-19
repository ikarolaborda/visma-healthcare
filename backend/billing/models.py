"""
Billing (Invoice) models.

FHIR R4-compliant Invoice resource implementation for managing
billing and invoicing for healthcare services.
"""

import uuid
from django.db import models
from decimal import Decimal
from patients.models import Patient
from appointments.models import Appointment


class Invoice(models.Model):
    """
    Invoice model conforming to FHIR Invoice resource structure.

    Represents a billing invoice for healthcare services rendered.

    FHIR R4 Reference: https://hl7.org/fhir/R4/invoice.html
    """

    # Status choices based on FHIR InvoiceStatus value set
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('balanced', 'Balanced'),
        ('cancelled', 'Cancelled'),
        ('entered-in-error', 'Entered in Error'),
    ]

    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        help_text='Unique invoice number'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Patient and related appointment
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text='Patient being billed'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text='Related appointment (if applicable)'
    )

    # Financial details
    total_net = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total amount before tax'
    )
    total_gross = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total amount including tax'
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Tax amount'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Amount already paid'
    )
    balance_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Remaining balance'
    )

    # Service details
    service_description = models.TextField(
        help_text='Description of services provided'
    )
    service_code = models.CharField(
        max_length=100,
        blank=True,
        help_text='Service code (CPT, HCPCS)'
    )

    # Dates
    issue_date = models.DateField(
        help_text='Date invoice was issued'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text='Payment due date'
    )
    service_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date service was provided'
    )

    # Payment information
    payment_method = models.CharField(
        max_length=100,
        blank=True,
        help_text='Method of payment (credit card, insurance, etc.)'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date payment was received'
    )

    # Additional notes
    notes = models.TextField(
        blank=True,
        help_text='Additional billing notes'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['patient', '-issue_date']),
            models.Index(fields=['invoice_number']),
        ]
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        """String representation of invoice."""
        return f"Invoice {self.invoice_number} - {self.patient.get_full_name()} - ${self.total_gross}"

    def calculate_balance(self):
        """Calculate and update balance due."""
        self.balance_due = self.total_gross - self.amount_paid
        return self.balance_due

    def is_paid(self):
        """Check if invoice is fully paid."""
        return self.amount_paid >= self.total_gross

    def is_overdue(self):
        """Check if invoice is overdue."""
        from django.utils import timezone
        if not self.due_date:
            return False
        return timezone.now().date() > self.due_date and not self.is_paid()

    def save(self, *args, **kwargs):
        """Override save to auto-calculate balance."""
        self.calculate_balance()
        super().save(*args, **kwargs)
