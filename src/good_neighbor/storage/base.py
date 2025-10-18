"""Generic repository pattern following category theory principles.

The Repository[Entity, Id] protocol defines a generic interface for CRUD operations
that satisfies mathematical laws, enabling composability and correctness guarantees.
"""

from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

from good_neighbor.effects import IO, ErrorDetails, Result

Entity = TypeVar("Entity")
Id = TypeVar("Id")


class Repository(ABC, Generic[Entity, Id]):
    """Generic repository protocol following SOLID principles.

    This protocol defines the contract for all repositories, providing:
    - Type-safe CRUD operations
    - Algebraic error handling via Result[E, A]
    - Suspended side effects via IO[A]
    - Mathematical laws that all implementations must satisfy

    Repository Laws:
    ----------------

    **Get-Insert Law**: Inserting then getting returns the entity
        repo.insert(e).flat_map(id => repo.get(id)) == IO[Result[E, Some(e)]]

    **Update-Get Law**: Updating then getting returns the updated entity
        repo.update(id, f).flat_map(_ => repo.get(id)) == IO[Result[E, Some(f(original))]]

    **Delete-Get Law**: Deleting then getting returns None
        repo.delete(id).flat_map(_ => repo.get(id)) == IO[Result[E, None]]

    **Idempotent Delete Law**: Deleting twice succeeds
        repo.delete(id).flat_map(_ => repo.delete(id)) == IO[Result[E, Success(None)]]

    These laws are verified by property-based tests to ensure correctness.

    Type Parameters:
        Entity: The domain entity type (e.g., User, Homepage, Widget)
        Id: The ID type (e.g., UserId, HomepageId, WidgetId)

    Example:
        >>> # Generic repository can be used with any entity type
        >>> user_repo: Repository[User, UserId] = YAMLUserRepository(storage)
        >>> homepage_repo: Repository[Homepage, HomepageId] = YAMLHomepageRepository(storage)
        >>>
        >>> # All repositories have the same interface
        >>> def get_by_id(repo: Repository[E, I], id: I) -> IO[Result[ErrorDetails, E | None]]:
        ...     return repo.get(id)
    """

    @abstractmethod
    def get(self, id: Id) -> IO[Result[ErrorDetails, Entity | None]]:
        """Retrieve an entity by ID.

        Args:
            id: The entity ID

        Returns:
            IO containing Result with entity if found, None if not found, or error

        Example:
            >>> user_id = UserId("user-123")
            >>> result = user_repo.get(user_id).run()
            >>> match result:
            ...     case Success(Some(user)):
            ...         print(f"Found: {user}")
            ...     case Success(None):
            ...         print("Not found")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """

    @abstractmethod
    def insert(self, entity: Entity) -> IO[Result[ErrorDetails, Id]]:
        """Insert a new entity.

        Args:
            entity: The entity to insert

        Returns:
            IO containing Result with the inserted entity's ID or error

        Example:
            >>> user = User(
            ...     user_id=UserId(str(uuid4())),
            ...     username="alice",
            ...     default_homepage_id=None,
            ...     created_at=datetime.now(timezone.utc),
            ...     updated_at=datetime.now(timezone.utc),
            ... )
            >>> result = user_repo.insert(user).run()
            >>> match result:
            ...     case Success(user_id):
            ...         print(f"Inserted with ID: {user_id}")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...

    @abstractmethod
    def update(self, id: Id, f: Callable[[Entity], Entity]) -> IO[Result[ErrorDetails, None]]:
        """Update an entity using a pure function.

        This method follows functional programming principles:
        - The update function `f` is pure (no side effects)
        - Immutability: entities are frozen dataclasses
        - The function returns a new entity with changes

        Args:
            id: The entity ID
            f: Pure function that transforms the entity

        Returns:
            IO containing Result with None on success or error

        Example:
            >>> # Update user's default homepage
            >>> def set_default(user: User) -> User:
            ...     return user.with_default_homepage(HomepageId("home-1"))
            >>>
            >>> result = user_repo.update(user_id, set_default).run()
            >>> match result:
            ...     case Success(None):
            ...         print("Updated successfully")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...

    @abstractmethod
    def delete(self, id: Id) -> IO[Result[ErrorDetails, None]]:
        """Delete an entity by ID.

        Satisfies idempotent delete law: deleting a non-existent entity succeeds.

        Args:
            id: The entity ID

        Returns:
            IO containing Result with None on success or error

        Example:
            >>> result = user_repo.delete(user_id).run()
            >>> match result:
            ...     case Success(None):
            ...         print("Deleted successfully")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...

    @abstractmethod
    def list(self) -> IO[Result[ErrorDetails, list[Entity]]]:
        """List all entities.

        Returns:
            IO containing Result with list of all entities or error

        Example:
            >>> result = user_repo.list().run()
            >>> match result:
            ...     case Success(users):
            ...         print(f"Found {len(users)} users")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...
