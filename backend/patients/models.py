"""
Patient model following FHIR standards.
Stores patient demographic and administrative information.
"""
from django.db import models
from django.core.validators import EmailValidator
import uuid


class Patient(models.Model):
    """
    Patient model conforming to FHIR Patient resource structure.

    This model stores patient demographic information following the
    Fast Healthcare Interoperability Resources (FHIR) standard.
    """

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('unknown', 'Unknown'),
    ]

    # Primary identifiers
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this patient"
    )

    # Name fields (simplified from FHIR HumanName)
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

    # Birth date
    birth_date = models.DateField(
        help_text="Date of birth"
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
        blank=True,
        null=True,
        help_text="Email address"
    )

    # Phone number
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Phone number"
    )

    # Metadata
    active = models.BooleanField(
        default=True,
        help_text="Whether this patient's record is in active use"
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
            models.Index(fields=['birth_date']),
            models.Index(fields=['email']),
        ]
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        """String representation of the patient."""
        return f"{self.given_name} {self.family_name} ({self.id})"

    def get_full_name(self):
        """Return the full name of the patient."""
        parts = [self.given_name]
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
