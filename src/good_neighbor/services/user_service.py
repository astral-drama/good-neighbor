"""User service with business logic."""

from __future__ import annotations

from good_neighbor.effects import IO, ErrorDetails, Result
from good_neighbor.models import User, UserId
from good_neighbor.storage import UserRepository


class UserService:
    """Service for user-related business logic.

    Composes repository operations using IO/Result monads.
    All operations are pure functions that return suspended effects.

    Example:
        >>> repos = create_yaml_repositories()
        >>> service = UserService(repos.users)
        >>> result = service.get_or_create_default_user().run()
        >>> match result:
        ...     case Success(user):
        ...         print(f"User: {user.username}")
        ...     case Failure(error):
        ...         print(f"Error: {error}")
    """

    def __init__(self, user_repo: UserRepository) -> None:
        """Initialize service with repository.

        Args:
            user_repo: UserRepository instance
        """
        self.user_repo = user_repo

    def get_or_create_default_user(self) -> IO[Result[ErrorDetails, User]]:
        """Get or create the default user.

        For single-user applications, ensures a default user exists.
        Delegates to repository implementation.

        Returns:
            IO containing Result with the default user or error

        Example:
            >>> result = service.get_or_create_default_user().run()
            >>> match result:
            ...     case Success(user):
            ...         print(f"User ID: {user.user_id}")
            ...     case Failure(error):
            ...         print(f"Error: {error.code}")
        """
        return self.user_repo.get_or_create_default()

    def get_user(self, user_id: UserId) -> IO[Result[ErrorDetails, User | None]]:
        """Get a user by ID.

        Args:
            user_id: The user ID to retrieve

        Returns:
            IO containing Result with user if found, None if not found, or error
        """
        return self.user_repo.get(user_id)

    def list_users(self) -> IO[Result[ErrorDetails, list[User]]]:
        """List all users.

        Returns:
            IO containing Result with list of all users or error
        """
        return self.user_repo.list()
