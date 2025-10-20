"""
API views for Invoices (Billing).
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Invoice
from .serializers import InvoiceSerializer

class InvoiceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer

    def list(self, request):
        queryset = Invoice.objects.select_related('patient', 'appointment').all()
        serializer = InvoiceSerializer(queryset, many=True)

        # Create FHIR Bundle response
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(serializer.data),
            "entry": [
                {
                    "resource": invoice_data
                }
                for invoice_data in serializer.data
            ]
        }

        return Response(bundle, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save()
            return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        invoice = get_object_or_404(Invoice.objects.select_related('patient', 'appointment'), pk=pk)
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        invoice = get_object_or_404(Invoice, pk=pk)
        serializer = InvoiceSerializer(invoice, data=request.data)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(InvoiceSerializer(updated).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        get_object_or_404(Invoice, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
