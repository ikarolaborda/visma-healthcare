"""
URL routing for Patient API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'Patient', PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
]
