"""
Repository Pattern implementation for data access abstraction.

The Repository Pattern provides a collection-like interface for accessing
domain objects, abstracting the data access layer from business logic.

Benefits:
- Single Responsibility: Separates data access from business logic
- Dependency Inversion: Business logic depends on repository abstractions
- Testability: Easy to mock repositories for unit testing
- Consistency: Standardized data access patterns across the application
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID
from django.db import models
from django.db.models import QuerySet
from django.core.cache import cache
from django.conf import settings

# Type variable for generic model
T = TypeVar('T', bound=models.Model)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository implementing common CRUD operations.

    This class follows the Repository Pattern and provides a generic
    interface for data access operations. Concrete repositories should
    inherit from this class and can override methods as needed.

    Type Parameters:
        T: The Django model type this repository manages

    Example:
        class PatientRepository(BaseRepository[Patient]):
            model = Patient

            def find_by_mrn(self, mrn: str) -> Optional[Patient]:
                return self.model.objects.filter(mrn=mrn).first()
    """

    model: Type[T]
    cache_prefix: str = ""
    cache_ttl: int = 300  # 5 minutes default

    def __init__(self):
        """Initialize repository with model validation."""
        if not hasattr(self, 'model') or not self.model:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a 'model' attribute"
            )
        if not self.cache_prefix:
            self.cache_prefix = self.model.__name__.lower()

    # ==================== READ OPERATIONS ====================

    def get_by_id(self, id: UUID) -> Optional[T]:
        """
        Retrieve a single entity by its primary key.

        Args:
            id: The UUID primary key of the entity

        Returns:
            The entity if found, None otherwise
        """
        cache_key = self._get_cache_key('id', str(id))
        cached = cache.get(cache_key)

        if cached is not None:
            return cached

        instance = self.model.objects.filter(id=id).first()

        if instance:
            cache.set(cache_key, instance, self.cache_ttl)

        return instance

    def get_all(self, limit: Optional[int] = None) -> QuerySet[T]:
        """
        Retrieve all entities, optionally limited.

        Args:
            limit: Maximum number of entities to return

        Returns:
            QuerySet of entities
        """
        queryset = self.model.objects.all()

        if limit:
            queryset = queryset[:limit]

        return queryset

    def filter_by(self, **kwargs) -> QuerySet[T]:
        """
        Filter entities by given criteria.

        Args:
            **kwargs: Filter criteria as keyword arguments

        Returns:
            QuerySet of filtered entities

        Example:
            repository.filter_by(status='active', gender='male')
        """
        return self.model.objects.filter(**kwargs)

    def exists(self, **kwargs) -> bool:
        """
        Check if any entity matches the given criteria.

        Args:
            **kwargs: Filter criteria as keyword arguments

        Returns:
            True if at least one entity exists, False otherwise
        """
        return self.model.objects.filter(**kwargs).exists()

    def count(self, **kwargs) -> int:
        """
        Count entities matching the given criteria.

        Args:
            **kwargs: Filter criteria as keyword arguments

        Returns:
            Number of matching entities
        """
        if kwargs:
            return self.model.objects.filter(**kwargs).count()
        return self.model.objects.count()

    # ==================== WRITE OPERATIONS ====================

    def create(self, **data) -> T:
        """
        Create a new entity.

        Args:
            **data: Entity data as keyword arguments

        Returns:
            The created entity

        Raises:
            ValidationError: If data validation fails
        """
        instance = self.model.objects.create(**data)
        self._invalidate_cache(instance)
        return instance

    def update(self, id: UUID, **data) -> Optional[T]:
        """
        Update an existing entity.

        Args:
            id: The UUID primary key of the entity
            **data: Updated data as keyword arguments

        Returns:
            The updated entity if found, None otherwise
        """
        instance = self.get_by_id(id)

        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        instance.save()
        self._invalidate_cache(instance)

        return instance

    def delete(self, id: UUID) -> bool:
        """
        Delete an entity by its primary key.

        Args:
            id: The UUID primary key of the entity

        Returns:
            True if entity was deleted, False if not found
        """
        instance = self.get_by_id(id)

        if not instance:
            return False

        self._invalidate_cache(instance)
        instance.delete()

        return True

    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple entities in a single database query.

        Args:
            data_list: List of dictionaries containing entity data

        Returns:
            List of created entities
        """
        instances = [self.model(**data) for data in data_list]
        created = self.model.objects.bulk_create(instances)

        # Invalidate cache for all created instances
        for instance in created:
            self._invalidate_cache(instance)

        return created

    # ==================== CACHE OPERATIONS ====================

    def _get_cache_key(self, key_type: str, value: str) -> str:
        """
        Generate a cache key for the given type and value.

        Args:
            key_type: Type of key (e.g., 'id', 'mrn')
            value: The value to include in the key

        Returns:
            The generated cache key
        """
        return f"{self.cache_prefix}:{key_type}:{value}"

    def _invalidate_cache(self, instance: T) -> None:
        """
        Invalidate cache entries for the given instance.

        Args:
            instance: The entity instance to invalidate cache for
        """
        cache_key = self._get_cache_key('id', str(instance.id))
        cache.delete(cache_key)

    # ==================== CUSTOM QUERY HELPERS ====================

    def find_one(self, **kwargs) -> Optional[T]:
        """
        Find a single entity matching the criteria.

        Args:
            **kwargs: Filter criteria as keyword arguments

        Returns:
            The first matching entity or None
        """
        return self.model.objects.filter(**kwargs).first()

    def paginate(self, page: int = 1, page_size: int = 20, **filters) -> Dict[str, Any]:
        """
        Paginate entities with optional filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            **filters: Optional filter criteria

        Returns:
            Dictionary containing:
                - items: List of entities for the current page
                - total: Total number of entities
                - page: Current page number
                - page_size: Items per page
                - total_pages: Total number of pages
        """
        queryset = self.filter_by(**filters) if filters else self.get_all()
        total = queryset.count()

        start = (page - 1) * page_size
        end = start + page_size

        items = list(queryset[start:end])
        total_pages = (total + page_size - 1) // page_size

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
        }
