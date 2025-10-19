"""YAML implementation of HomepageRepository."""

from typing import Callable

from good_neighbor.effects import IO, Effect, ErrorDetails, Failure, Result, Success
from good_neighbor.models import Homepage, HomepageId, UserId

from .homepage_repository import HomepageRepository
from .yaml_storage import YAMLStorage


class YAMLHomepageRepository(HomepageRepository):
    """YAML-based implementation of HomepageRepository.

    Stores homepages in storage.yaml file using YAMLStorage.
    All operations return IO[Result[ErrorDetails, A]] for composability.
    """

    def __init__(self, storage: YAMLStorage) -> None:
        """Initialize repository.

        Args:
            storage: Shared YAMLStorage instance
        """
        self.storage = storage

    def get(self, id: HomepageId) -> IO[Result[ErrorDetails, Homepage | None]]:
        """Retrieve a homepage by ID."""

        def _get() -> Result[ErrorDetails, Homepage | None]:
            try:
                homepages = self.storage.get_homepages()
                homepage = homepages.get(str(id))
                return Success(homepage)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR", message=f"Failed to get homepage: {e}", details={"homepage_id": str(id)}
                    )
                )

        return Effect(_get)

    def insert(self, entity: Homepage) -> IO[Result[ErrorDetails, HomepageId]]:
        """Insert a new homepage."""

        def _insert() -> Result[ErrorDetails, HomepageId]:
            try:
                # Check if homepage already exists
                homepages = self.storage.get_homepages()
                if str(entity.homepage_id) in homepages:
                    return Failure(
                        ErrorDetails(
                            code="DUPLICATE_ID",
                            message="Homepage with this ID already exists",
                            details={"homepage_id": str(entity.homepage_id)},
                        )
                    )

                # Insert homepage
                self.storage.set_homepage(entity)
                self.storage.save()

                return Success(entity.homepage_id)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to insert homepage: {e}",
                        details={"homepage_id": str(entity.homepage_id)},
                    )
                )

        return Effect(_insert)

    def update(self, id: HomepageId, f: Callable[[Homepage], Homepage]) -> IO[Result[ErrorDetails, None]]:
        """Update a homepage using a pure function."""

        def _update() -> Result[ErrorDetails, None]:
            try:
                homepages = self.storage.get_homepages()
                homepage = homepages.get(str(id))

                if homepage is None:
                    return Failure(
                        ErrorDetails(code="NOT_FOUND", message="Homepage not found", details={"homepage_id": str(id)})
                    )

                # Apply update function
                updated_homepage = f(homepage)

                # Save updated homepage
                self.storage.set_homepage(updated_homepage)
                self.storage.save()

                return Success(None)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to update homepage: {e}",
                        details={"homepage_id": str(id)},
                    )
                )

        return Effect(_update)

    def delete(self, id: HomepageId) -> IO[Result[ErrorDetails, None]]:
        """Delete a homepage by ID (idempotent)."""

        def _delete() -> Result[ErrorDetails, None]:
            try:
                self.storage.delete_homepage(str(id))
                self.storage.save()
                return Success(None)  # Idempotent: success even if not found
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to delete homepage: {e}",
                        details={"homepage_id": str(id)},
                    )
                )

        return Effect(_delete)

    def list(self) -> IO[Result[ErrorDetails, list[Homepage]]]:
        """List all homepages."""

        def _list() -> Result[ErrorDetails, list[Homepage]]:
            try:
                homepages = self.storage.get_homepages()
                return Success(list(homepages.values()))
            except Exception as e:
                return Failure(ErrorDetails(code="STORAGE_ERROR", message=f"Failed to list homepages: {e}"))

        return Effect(_list)

    def list_by_user(self, user_id: UserId) -> IO[Result[ErrorDetails, list[Homepage]]]:
        """List all homepages for a specific user."""

        def _list_by_user() -> Result[ErrorDetails, list[Homepage]]:
            try:
                homepages = self.storage.get_homepages()
                user_homepages = [hp for hp in homepages.values() if hp.user_id == user_id]
                return Success(user_homepages)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to list homepages for user: {e}",
                        details={"user_id": str(user_id)},
                    )
                )

        return Effect(_list_by_user)

    def get_default_for_user(self, user_id: UserId) -> IO[Result[ErrorDetails, Homepage | None]]:
        """Get the default homepage for a user."""

        def _get_default() -> Result[ErrorDetails, Homepage | None]:
            try:
                homepages = self.storage.get_homepages()
                default_homepage = next(
                    (hp for hp in homepages.values() if hp.user_id == user_id and hp.is_default), None
                )
                return Success(default_homepage)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to get default homepage: {e}",
                        details={"user_id": str(user_id)},
                    )
                )

        return Effect(_get_default)
