"""
URL configuration for healthcare project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="Healthcare Patient Management API",
        default_version='v1',
        description="FHIR-compliant RESTful API for managing patient information",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@healthcare.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Authentication API
    path('api/auth/', include('authentication.urls')),

    # FHIR Patient API
    path('fhir/', include('patients.urls')),

    # FHIR Practitioner API
    path('fhir/', include('practitioners.urls')),

    # FHIR Appointment API
    path('fhir/', include('appointments.urls')),

    # FHIR MedicationRequest (Prescriptions) API
    path('fhir/', include('prescriptions.urls')),

    # Clinical Records (Patient History) API
    path('fhir/', include('patient_history.urls')),

    # Invoice (Billing) API
    path('fhir/', include('billing.urls')),

    # Reports API
    path('api/reports/', include('reports.urls')),

    # AI Chat API
    path('api/ai-chat/', include('ai_chat.urls')),

    # Common/Settings API
    path('api/common/', include('common.urls')),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
