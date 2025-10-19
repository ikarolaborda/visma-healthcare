"""
Domain Layer: Abstract interfaces for Reports module.
Implements Dependency Inversion Principle (DIP).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .models import Report


class IReportStrategy(ABC):
    """
    Abstract base class for report generation strategies.
    Implements Strategy Pattern - defines the interface for all report format strategies.
    """

    @abstractmethod
    def generate(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bytes:
        """
        Generate report in specific format.

        Args:
            data: List of records to include in report
            metadata: Report metadata (title, parameters, generated_at, etc.)

        Returns:
            bytes: Generated report content
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return file extension for this format (e.g., 'pdf', 'csv')."""
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """Return MIME content type for this format."""
        pass


class IReportGenerator(ABC):
    """
    Abstract interface for report generation service.
    Implements Dependency Inversion Principle - high-level module depends on abstraction.
    """

    @abstractmethod
    def generate_report(
        self,
        report_type: str,
        format_type: str,
        filters: Dict[str, Any],
        user_id: int
    ) -> 'Report':
        """
        Generate a report based on type and format.

        Args:
            report_type: Type of report (patients, appointments, etc.)
            format_type: Output format (pdf, csv, txt, json)
            filters: Filtering parameters (date_range, status, etc.)
            user_id: ID of user requesting the report

        Returns:
            Report: Generated report model instance
        """
        pass


class IReportDataProvider(ABC):
    """
    Abstract interface for fetching report data.
    Allows different data sources to be plugged in.
    """

    @abstractmethod
    def get_data(self, report_type: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data for report based on type and filters.

        Args:
            report_type: Type of report
            filters: Filtering parameters

        Returns:
            List of data records
        """
        pass

    @abstractmethod
    def get_field_definitions(self, report_type: str) -> List[Dict[str, str]]:
        """
        Get field definitions for report type.

        Returns:
            List of field definitions with name, label, and type
        """
        pass
