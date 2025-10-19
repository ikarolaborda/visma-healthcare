"""
API views for Patient resource management.

Implements FHIR-compliant RESTful endpoints following SOLID principles:
- Single Responsibility: Each view handles one resource type
- Open/Closed: Extensible through inheritance
- Liskov Substitution: Proper use of DRF base classes
- Interface Segregation: Focused on Patient operations
- Dependency Inversion: Depends on abstractions (serializers, models)
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Patient
from .serializers import FHIRPatientSerializer, PatientSerializer


class PatientViewSet(viewsets.ViewSet):
    """
    FHIR-compliant Patient resource API ViewSet.

    Provides CRUD operations for Patient resources following
    the FHIR R4 specification.

    All endpoints now require JWT authentication via Bearer token.

    Endpoints:
        GET /fhir/Patient - List all patients (requires authentication)
        POST /fhir/Patient - Create a new patient (requires authentication)
        GET /fhir/Patient/{id} - Retrieve a specific patient (requires authentication)
        PUT /fhir/Patient/{id} - Update a specific patient (requires authentication)
        DELETE /fhir/Patient/{id} - Delete a specific patient (requires authentication)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FHIRPatientSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of all patients in FHIR format",
        responses={
            200: openapi.Response(
                description="Bundle of Patient resources",
                examples={
                    "application/json": {
                        "resourceType": "Bundle",
                        "type": "searchset",
                        "total": 2,
                        "entry": []
                    }
                }
            )
        }
    )
    def list(self, request):
        """
        List all patients as FHIR Patient resources.

        Returns:
            Response: Array of FHIR Patient resources
        """
        queryset = Patient.objects.all()
        serializer = FHIRPatientSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new patient record",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['resourceType', 'name', 'gender', 'birthDate'],
            properties={
                'resourceType': openapi.Schema(type=openapi.TYPE_STRING, example='Patient'),
                'name': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'family': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                            'given': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING),
                                example=['John']
                            )
                        }
                    )
                ),
                'gender': openapi.Schema(type=openapi.TYPE_STRING, example='male'),
                'birthDate': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='1990-01-01'),
            }
        ),
        responses={
            201: openapi.Response(description="Patient created successfully"),
            400: openapi.Response(description="Invalid FHIR Patient resource")
        }
    )
    def create(self, request):
        """
        Create a new patient from FHIR Patient resource.

        Args:
            request: HTTP request with FHIR Patient resource in body

        Returns:
            Response: Created Patient resource with 201 status
        """
        serializer = FHIRPatientSerializer(data=request.data)

        if serializer.is_valid():
            patient = serializer.save()
            response_serializer = FHIRPatientSerializer(patient)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a specific patient by ID",
        responses={
            200: openapi.Response(description="Patient resource"),
            404: openapi.Response(description="Patient not found")
        }
    )
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific patient by ID.

        Args:
            request: HTTP request
            pk: Patient ID (UUID)

        Returns:
            Response: FHIR Patient resource
        """
        patient = get_object_or_404(Patient, pk=pk)
        serializer = FHIRPatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a specific patient",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resourceType': openapi.Schema(type=openapi.TYPE_STRING, example='Patient'),
            }
        ),
        responses={
            200: openapi.Response(description="Patient updated successfully"),
            400: openapi.Response(description="Invalid FHIR Patient resource"),
            404: openapi.Response(description="Patient not found")
        }
    )
    def update(self, request, pk=None):
        """
        Update an existing patient.

        Args:
            request: HTTP request with FHIR Patient resource in body
            pk: Patient ID (UUID)

        Returns:
            Response: Updated Patient resource
        """
        patient = get_object_or_404(Patient, pk=pk)
        serializer = FHIRPatientSerializer(patient, data=request.data)

        if serializer.is_valid():
            updated_patient = serializer.save()
            response_serializer = FHIRPatientSerializer(updated_patient)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a specific patient",
        responses={
            204: openapi.Response(description="Patient deleted successfully"),
            404: openapi.Response(description="Patient not found")
        }
    )
    def destroy(self, request, pk=None):
        """
        Delete a patient.

        Args:
            request: HTTP request
            pk: Patient ID (UUID)

        Returns:
            Response: 204 No Content on success
        """
        patient = get_object_or_404(Patient, pk=pk)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
