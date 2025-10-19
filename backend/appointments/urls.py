"""
URL routing for Appointment API endpoints.

This module defines the URL patterns for FHIR-compliant Appointment resources.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet

# Create a router for the Appointment ViewSet
router = DefaultRouter()
router.register(r'Appointment', AppointmentViewSet, basename='appointment')

# URL patterns
urlpatterns = router.urls
