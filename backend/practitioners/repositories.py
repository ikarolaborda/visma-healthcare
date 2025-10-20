"""
Repository layer for Practitioner data access.

This module implements the Repository Pattern for Practitioner models,
providing a clean abstraction over data access operations.
"""

from typing import Optional, List
from common.repositories import BaseRepository
from .models import Practitioner


class PractitionerRepository(BaseRepository[Practitioner]):
    """
    Repository for managing Practitioner data access.

    This class extends BaseRepository to provide Practitioner-specific
    data access methods while inheriting all standard CRUD operations.

    Inherited methods include:
    - get_by_id(id: UUID) -> Optional[Practitioner]
    - get_all(limit: Optional[int]) -> QuerySet[Practitioner]
    - filter_by(**kwargs) -> QuerySet[Practitioner]
    - create(**data) -> Practitioner
    - update(id: UUID, **data) -> Optional[Practitioner]
    - delete(id: UUID) -> bool
    - paginate(page: int, page_size: int, **filters) -> Dict
    """

    model = Practitioner

    def find_by_npi(self, npi: str) -> Optional[Practitioner]:
        """
        Find a practitioner by their National Provider Identifier (NPI).

        Args:
            npi: The National Provider Identifier

        Returns:
            Practitioner instance if found, None otherwise
        """
        return self.find_one(npi=npi)

    def find_by_specialization(self, specialization: str) -> List[Practitioner]:
        """
        Find all practitioners with a specific specialization.

        Args:
            specialization: The medical specialization to search for

        Returns:
            List of Practitioner instances
        """
        return list(self.filter_by(
            specialization__icontains=specialization,
            active=True
        ))

    def find_active_practitioners(self) -> List[Practitioner]:
        """
        Find all active practitioners.

        Returns:
            List of active Practitioner instances
        """
        return list(self.filter_by(active=True))

    def find_by_email(self, email: str) -> Optional[Practitioner]:
        """
        Find a practitioner by their email address.

        Args:
            email: The email address to search for

        Returns:
            Practitioner instance if found, None otherwise
        """
        return self.find_one(email=email)

    def search_by_name(self, name: str) -> List[Practitioner]:
        """
        Search practitioners by name (given or family name).

        Args:
            name: The name to search for (partial match supported)

        Returns:
            List of matching Practitioner instances
        """
        from django.db.models import Q

        return list(self.model.objects.filter(
            Q(given_name__icontains=name) |
            Q(family_name__icontains=name),
            active=True
        ))
