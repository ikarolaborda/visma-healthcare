"""
URL configuration for Billing API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet

router = DefaultRouter()
router.register(r'Invoice', InvoiceViewSet, basename='invoice')

urlpatterns = router.urls
