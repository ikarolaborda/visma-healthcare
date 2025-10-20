"""
Common models shared across the application.
"""
from django.db import models
from django.core.validators import FileExtensionValidator


class ClinicSettings(models.Model):
    """
    Singleton model for storing clinic/organization settings.
    Only one instance should exist.
    """

    # Clinic Information
    clinic_name = models.CharField(
        max_length=255,
        default='Healthcare Clinic',
        help_text='Name of the clinic or healthcare organization'
    )
    clinic_address = models.TextField(
        blank=True,
        help_text='Full address of the clinic'
    )
    clinic_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text='Primary contact phone number'
    )
    clinic_email = models.EmailField(
        blank=True,
        help_text='Primary contact email'
    )
    clinic_website = models.URLField(
        blank=True,
        help_text='Clinic website URL'
    )

    # Branding
    logo = models.ImageField(
        upload_to='clinic/logos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg'])],
        help_text='Clinic logo for reports and documents'
    )
    primary_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Primary brand color (hex format, e.g., #3B82F6)'
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#10B981',
        help_text='Secondary brand color (hex format, e.g., #10B981)'
    )

    # Report Settings
    report_header_text = models.TextField(
        blank=True,
        help_text='Custom header text for reports'
    )
    report_footer_text = models.TextField(
        blank=True,
        default='© 2025 Healthcare Patient Management. All rights reserved.',
        help_text='Custom footer text for reports'
    )
    include_logo_in_reports = models.BooleanField(
        default=True,
        help_text='Include clinic logo in generated reports'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Clinic Settings'
        verbose_name_plural = 'Clinic Settings'

    def __str__(self):
        return f"Settings for {self.clinic_name}"

    def save(self, *args, **kwargs):
        """
        Override save to ensure only one instance exists (singleton pattern).
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load the singleton instance, creating it if it doesn't exist.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
