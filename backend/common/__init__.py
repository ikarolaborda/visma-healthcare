"""
Common module containing reusable base patterns for the healthcare system.

This module provides:
- Repository Pattern: Data access abstraction
- Service Layer Pattern: Business logic encapsulation
- Factory Pattern: FHIR resource creation
"""

from .repositories import BaseRepository
from .services import BaseService
from .factories import FHIRResourceFactory

__all__ = [
    'BaseRepository',
    'BaseService',
    'FHIRResourceFactory',
]
