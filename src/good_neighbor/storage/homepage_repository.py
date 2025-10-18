"""Homepage repository protocol."""

from abc import abstractmethod

from good_neighbor.effects import IO, ErrorDetails, Result
from good_neighbor.models import Homepage, HomepageId, UserId

from .base import Repository


class HomepageRepository(Repository[Homepage, HomepageId]):
    """Repository for Homepage entities.

    Extends the generic Repository[Homepage, HomepageId] protocol with homepage-specific queries.

    All generic repository laws apply:
    - Get-Insert: inserting then getting returns the homepage
    - Update-Get: updating then getting returns the updated homepage
    - Delete-Get: deleting then getting returns None
    - Idempotent Delete: deleting twice succeeds

    Additional domain rules (enforced at service layer):
    - A user must always have at least one homepage
    - Only one homepage can be marked as default per user
    - Deleting a default homepage requires setting a new default first

    Example:
        >>> homepage_repo: HomepageRepository = YAMLHomepageRepository(storage)
        >>>
        >>> # Generic operations
        >>> result = homepage_repo.get(HomepageId("home-123")).run()
        >>>
        >>> # Specialized operations - list all homepages for a user
        >>> user_homepages = homepage_repo.list_by_user(UserId("user-123")).run()
    """

    @abstractmethod
    def list_by_user(self, user_id: UserId) -> IO[Result[ErrorDetails, list[Homepage]]]:
        """List all homepages for a specific user.

        Args:
            user_id: The user ID to filter by

        Returns:
            IO containing Result with list of user's homepages or error

        Example:
            >>> result = homepage_repo.list_by_user(user_id).run()
            >>> match result:
            ...     case Success(homepages):
            ...         for hp in homepages:
            ...             print(f"{hp.name} (default: {hp.is_default})")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...

    @abstractmethod
    def get_default_for_user(self, user_id: UserId) -> IO[Result[ErrorDetails, Homepage | None]]:
        """Get the default homepage for a user.

        Args:
            user_id: The user ID

        Returns:
            IO containing Result with default homepage or None if user has no homepages

        Example:
            >>> result = homepage_repo.get_default_for_user(user_id).run()
            >>> match result:
            ...     case Success(Some(homepage)):
            ...         print(f"Default: {homepage.name}")
            ...     case Success(None):
            ...         print("No default homepage")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...
