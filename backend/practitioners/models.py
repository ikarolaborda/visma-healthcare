"""
Practitioner models for the healthcare system.

This module defines the Practitioner model following FHIR R4 standards.
"""

import uuid
from django.db import models
from django.core.validators import EmailValidator


class Practitioner(models.Model):
    """
    Practitioner model conforming to FHIR Practitioner resource structure.

    This model stores healthcare practitioner information following the
    Fast Healthcare Interoperability Resources (FHIR) standard.
    Practitioners include doctors, nurses, therapists, and other healthcare providers.
    """

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('unknown', 'Unknown'),
    ]

    PREFIX_CHOICES = [
        ('Dr.', 'Doctor'),
        ('Prof.', 'Professor'),
        ('Mr.', 'Mister'),
        ('Ms.', 'Miss'),
        ('Mrs.', 'Misses'),
    ]

    # Primary identifiers
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this practitioner"
    )

    # Name fields (following FHIR HumanName)
    prefix = models.CharField(
        max_length=10,
        choices=PREFIX_CHOICES,
        blank=True,
        null=True,
        help_text="Name prefix (Dr., Prof., etc.)"
    )
    family_name = models.CharField(
        max_length=255,
        help_text="Family name (surname)"
    )
    given_name = models.CharField(
        max_length=255,
        help_text="Given name (first name)"
    )
    middle_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Middle name(s)"
    )

    # Gender - FHIR administrative gender
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="Administrative gender - male | female | other | unknown"
    )

    # Birth date (optional for practitioners)
    birth_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth"
    )

    # Professional identifiers
    npi = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text="National Provider Identifier (NPI) - unique 10-digit number"
    )
    license_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Medical license number"
    )

    # Professional information
    specialization = models.CharField(
        max_length=200,
        help_text="Medical specialization (e.g., Cardiology, Pediatrics, General Practice)"
    )
    qualification = models.TextField(
        help_text="Qualifications and degrees (e.g., MD, PhD, DO)"
    )
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Years of professional experience"
    )

    # Address fields (simplified from FHIR Address)
    address_line = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Street address"
    )
    address_city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City"
    )
    address_state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="State or province"
    )
    address_postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Postal code"
    )
    address_country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country"
    )

    # Telecom - Email (ContactPoint in FHIR)
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Professional email address"
    )

    # Phone number
    phone = models.CharField(
        max_length=50,
        help_text="Professional phone number"
    )

    # Metadata
    active = models.BooleanField(
        default=True,
        help_text="Whether this practitioner is currently active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Record creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Record last update timestamp"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family_name', 'given_name']),
            models.Index(fields=['specialization']),
            models.Index(fields=['npi']),
            models.Index(fields=['email']),
        ]
        verbose_name = 'Practitioner'
        verbose_name_plural = 'Practitioners'

    def __str__(self):
        """String representation of the practitioner."""
        prefix = f"{self.prefix} " if self.prefix else ""
        return f"{prefix}{self.given_name} {self.family_name} - {self.specialization}"

    def get_full_name(self):
        """Return the full name of the practitioner with prefix."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.append(self.given_name)
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.family_name)
        return ' '.join(parts)

    def get_address(self):
        """Return formatted address string."""
        address_parts = [
            self.address_line,
            self.address_city,
            self.address_state,
            self.address_postal_code,
            self.address_country
        ]
        return ', '.join(filter(None, address_parts))

    def get_credentials(self):
        """Return formatted credentials string."""
        if self.prefix and self.qualification:
            return f"{self.prefix} {self.given_name} {self.family_name}, {self.qualification}"
        elif self.qualification:
            return f"{self.given_name} {self.family_name}, {self.qualification}"
        return self.get_full_name()
