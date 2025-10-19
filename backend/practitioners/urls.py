"""
URL routing for Practitioner API endpoints.

This module defines the URL patterns for FHIR-compliant Practitioner resources.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PractitionerViewSet

# Create a router for the Practitioner ViewSet
router = DefaultRouter()
router.register(r'Practitioner', PractitionerViewSet, basename='practitioner')

# URL patterns
urlpatterns = router.urls
