"""
API views for Prescription (MedicationRequest) resources.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionViewSet(viewsets.ViewSet):
    """
    API ViewSet for Prescription resources.

    Provides CRUD operations for medication prescriptions.
    All endpoints require JWT authentication.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PrescriptionSerializer

    def list(self, request):
        """
        List all prescriptions as FHIR MedicationRequest resources in a Bundle.

        Returns:
            Response: FHIR Bundle containing MedicationRequest resources
        """
        queryset = Prescription.objects.select_related('patient', 'prescriber').all()
        serializer = PrescriptionSerializer(queryset, many=True)

        # Create FHIR Bundle response
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(serializer.data),
            "entry": [
                {
                    "resource": prescription_data
                }
                for prescription_data in serializer.data
            ]
        }

        return Response(bundle, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create a new prescription.

        Args:
            request: HTTP request with prescription data in body

        Returns:
            Response: Created Prescription resource with 201 status
        """
        serializer = PrescriptionSerializer(data=request.data)

        if serializer.is_valid():
            prescription = serializer.save()
            response_serializer = PrescriptionSerializer(prescription)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific prescription by ID.

        Args:
            request: HTTP request
            pk: Prescription ID (UUID)

        Returns:
            Response: Prescription resource
        """
        prescription = get_object_or_404(
            Prescription.objects.select_related('patient', 'prescriber'),
            pk=pk
        )
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Update an existing prescription.

        Args:
            request: HTTP request with prescription data in body
            pk: Prescription ID (UUID)

        Returns:
            Response: Updated Prescription resource
        """
        prescription = get_object_or_404(Prescription, pk=pk)
        serializer = PrescriptionSerializer(prescription, data=request.data)

        if serializer.is_valid():
            updated_prescription = serializer.save()
            response_serializer = PrescriptionSerializer(updated_prescription)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a prescription.

        Args:
            request: HTTP request
            pk: Prescription ID (UUID)

        Returns:
            Response: 204 No Content on success
        """
        prescription = get_object_or_404(Prescription, pk=pk)
        prescription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
