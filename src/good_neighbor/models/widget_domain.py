"""Widget domain model (frozen dataclass)."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .types import HomepageId, WidgetId


class WidgetType(str, Enum):
    """Widget type enumeration."""

    IFRAME = "iframe"
    SHORTCUT = "shortcut"
    QUERY = "query"
    # Future: WEATHER, RSS, CUSTOM, etc.


@dataclass(frozen=True)
class Widget:
    """Widget domain model (immutable).

    Represents a widget displayed on a homepage.
    Properties are stored as a dict and validated by Pydantic schemas
    in the API layer.

    Attributes:
        widget_id: Unique widget identifier
        homepage_id: ID of the homepage this widget belongs to
        type: Widget type (iframe, shortcut, etc.)
        position: Display order (lower values displayed first)
        properties: Widget-specific properties (validated by schema)
        created_at: Timestamp when widget was created
        updated_at: Timestamp when widget was last updated
    """

    widget_id: WidgetId
    homepage_id: HomepageId
    type: WidgetType
    position: int
    properties: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def with_position(self, position: int) -> "Widget":
        """Create a new Widget with updated position.

        Since Widget is immutable, this returns a new instance.

        Args:
            position: The new position

        Returns:
            New Widget instance with updated position and updated_at
        """
        return Widget(
            widget_id=self.widget_id,
            homepage_id=self.homepage_id,
            type=self.type,
            position=position,
            properties=self.properties,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def with_properties(self, properties: dict[str, Any]) -> "Widget":
        """Create a new Widget with updated properties.

        Args:
            properties: The new properties dict

        Returns:
            New Widget instance with updated properties and updated_at
        """
        return Widget(
            widget_id=self.widget_id,
            homepage_id=self.homepage_id,
            type=self.type,
            position=self.position,
            properties=properties,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        title = self.properties.get("title", "Untitled")
        return f"Widget({self.type.value}: {title}, id={self.widget_id})"


# Export both WidgetType and Widget
__all__ = ["WidgetType", "Widget"]
