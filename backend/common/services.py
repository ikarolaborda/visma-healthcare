"""
Service Layer Pattern implementation for business logic encapsulation.

The Service Layer Pattern encapsulates business logic and coordinates
between repositories, external services, and domain operations.

Benefits:
- Single Responsibility: Each service handles a specific business domain
- Open/Closed: Easy to extend with new services without modifying existing ones
- Dependency Inversion: Services depend on repository abstractions
- Testability: Business logic can be tested independently
- Reusability: Services can be reused across different views/endpoints
"""

from abc import ABC
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID
from django.db import models, transaction
from django.core.exceptions import ValidationError
import logging

from .repositories import BaseRepository

# Type variable for generic model
T = TypeVar('T', bound=models.Model)

logger = logging.getLogger(__name__)


class BaseService(ABC, Generic[T]):
    """
    Abstract base service implementing common business logic patterns.

    This class follows the Service Layer Pattern and provides a framework
    for implementing business logic that coordinates between repositories,
    validates data, and manages transactions.

    Services should:
    - Contain business logic and validation
    - Coordinate between multiple repositories
    - Handle transaction boundaries
    - Emit events/notifications
    - NOT contain data access code (use repositories)

    Type Parameters:
        T: The Django model type this service manages

    Example:
        class PatientService(BaseService[Patient]):
            def __init__(self, patient_repo: PatientRepository):
                super().__init__(patient_repo)

            def register_patient(self, patient_data: dict) -> Patient:
                self.validate_patient_data(patient_data)
                return self.create(patient_data)

            def validate_patient_data(self, data: dict) -> None:
                if not data.get('birth_date'):
                    raise ValidationError('Birth date is required')
    """

    def __init__(self, repository: BaseRepository[T]):
        """
        Initialize service with required repository.

        Args:
            repository: The repository instance for data access
        """
        self.repository = repository

    # ==================== READ OPERATIONS ====================

    def get_by_id(self, id: UUID) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            id: The UUID primary key

        Returns:
            The entity if found, None otherwise
        """
        return self.repository.get_by_id(id)

    def get_all(self, limit: Optional[int] = None) -> List[T]:
        """
        Retrieve all entities.

        Args:
            limit: Optional maximum number of entities to return

        Returns:
            List of entities
        """
        return list(self.repository.get_all(limit=limit))

    def filter_by(self, **criteria) -> List[T]:
        """
        Filter entities by given criteria.

        Args:
            **criteria: Filter criteria as keyword arguments

        Returns:
            List of filtered entities
        """
        return list(self.repository.filter_by(**criteria))

    def exists(self, **criteria) -> bool:
        """
        Check if entity exists matching criteria.

        Args:
            **criteria: Filter criteria as keyword arguments

        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists(**criteria)

    def count(self, **criteria) -> int:
        """
        Count entities matching criteria.

        Args:
            **criteria: Filter criteria as keyword arguments

        Returns:
            Number of matching entities
        """
        return self.repository.count(**criteria)

    # ==================== WRITE OPERATIONS ====================

    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity with validation.

        Args:
            data: Entity data as dictionary

        Returns:
            The created entity

        Raises:
            ValidationError: If validation fails
        """
        # Validate data before creation
        self.validate_create(data)

        # Pre-processing hook
        data = self.before_create(data)

        # Create entity
        instance = self.repository.create(**data)

        # Post-processing hook
        self.after_create(instance)

        logger.info(
            f"{self.repository.model.__name__} created: {instance.id}"
        )

        return instance

    @transaction.atomic
    def update(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing entity with validation.

        Args:
            id: The UUID primary key
            data: Updated data as dictionary

        Returns:
            The updated entity if found, None otherwise

        Raises:
            ValidationError: If validation fails
        """
        # Check if entity exists
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        # Validate update data
        self.validate_update(existing, data)

        # Pre-processing hook
        data = self.before_update(existing, data)

        # Update entity
        updated = self.repository.update(id, **data)

        # Post-processing hook
        if updated:
            self.after_update(updated)

            logger.info(
                f"{self.repository.model.__name__} updated: {updated.id}"
            )

        return updated

    @transaction.atomic
    def delete(self, id: UUID) -> bool:
        """
        Delete an entity by ID.

        Args:
            id: The UUID primary key

        Returns:
            True if deleted, False if not found

        Raises:
            ValidationError: If deletion is not allowed
        """
        # Check if entity exists
        existing = self.repository.get_by_id(id)
        if not existing:
            return False

        # Validate deletion
        self.validate_delete(existing)

        # Pre-processing hook
        self.before_delete(existing)

        # Delete entity
        deleted = self.repository.delete(id)

        # Post-processing hook
        if deleted:
            self.after_delete(id)

            logger.info(
                f"{self.repository.model.__name__} deleted: {id}"
            )

        return deleted

    # ==================== VALIDATION HOOKS ====================

    def validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creation.

        Override this method to add custom validation logic.

        Args:
            data: Entity data to validate

        Raises:
            ValidationError: If validation fails
        """
        pass

    def validate_update(self, existing: T, data: Dict[str, Any]) -> None:
        """
        Validate data before update.

        Override this method to add custom validation logic.

        Args:
            existing: The existing entity
            data: Updated data to validate

        Raises:
            ValidationError: If validation fails
        """
        pass

    def validate_delete(self, existing: T) -> None:
        """
        Validate before deletion.

        Override this method to add custom validation logic.

        Args:
            existing: The entity to be deleted

        Raises:
            ValidationError: If deletion is not allowed
        """
        pass

    # ==================== LIFECYCLE HOOKS ====================

    def before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pre-processing hook before entity creation.

        Override this method to modify data before creation.

        Args:
            data: Entity data

        Returns:
            Modified entity data
        """
        return data

    def after_create(self, instance: T) -> None:
        """
        Post-processing hook after entity creation.

        Override this method to perform actions after creation
        (e.g., send notifications, create related entities).

        Args:
            instance: The created entity
        """
        pass

    def before_update(self, existing: T, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pre-processing hook before entity update.

        Override this method to modify data before update.

        Args:
            existing: The existing entity
            data: Updated data

        Returns:
            Modified update data
        """
        return data

    def after_update(self, instance: T) -> None:
        """
        Post-processing hook after entity update.

        Override this method to perform actions after update
        (e.g., send notifications, update related entities).

        Args:
            instance: The updated entity
        """
        pass

    def before_delete(self, instance: T) -> None:
        """
        Pre-processing hook before entity deletion.

        Override this method to perform cleanup before deletion.

        Args:
            instance: The entity to be deleted
        """
        pass

    def after_delete(self, id: UUID) -> None:
        """
        Post-processing hook after entity deletion.

        Override this method to perform cleanup after deletion
        (e.g., delete related entities, send notifications).

        Args:
            id: The ID of the deleted entity
        """
        pass

    # ==================== PAGINATION ====================

    def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        **filters
    ) -> Dict[str, Any]:
        """
        Paginate entities with optional filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            **filters: Optional filter criteria

        Returns:
            Pagination result dictionary
        """
        return self.repository.paginate(page, page_size, **filters)
