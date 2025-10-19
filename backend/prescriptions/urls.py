"""
URL configuration for Prescription API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet

router = DefaultRouter()
router.register(r'MedicationRequest', PrescriptionViewSet, basename='prescription')

urlpatterns = router.urls
