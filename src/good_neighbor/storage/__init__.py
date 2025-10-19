"""Storage layer with generic repository pattern.

This package provides:
- Generic Repository[Entity, Id] protocol
- Specialized repository protocols (UserRepository, HomepageRepository, WidgetRepository)
- YAML backend implementation
- Repository factory functions
"""

from .base import Repository
from .factory import Repositories, create_yaml_repositories
from .homepage_repository import HomepageRepository
from .user_repository import UserRepository
from .widget_repository import WidgetRepository
from .yaml_homepage_repository import YAMLHomepageRepository
from .yaml_storage import YAMLStorage
from .yaml_user_repository import YAMLUserRepository
from .yaml_widget_repository import YAMLWidgetRepository

__all__ = [
    # Generic protocols
    "Repository",
    "UserRepository",
    "HomepageRepository",
    "WidgetRepository",
    # YAML implementations
    "YAMLStorage",
    "YAMLUserRepository",
    "YAMLHomepageRepository",
    "YAMLWidgetRepository",
    # Factory
    "Repositories",
    "create_yaml_repositories",
]
