"""
API views for Clinical Records (Patient History).
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ClinicalRecord
from .serializers import ClinicalRecordSerializer, FHIRClinicalRecordSerializer

class ClinicalRecordViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return FHIR serializer by default, standard serializer if format=standard.
        """
        format_param = self.request.query_params.get('format', 'fhir')
        if format_param.lower() == 'standard':
            return ClinicalRecordSerializer
        return FHIRClinicalRecordSerializer

    def list(self, request):
        queryset = ClinicalRecord.objects.select_related('patient', 'recorded_by').all()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)

        # Create FHIR Bundle response
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(serializer.data),
            "entry": [
                {
                    "resource": record_data
                }
                for record_data in serializer.data
            ]
        }

        return Response(bundle, status=status.HTTP_200_OK)

    def create(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            return Response(serializer_class(record).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        record = get_object_or_404(ClinicalRecord.objects.select_related('patient', 'recorded_by'), pk=pk)
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(record).data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        record = get_object_or_404(ClinicalRecord, pk=pk)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(record, data=request.data)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(serializer_class(updated).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        get_object_or_404(ClinicalRecord, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
