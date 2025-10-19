"""
URL configuration for Patient History API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicalRecordViewSet

router = DefaultRouter()
router.register(r'ClinicalRecord', ClinicalRecordViewSet, basename='clinicalrecord')

urlpatterns = router.urls
