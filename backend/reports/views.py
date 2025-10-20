"""
API Views for Reports module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer, ReportFilterSerializer
from .service import ReportService


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Report resources.

    Provides endpoints for:
    - Listing user reports
    - Generating new reports
    - Retrieving report details
    - Downloading report files
    - Deleting reports

    All endpoints require authentication.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer
    service = ReportService()

    def get_queryset(self):
        """
        Get reports for current user with optional filtering.
        """
        user = self.request.user
        filters = {}

        # Extract filter parameters
        report_type = self.request.query_params.get('report_type')
        format_type = self.request.query_params.get('format')
        status_filter = self.request.query_params.get('status')

        if report_type:
            filters['report_type'] = report_type
        if format_type:
            filters['format'] = format_type
        if status_filter:
            filters['status'] = status_filter

        return self.service.list_reports(user_id=user.id, filters=filters if filters else None)

    @swagger_auto_schema(
        operation_description="List all reports for current user",
        manual_parameters=[
            openapi.Parameter('report_type', openapi.IN_QUERY, description="Filter by report type", type=openapi.TYPE_STRING),
            openapi.Parameter('format', openapi.IN_QUERY, description="Filter by format", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING),
        ],
        responses={200: ReportSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List reports with optional filtering."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Generate a new report",
        request_body=ReportCreateSerializer,
        responses={
            201: ReportSerializer,
            400: "Validation error"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Generate a new report.

        Accepts report parameters and creates a report file.
        The report is generated synchronously.
        """
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Generate report using service
            report = self.service.generate_report(
                report_type=serializer.validated_data['report_type'],
                format_type=serializer.validated_data['format'],
                filters=serializer.validated_data.get('filters', {}),
                user_id=request.user.id,
                title=serializer.validated_data.get('title'),
                description=serializer.validated_data.get('description', '')
            )

            # Return created report
            output_serializer = ReportSerializer(report, context={'request': request})
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Report generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Retrieve report details",
        responses={
            200: ReportSerializer,
            404: "Report not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get report details."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a report",
        responses={
            204: "Report deleted successfully",
            404: "Report not found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a report and its file."""
        report = self.get_object()

        try:
            self.service.delete_report(report.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': f'Failed to delete report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Download report file",
        responses={
            200: "File content",
            400: "Report not ready",
            404: "Report or file not found"
        }
    )
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download the generated report file.

        Returns the file as a download with appropriate content type.
        """
        report = self.get_object()

        # Check if report is completed
        if report.status != Report.STATUS_COMPLETED:
            return Response(
                {'error': f'Report is not ready. Current status: {report.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if file exists
        if not report.file:
            return Response(
                {'error': 'Report file not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Get strategy to determine content type
            from .factory import ReportFactory
            strategy = ReportFactory.create_strategy(report.format)

            # Return file response
            response = FileResponse(
                report.file.open('rb'),
                content_type=strategy.get_content_type()
            )
            response['Content-Disposition'] = f'attachment; filename="{report.get_filename()}"'
            return response

        except FileNotFoundError:
            return Response(
                {'error': 'Report file not found on disk'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Get available report types",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'report_types': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'formats': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            }
        )}
    )
    @action(detail=False, methods=['get'])
    def options(self, request):
        """
        Get available report types and formats.

        Returns lists of supported report types and output formats.
        """
        return Response({
            'report_types': self.service.get_available_report_types(),
            'formats': self.service.get_supported_formats(),
        })
