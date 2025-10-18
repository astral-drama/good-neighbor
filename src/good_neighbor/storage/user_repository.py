"""User repository protocol."""

from abc import abstractmethod

from good_neighbor.effects import IO, ErrorDetails, Result
from good_neighbor.models import User, UserId

from .base import Repository


class UserRepository(Repository[User, UserId]):
    """Repository for User entities.

    Extends the generic Repository[User, UserId] protocol with user-specific operations.

    All generic repository laws apply:
    - Get-Insert: inserting then getting returns the user
    - Update-Get: updating then getting returns the updated user
    - Delete-Get: deleting then getting returns None
    - Idempotent Delete: deleting twice succeeds

    Example:
        >>> user_repo: UserRepository = YAMLUserRepository(storage)
        >>>
        >>> # Generic operations
        >>> result = user_repo.get(UserId("user-123")).run()
        >>>
        >>> # Specialized operations
        >>> default_user = user_repo.get_or_create_default().run()
    """

    @abstractmethod
    def get_or_create_default(self) -> IO[Result[ErrorDetails, User]]:
        """Get or create the default user.

        For single-user applications, this ensures a default user exists.
        Future multi-user implementations can extend this to support authentication.

        Returns:
            IO containing Result with the default user or error

        Example:
            >>> result = user_repo.get_or_create_default().run()
            >>> match result:
            ...     case Success(user):
            ...         print(f"User: {user.username}")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
