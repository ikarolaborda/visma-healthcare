"""
Application Layer: Report generation service.
Implements business logic for report generation using DIP.
"""
from __future__ import annotations
import os
from typing import Any, Dict, TYPE_CHECKING
from datetime import datetime
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import QuerySet

from .interfaces import IReportGenerator, IReportDataProvider
from .models import Report
from .factory import ReportFactory
from .data_provider import DjangoReportDataProvider


class ReportService(IReportGenerator):
    """
    Service class for report generation.
    Implements IReportGenerator interface (Dependency Inversion Principle).
    Orchestrates the report generation process using Strategy and Factory patterns.
    """

    def __init__(self, data_provider: IReportDataProvider = None):
        """
        Initialize service with data provider.

        Args:
            data_provider: Optional custom data provider (DIP - depends on abstraction)
        """
        self.data_provider = data_provider or DjangoReportDataProvider()

    def generate_report(
        self,
        report_type: str,
        format_type: str,
        filters: Dict[str, Any],
        user_id: int,
        title: str = None,
        description: str = ""
    ) -> Report:
        """
        Generate a report based on type and format.

        This method demonstrates the integration of all design patterns:
        - Factory Pattern: Creates appropriate strategy
        - Strategy Pattern: Generates report in requested format
        - DIP: Depends on abstractions (IReportDataProvider, IReportStrategy)

        Args:
            report_type: Type of report (patients, appointments, etc.)
            format_type: Output format (pdf, csv, txt, json)
            filters: Filtering parameters
            user_id: ID of user requesting the report
            title: Optional custom title
            description: Optional description

        Returns:
            Report: Generated report model instance

        Raises:
            ValueError: If report_type or format_type is invalid
        """
        # Create report record
        if not title:
            title = f"{report_type.replace('_', ' ').title()} Report"

        report = Report.objects.create(
            user_id=user_id,
            report_type=report_type,
            format=format_type,
            title=title,
            description=description,
            filters=filters,
            status=Report.STATUS_PENDING
        )

        try:
            # Mark as processing
            report.mark_processing()

            # Fetch data using data provider (DIP - depends on abstraction)
            data = self.data_provider.get_data(report_type, filters)

            # Create metadata
            metadata = {
                'title': title,
                'report_type': report_type,
                'generated_at': timezone.now().isoformat(),
                'filters': filters,
                'user_id': user_id
            }

            # Get strategy from factory (Factory Pattern)
            strategy = ReportFactory.create_strategy(format_type)

            # Generate report using strategy (Strategy Pattern)
            content = strategy.generate(data, metadata)

            # Save file
            filename = f"{report_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{strategy.get_file_extension()}"
            file_content = ContentFile(content)

            # Save to report model
            report.file.save(filename, file_content, save=False)
            report.mark_completed(report.file.name, len(data))

            return report

        except Exception as e:
            # Mark as failed
            report.mark_failed(str(e))
            raise

    def get_report(self, report_id: str) -> Report:
        """
        Retrieve a report by ID.

        Args:
            report_id: UUID of the report

        Returns:
            Report instance

        Raises:
            Report.DoesNotExist: If report not found
        """
        return Report.objects.get(pk=report_id)

    def list_reports(self, user_id: int = None, filters: Dict[str, Any] = None) -> 'QuerySet':
        """
        List reports with optional filtering.

        Args:
            user_id: Optional user ID to filter by
            filters: Optional additional filters

        Returns:
            QuerySet of Report instances
        """
        queryset = Report.objects.all()

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if filters:
            if filters.get('report_type'):
                queryset = queryset.filter(report_type=filters['report_type'])

            if filters.get('format'):
                queryset = queryset.filter(format=filters['format'])

            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])

            if filters.get('created_from'):
                queryset = queryset.filter(created_at__gte=filters['created_from'])

            if filters.get('created_to'):
                queryset = queryset.filter(created_at__lte=filters['created_to'])

        return queryset.order_by('-created_at')

    def delete_report(self, report_id: str):
        """
        Delete a report.

        Args:
            report_id: UUID of the report

        Raises:
            Report.DoesNotExist: If report not found
        """
        report = Report.objects.get(pk=report_id)

        # Delete file from storage if exists
        if report.file:
            if os.path.exists(report.file.path):
                os.remove(report.file.path)

        report.delete()

    def get_supported_formats(self) -> list:
        """Get list of supported output formats."""
        return ReportFactory.get_supported_formats()

    def get_available_report_types(self) -> list:
        """Get list of available report types."""
        return [choice[0] for choice in Report.REPORT_TYPE_CHOICES]
