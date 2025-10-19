"""
API views for Clinical Records (Patient History).
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ClinicalRecord
from .serializers import ClinicalRecordSerializer

class ClinicalRecordViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClinicalRecordSerializer

    def list(self, request):
        queryset = ClinicalRecord.objects.select_related('patient', 'recorded_by').all()
        serializer = ClinicalRecordSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ClinicalRecordSerializer(data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            return Response(ClinicalRecordSerializer(record).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        record = get_object_or_404(ClinicalRecord.objects.select_related('patient', 'recorded_by'), pk=pk)
        return Response(ClinicalRecordSerializer(record).data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        record = get_object_or_404(ClinicalRecord, pk=pk)
        serializer = ClinicalRecordSerializer(record, data=request.data)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(ClinicalRecordSerializer(updated).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        get_object_or_404(ClinicalRecord, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
