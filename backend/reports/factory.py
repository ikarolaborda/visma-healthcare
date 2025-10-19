"""
Application Layer: Report Factory implementing Factory Pattern.
Creates appropriate strategy based on requested format.
"""
from typing import Dict
from .interfaces import IReportStrategy
from .strategies import (
    PDFReportStrategy,
    CSVReportStrategy,
    TXTReportStrategy,
    JSONReportStrategy
)


class ReportFactory:
    """
    Factory class for creating report strategy instances.
    Implements Factory Pattern - encapsulates object creation logic.
    """

    # Registry of available strategies
    _strategies: Dict[str, type] = {
        'pdf': PDFReportStrategy,
        'csv': CSVReportStrategy,
        'txt': TXTReportStrategy,
        'json': JSONReportStrategy,
    }

    @classmethod
    def create_strategy(cls, format_type: str) -> IReportStrategy:
        """
        Create and return appropriate report strategy based on format.

        Args:
            format_type: Output format ('pdf', 'csv', 'txt', 'json')

        Returns:
            IReportStrategy: Instance of appropriate strategy

        Raises:
            ValueError: If format_type is not supported
        """
        format_type = format_type.lower()

        if format_type not in cls._strategies:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {', '.join(cls._strategies.keys())}"
            )

        strategy_class = cls._strategies[format_type]
        return strategy_class()

    @classmethod
    def register_strategy(cls, format_type: str, strategy_class: type):
        """
        Register a new strategy class.
        Allows extending the factory with new formats at runtime.

        Args:
            format_type: Format identifier
            strategy_class: Strategy class to register
        """
        if not issubclass(strategy_class, IReportStrategy):
            raise TypeError(f"{strategy_class} must implement IReportStrategy")

        cls._strategies[format_type.lower()] = strategy_class

    @classmethod
    def get_supported_formats(cls) -> list:
        """Return list of supported formats."""
        return list(cls._strategies.keys())
