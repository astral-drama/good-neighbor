"""Widget data models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class WidgetType(str, Enum):
    """Widget type enumeration."""

    IFRAME = "iframe"
    SHORTCUT = "shortcut"
    # Future: WEATHER, RSS, CUSTOM, etc.


class Widget(BaseModel):
    """Base widget model."""

    id: str = Field(..., description="Unique widget identifier (UUID)")
    type: WidgetType = Field(..., description="Widget type")
    position: int = Field(default=0, description="Display order (lower values first)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Widget-specific properties")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IframeWidgetProperties(BaseModel):
    """Properties for iframe widgets."""

    url: HttpUrl = Field(..., description="URL to embed in iframe")
    title: str = Field(..., description="Widget title")
    width: int = Field(default=400, ge=100, le=2000, description="Width in pixels")
    height: int = Field(default=300, ge=100, le=2000, description="Height in pixels")
    refresh_interval: Optional[int] = Field(
        default=None, ge=5, description="Auto-refresh interval in seconds (None = no refresh)"
    )


class ShortcutWidgetProperties(BaseModel):
    """Properties for shortcut widgets."""

    url: HttpUrl = Field(..., description="Link URL")
    title: str = Field(..., description="Link title")
    icon: str = Field(default="🔗", description="Icon (emoji or URL)")
    description: Optional[str] = Field(default=None, description="Optional description")


class CreateWidgetRequest(BaseModel):
    """Request model for creating a widget."""

    type: WidgetType = Field(..., description="Widget type to create")
    properties: dict[str, Any] = Field(..., description="Widget properties")
    position: Optional[int] = Field(default=None, description="Display position (auto-assigned if not provided)")


class UpdateWidgetRequest(BaseModel):
    """Request model for updating a widget."""

    properties: dict[str, Any] = Field(..., description="Updated widget properties")


class UpdatePositionRequest(BaseModel):
    """Request model for updating widget position."""

    position: int = Field(..., ge=0, description="New position index")
