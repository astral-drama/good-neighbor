"""Factory functions for creating repository instances."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .homepage_repository import HomepageRepository
from .user_repository import UserRepository
from .widget_repository import WidgetRepository
from .yaml_homepage_repository import YAMLHomepageRepository
from .yaml_storage import YAMLStorage
from .yaml_user_repository import YAMLUserRepository
from .yaml_widget_repository import YAMLWidgetRepository


@dataclass(frozen=True)
class Repositories:
    """Container for all repository instances.

    All repositories share the same YAMLStorage instance, ensuring
    consistency and atomic operations across entity types.

    Example:
        >>> repos = create_yaml_repositories("storage.yaml")
        >>> user = repos.users.get_or_create_default().run()
        >>> homepages = repos.homepages.list_by_user(user.user_id).run()
    """

    users: UserRepository
    homepages: HomepageRepository
    widgets: WidgetRepository
    storage: YAMLStorage


def create_yaml_repositories(file_path: str | Path = "storage.yaml") -> Repositories:
    """Create YAML-backed repository instances.

    Creates a shared YAMLStorage instance and repository implementations
    that use it. The storage is automatically loaded on first access.

    Args:
        file_path: Path to storage.yaml file (default: "storage.yaml")

    Returns:
        Repositories container with all repository instances

    Example:
        >>> repos = create_yaml_repositories("data/storage.yaml")
        >>> repos.storage.load()  # Optional: load data immediately
        >>>
        >>> # Use repositories
        >>> result = repos.users.get_or_create_default().run()
        >>> match result:
        ...     case Success(user):
        ...         print(f"User: {user.username}")
        ...     case Failure(error):
        ...         print(f"Error: {error}")
    """
    # Create shared storage instance
    storage = YAMLStorage(file_path)

    # Create repository instances sharing the same storage
    return Repositories(
        users=YAMLUserRepository(storage),
        homepages=YAMLHomepageRepository(storage),
        widgets=YAMLWidgetRepository(storage),
        storage=storage,
    )
