"""Homepage service with business logic."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from good_neighbor.effects import IO, Effect, ErrorDetails, Failure, Result
from good_neighbor.models import Homepage, HomepageId, UserId
from good_neighbor.storage import HomepageRepository


class HomepageService:
    """Service for homepage-related business logic.

    Composes repository operations using IO/Result monads.
    Enforces business rules:
    - Cannot delete the last homepage for a user
    - Only one homepage can be marked as default per user

    Example:
        >>> repos = create_yaml_repositories()
        >>> service = HomepageService(repos.homepages)
        >>> result = service.create_homepage(user_id, "Work").run()
    """

    def __init__(self, homepage_repo: HomepageRepository) -> None:
        """Initialize service with repository.

        Args:
            homepage_repo: HomepageRepository instance
        """
        self.homepage_repo = homepage_repo

    def get_homepage(self, homepage_id: HomepageId) -> IO[Result[ErrorDetails, Homepage | None]]:
        """Get a homepage by ID.

        Args:
            homepage_id: The homepage ID to retrieve

        Returns:
            IO containing Result with homepage if found, None if not found, or error
        """
        return self.homepage_repo.get(homepage_id)

    def list_homepages_for_user(self, user_id: UserId) -> IO[Result[ErrorDetails, list[Homepage]]]:
        """List all homepages for a specific user.

        Args:
            user_id: The user ID

        Returns:
            IO containing Result with list of homepages or error
        """
        return self.homepage_repo.list_by_user(user_id)

    def get_default_homepage(self, user_id: UserId) -> IO[Result[ErrorDetails, Homepage | None]]:
        """Get the default homepage for a user.

        Args:
            user_id: The user ID

        Returns:
            IO containing Result with default homepage if found, None otherwise, or error
        """
        return self.homepage_repo.get_default_for_user(user_id)

    def create_homepage(
        self, user_id: UserId, name: str, is_default: bool = False
    ) -> IO[Result[ErrorDetails, Homepage]]:
        """Create a new homepage for a user.

        If is_default=True, unsets any existing default homepage for the user.

        Args:
            user_id: The user ID
            name: Homepage name
            is_default: Whether this should be the default homepage

        Returns:
            IO containing Result with created homepage or error

        Example:
            >>> result = service.create_homepage(user_id, "Work", is_default=True).run()
            >>> match result:
            ...     case Success(homepage):
            ...         print(f"Created: {homepage.name}")
            ...     case Failure(error):
            ...         print(f"Error: {error.message}")
        """
        now = datetime.now(timezone.utc)
        new_homepage = Homepage(
            homepage_id=HomepageId(str(uuid4())),
            user_id=user_id,
            name=name,
            is_default=is_default,
            created_at=now,
            updated_at=now,
        )

        if not is_default:
            # Simple case: just insert the homepage
            return self.homepage_repo.insert(new_homepage).map(lambda _: new_homepage)

        # If setting as default, unset existing default first
        def _create_default(existing: Homepage | None) -> IO[Result[ErrorDetails, Homepage]]:
            if existing is None:
                # No existing default, just insert
                return self.homepage_repo.insert(new_homepage).map(lambda _: new_homepage)

            # Unset existing default, then insert new one
            return self.homepage_repo.update(existing.homepage_id, lambda hp: hp.unset_as_default()).flat_map(
                lambda _: self.homepage_repo.insert(new_homepage).map(lambda _: new_homepage)
            )

        return self.homepage_repo.get_default_for_user(user_id).flat_map(
            lambda result: result.flat_map(_create_default)
        )

    def update_homepage_name(self, homepage_id: HomepageId, new_name: str) -> IO[Result[ErrorDetails, None]]:
        """Update a homepage's name.

        Args:
            homepage_id: The homepage ID
            new_name: New name for the homepage

        Returns:
            IO containing Result with None on success or error
        """
        return self.homepage_repo.update(homepage_id, lambda hp: hp.with_name(new_name))

    def set_default_homepage(self, homepage_id: HomepageId, user_id: UserId) -> IO[Result[ErrorDetails, None]]:
        """Set a homepage as the default for a user.

        Unsets any existing default homepage for the user first.

        Args:
            homepage_id: The homepage ID to set as default
            user_id: The user ID (for validation)

        Returns:
            IO containing Result with None on success or error
        """

        def _set_default(homepage: Homepage | None) -> IO[Result[ErrorDetails, None]]:
            if homepage is None:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="NOT_FOUND", message="Homepage not found", details={"homepage_id": str(homepage_id)}
                        )
                    )
                )

            if homepage.user_id != user_id:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="FORBIDDEN",
                            message="Homepage does not belong to user",
                            details={"homepage_id": str(homepage_id), "user_id": str(user_id)},
                        )
                    )
                )

            # Get existing default and unset it
            def _unset_and_set(existing_default: Homepage | None) -> IO[Result[ErrorDetails, None]]:
                if existing_default is None or existing_default.homepage_id == homepage_id:
                    # No existing default or already default, just set this one
                    return self.homepage_repo.update(homepage_id, lambda hp: hp.set_as_default())

                # Unset existing default, then set new one
                return self.homepage_repo.update(
                    existing_default.homepage_id, lambda hp: hp.unset_as_default()
                ).flat_map(lambda _: self.homepage_repo.update(homepage_id, lambda hp: hp.set_as_default()))

            return self.homepage_repo.get_default_for_user(user_id).flat_map(
                lambda result: result.flat_map(_unset_and_set)
            )

        return self.homepage_repo.get(homepage_id).flat_map(lambda result: result.flat_map(_set_default))

    def delete_homepage(self, homepage_id: HomepageId, user_id: UserId) -> IO[Result[ErrorDetails, None]]:
        """Delete a homepage.

        Business rule: Cannot delete the last homepage for a user.

        Args:
            homepage_id: The homepage ID to delete
            user_id: The user ID (for validation and business rule checking)

        Returns:
            IO containing Result with None on success or error
        """

        def _validate_and_delete(homepages: list[Homepage]) -> IO[Result[ErrorDetails, None]]:
            # Check if homepage exists and belongs to user
            homepage = next((hp for hp in homepages if hp.homepage_id == homepage_id), None)

            if homepage is None:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="NOT_FOUND", message="Homepage not found", details={"homepage_id": str(homepage_id)}
                        )
                    )
                )

            if homepage.user_id != user_id:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="FORBIDDEN",
                            message="Homepage does not belong to user",
                            details={"homepage_id": str(homepage_id), "user_id": str(user_id)},
                        )
                    )
                )

            # Business rule: cannot delete last homepage
            user_homepages = [hp for hp in homepages if hp.user_id == user_id]
            if len(user_homepages) <= 1:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="BUSINESS_RULE_VIOLATION",
                            message="Cannot delete the last homepage for a user",
                            details={"homepage_id": str(homepage_id), "user_id": str(user_id)},
                        )
                    )
                )

            # All validations passed, delete the homepage
            return self.homepage_repo.delete(homepage_id)

        return self.homepage_repo.list().flat_map(lambda result: result.flat_map(_validate_and_delete))
