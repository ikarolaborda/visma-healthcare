"""
Django app configuration for practitioners module.
"""

from django.apps import AppConfig


class PractitionersConfig(AppConfig):
    """Configuration for the practitioners app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "practitioners"
    verbose_name = "Healthcare Practitioners"
