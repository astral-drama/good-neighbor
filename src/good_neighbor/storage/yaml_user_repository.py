"""YAML implementation of UserRepository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from good_neighbor.effects import IO, Effect, ErrorDetails, Failure, Result, Success
from good_neighbor.models import User, UserId

from .user_repository import UserRepository
from .yaml_storage import YAMLStorage


class YAMLUserRepository(UserRepository):
    """YAML-based implementation of UserRepository.

    Stores users in storage.yaml file using YAMLStorage.
    All operations return IO[Result[ErrorDetails, A]] for composability.
    """

    def __init__(self, storage: YAMLStorage) -> None:
        """Initialize repository.

        Args:
            storage: Shared YAMLStorage instance
        """
        self.storage = storage

    def get(self, id: UserId) -> IO[Result[ErrorDetails, User | None]]:
        """Retrieve a user by ID."""

        def _get() -> Result[ErrorDetails, User | None]:
            try:
                users = self.storage.get_users()
                user = users.get(str(id))
                return Success(user)
            except Exception as e:
                return Failure(
                    ErrorDetails(code="STORAGE_ERROR", message=f"Failed to get user: {e}", details={"user_id": str(id)})
                )

        return Effect(_get)

    def insert(self, entity: User) -> IO[Result[ErrorDetails, UserId]]:
        """Insert a new user."""

        def _insert() -> Result[ErrorDetails, UserId]:
            try:
                # Check if user already exists
                users = self.storage.get_users()
                if str(entity.user_id) in users:
                    return Failure(
                        ErrorDetails(
                            code="DUPLICATE_ID",
                            message="User with this ID already exists",
                            details={"user_id": str(entity.user_id)},
                        )
                    )

                # Insert user
                self.storage.set_user(entity)
                self.storage.save()

                return Success(entity.user_id)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to insert user: {e}",
                        details={"user_id": str(entity.user_id)},
                    )
                )

        return Effect(_insert)

    def update(self, id: UserId, f: Callable[[User], User]) -> IO[Result[ErrorDetails, None]]:
        """Update a user using a pure function."""

        def _update() -> Result[ErrorDetails, None]:
            try:
                users = self.storage.get_users()
                user = users.get(str(id))

                if user is None:
                    return Failure(
                        ErrorDetails(code="NOT_FOUND", message="User not found", details={"user_id": str(id)})
                    )

                # Apply update function
                updated_user = f(user)

                # Save updated user
                self.storage.set_user(updated_user)
                self.storage.save()

                return Success(None)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR", message=f"Failed to update user: {e}", details={"user_id": str(id)}
                    )
                )

        return Effect(_update)

    def delete(self, id: UserId) -> IO[Result[ErrorDetails, None]]:
        """Delete a user by ID (idempotent)."""

        def _delete() -> Result[ErrorDetails, None]:
            try:
                self.storage.delete_user(str(id))
                self.storage.save()
                return Success(None)  # Idempotent: success even if not found
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR", message=f"Failed to delete user: {e}", details={"user_id": str(id)}
                    )
                )

        return Effect(_delete)

    def list(self) -> IO[Result[ErrorDetails, list[User]]]:
        """List all users."""

        def _list() -> Result[ErrorDetails, list[User]]:
            try:
                users = self.storage.get_users()
                return Success(list(users.values()))
            except Exception as e:
                return Failure(ErrorDetails(code="STORAGE_ERROR", message=f"Failed to list users: {e}"))

        return Effect(_list)

    def get_or_create_default(self) -> IO[Result[ErrorDetails, User]]:
        """Get or create the default user."""

        def _get_or_create() -> Result[ErrorDetails, User]:
            try:
                users = self.storage.get_users()

                # Look for existing default user
                default_user = next((u for u in users.values() if u.username == "default"), None)

                if default_user:
                    return Success(default_user)

                # Create default user
                now = datetime.now(timezone.utc)
                new_user = User(
                    user_id=UserId(str(uuid4())),
                    username="default",
                    default_homepage_id=None,
                    created_at=now,
                    updated_at=now,
                )

                self.storage.set_user(new_user)
                self.storage.save()

                return Success(new_user)
            except Exception as e:
                return Failure(ErrorDetails(code="STORAGE_ERROR", message=f"Failed to get or create default user: {e}"))

        return Effect(_get_or_create)
