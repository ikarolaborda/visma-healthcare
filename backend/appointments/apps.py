"""
Appointments app configuration.
"""
from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """Configuration for Appointments app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "appointments"
    verbose_name = "Appointments"
