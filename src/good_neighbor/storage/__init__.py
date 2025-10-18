"""Storage layer with generic repository pattern.

This package provides:
- Generic Repository[Entity, Id] protocol
- Specialized repository protocols (UserRepository, HomepageRepository, WidgetRepository)
- YAML backend implementation
- Repository factory functions
"""

from .base import Repository
from .homepage_repository import HomepageRepository
from .user_repository import UserRepository
from .widget_repository import WidgetRepository

__all__ = [
    "Repository",
    "UserRepository",
    "HomepageRepository",
    "WidgetRepository",
]
