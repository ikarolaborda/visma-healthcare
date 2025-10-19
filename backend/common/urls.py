"""
URL configuration for common app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicSettingsViewSet

router = DefaultRouter()
router.register(r'settings', ClinicSettingsViewSet, basename='clinic-settings')

urlpatterns = [
    path('', include(router.urls)),
]
