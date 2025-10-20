"""
Service layer for Practitioner business logic.

This module implements the Service Layer Pattern for Practitioner operations,
encapsulating business logic and coordinating between repositories.
"""

from typing import Dict, Any
from uuid import UUID
from django.core.exceptions import ValidationError
from common.services import BaseService
from .models import Practitioner
from .repositories import PractitionerRepository


class PractitionerService(BaseService[Practitioner]):
    """
    Service for managing Practitioner business logic.

    This class extends BaseService to provide Practitioner-specific
    business logic while inheriting standard service operations.

    Business rules enforced:
    - NPI must be unique if provided
    - Email must be unique
    - Specialization and qualification are required
    - Active practitioners must have complete contact information
    """

    def __init__(self):
        """Initialize service with PractitionerRepository."""
        repository = PractitionerRepository()
        super().__init__(repository)

    def validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a practitioner.

        Args:
            data: Practitioner data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not data.get('given_name'):
            raise ValidationError('Given name is required')

        if not data.get('family_name'):
            raise ValidationError('Family name is required')

        if not data.get('email'):
            raise ValidationError('Email is required')

        if not data.get('phone'):
            raise ValidationError('Phone number is required')

        if not data.get('specialization'):
            raise ValidationError('Specialization is required')

        if not data.get('qualification'):
            raise ValidationError('Qualification is required')

        # Validate NPI uniqueness if provided
        if data.get('npi'):
            existing = self.repository.find_by_npi(data['npi'])
            if existing:
                raise ValidationError(f'Practitioner with NPI {data["npi"]} already exists')

        # Validate email uniqueness
        existing = self.repository.find_by_email(data['email'])
        if existing:
            raise ValidationError(f'Practitioner with email {data["email"]} already exists')

    def validate_update(self, existing: Practitioner, data: Dict[str, Any]) -> None:
        """
        Validate data before updating a practitioner.

        Args:
            existing: The existing Practitioner instance
            data: Updated data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Validate NPI uniqueness if being changed
        if 'npi' in data and data['npi'] != existing.npi:
            if data['npi']:
                other = self.repository.find_by_npi(data['npi'])
                if other and other.id != existing.id:
                    raise ValidationError(f'Practitioner with NPI {data["npi"]} already exists')

        # Validate email uniqueness if being changed
        if 'email' in data and data['email'] != existing.email:
            other = self.repository.find_by_email(data['email'])
            if other and other.id != existing.id:
                raise ValidationError(f'Practitioner with email {data["email"]} already exists')

    def validate_delete(self, existing: Practitioner) -> None:
        """
        Validate before deleting a practitioner.

        Args:
            existing: The Practitioner to be deleted

        Raises:
            ValidationError: If deletion is not allowed
        """
        # In the future, we can add checks for:
        # - Active appointments
        # - Pending prescriptions
        # - Patient assignments
        # For now, allow deletion
        pass

    def find_by_specialization(self, specialization: str):
        """
        Find practitioners by specialization.

        Args:
            specialization: The medical specialization

        Returns:
            List of practitioners with the specified specialization
        """
        return self.repository.find_by_specialization(specialization)

    def find_active_practitioners(self):
        """
        Get all active practitioners.

        Returns:
            List of active practitioners
        """
        return self.repository.find_active_practitioners()

    def search_practitioners(self, query: str):
        """
        Search practitioners by name or specialization.

        Args:
            query: Search query string

        Returns:
            List of matching practitioners
        """
        # Search by name
        name_results = self.repository.search_by_name(query)

        # Search by specialization
        spec_results = self.repository.find_by_specialization(query)

        # Combine and deduplicate results
        all_results = {p.id: p for p in name_results + spec_results}
        return list(all_results.values())

    def deactivate_practitioner(self, practitioner_id: UUID) -> bool:
        """
        Deactivate a practitioner instead of deleting.

        Args:
            practitioner_id: UUID of the practitioner

        Returns:
            True if deactivated successfully, False otherwise
        """
        updated = self.update(practitioner_id, {'active': False})
        return updated is not None
