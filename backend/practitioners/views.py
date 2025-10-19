"""
API views for Practitioner resources.

This module provides FHIR-compliant REST API endpoints for managing
healthcare practitioner resources.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Practitioner
from .serializers import FHIRPractitionerSerializer


class PractitionerViewSet(viewsets.ViewSet):
    """
    FHIR-compliant Practitioner resource API ViewSet.

    Provides CRUD operations for Practitioner resources following
    the FHIR R4 specification.

    All endpoints require JWT authentication via Bearer token.

    Endpoints:
        GET /fhir/Practitioner - List all practitioners
        POST /fhir/Practitioner - Create a new practitioner
        GET /fhir/Practitioner/{id} - Retrieve a specific practitioner
        PUT /fhir/Practitioner/{id} - Update a specific practitioner
        DELETE /fhir/Practitioner/{id} - Delete a specific practitioner
        GET /fhir/Practitioner/search - Search practitioners
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FHIRPractitionerSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of all practitioners in FHIR format",
        responses={
            200: openapi.Response(
                description="Bundle of Practitioner resources",
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
        List all practitioners as FHIR Practitioner resources.

        Returns:
            Response: Array of FHIR Practitioner resources
        """
        queryset = Practitioner.objects.all()
        serializer = FHIRPractitionerSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new practitioner record",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['resourceType', 'name', 'specialization', 'qualification'],
            properties={
                'resourceType': openapi.Schema(type=openapi.TYPE_STRING, example='Practitioner'),
                'name': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'family': openapi.Schema(type=openapi.TYPE_STRING, example='Smith'),
                            'given': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING),
                                example=['John']
                            ),
                            'prefix': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING),
                                example=['Dr.']
                            )
                        }
                    )
                ),
                'gender': openapi.Schema(type=openapi.TYPE_STRING, example='male'),
                'specialization': openapi.Schema(type=openapi.TYPE_STRING, example='Cardiology'),
                'qualification': openapi.Schema(type=openapi.TYPE_STRING, example='MD, PhD'),
                'telecom': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'system': openapi.Schema(type=openapi.TYPE_STRING, example='email'),
                            'value': openapi.Schema(type=openapi.TYPE_STRING, example='dr.smith@hospital.com'),
                        }
                    )
                ),
            }
        ),
        responses={
            201: openapi.Response(description="Practitioner created successfully"),
            400: openapi.Response(description="Invalid FHIR Practitioner resource")
        }
    )
    def create(self, request):
        """
        Create a new practitioner from FHIR Practitioner resource.

        Args:
            request: HTTP request with FHIR Practitioner resource in body

        Returns:
            Response: Created Practitioner resource with 201 status
        """
        serializer = FHIRPractitionerSerializer(data=request.data)

        if serializer.is_valid():
            practitioner = serializer.save()
            response_serializer = FHIRPractitionerSerializer(practitioner)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a specific practitioner by ID",
        responses={
            200: openapi.Response(description="Practitioner resource"),
            404: openapi.Response(description="Practitioner not found")
        }
    )
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific practitioner by ID.

        Args:
            request: HTTP request
            pk: Practitioner ID (UUID)

        Returns:
            Response: FHIR Practitioner resource
        """
        practitioner = get_object_or_404(Practitioner, pk=pk)
        serializer = FHIRPractitionerSerializer(practitioner)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a specific practitioner",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resourceType': openapi.Schema(type=openapi.TYPE_STRING, example='Practitioner'),
            }
        ),
        responses={
            200: openapi.Response(description="Practitioner updated successfully"),
            400: openapi.Response(description="Invalid FHIR Practitioner resource"),
            404: openapi.Response(description="Practitioner not found")
        }
    )
    def update(self, request, pk=None):
        """
        Update an existing practitioner.

        Args:
            request: HTTP request with FHIR Practitioner resource in body
            pk: Practitioner ID (UUID)

        Returns:
            Response: Updated Practitioner resource
        """
        practitioner = get_object_or_404(Practitioner, pk=pk)
        serializer = FHIRPractitionerSerializer(practitioner, data=request.data)

        if serializer.is_valid():
            updated_practitioner = serializer.save()
            response_serializer = FHIRPractitionerSerializer(updated_practitioner)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a specific practitioner",
        responses={
            204: openapi.Response(description="Practitioner deleted successfully"),
            404: openapi.Response(description="Practitioner not found")
        }
    )
    def destroy(self, request, pk=None):
        """
        Delete a practitioner.

        Args:
            request: HTTP request
            pk: Practitioner ID (UUID)

        Returns:
            Response: 204 No Content on success
        """
        practitioner = get_object_or_404(Practitioner, pk=pk)
        practitioner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Search practitioners by name or specialization",
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Search query (name or specialization)",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(description="Bundle of matching Practitioner resources"),
        }
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search practitioners by name or specialization.

        Args:
            request: HTTP request with 'query' parameter

        Returns:
            Response: FHIR Bundle containing matching practitioners
        """
        query = request.query_params.get('query', '')

        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.db.models import Q

        queryset = Practitioner.objects.filter(
            Q(given_name__icontains=query) |
            Q(family_name__icontains=query) |
            Q(specialization__icontains=query),
            active=True
        )

        serializer = FHIRPractitionerSerializer(queryset, many=True)

        bundle = {
            'resourceType': 'Bundle',
            'type': 'searchset',
            'total': queryset.count(),
            'entry': [
                {
                    'resource': practitioner_data
                }
                for practitioner_data in serializer.data
            ]
        }

        return Response(bundle, status=status.HTTP_200_OK)
