"""Data models for Good Neighbor.

Domain models (frozen dataclasses):
- User: User account
- Homepage: Collection of widgets
- Widget: Individual widget

Phantom types for type safety:
- UserId, HomepageId, WidgetId

Legacy Pydantic models (widget.py) are kept for backwards compatibility
but should be migrated to use the new domain models.
"""

# Phantom types
# Domain models
from .homepage import Homepage
from .types import HomepageId, UserId, WidgetId
from .user import User

# Legacy Pydantic models (for backwards compat)
from .widget import (
    CreateWidgetRequest,
    IframeWidgetProperties,
    ShortcutWidgetProperties,
    UpdatePositionRequest,
    UpdateWidgetRequest,
)
from .widget import (
    Widget as LegacyWidget,
)
from .widget import (
    WidgetType as LegacyWidgetType,
)
from .widget_domain import Widget, WidgetType

__all__ = [
    # Phantom types
    "UserId",
    "HomepageId",
    "WidgetId",
    # Domain models
    "User",
    "Homepage",
    "Widget",
    "WidgetType",
    # Legacy models
    "LegacyWidget",
    "LegacyWidgetType",
    "IframeWidgetProperties",
    "ShortcutWidgetProperties",
    "CreateWidgetRequest",
    "UpdateWidgetRequest",
    "UpdatePositionRequest",
]
