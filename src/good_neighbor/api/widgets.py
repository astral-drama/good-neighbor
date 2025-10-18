"""Widget API endpoints."""

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from good_neighbor.models.widget import (
    CreateWidgetRequest,
    UpdatePositionRequest,
    UpdateWidgetRequest,
    Widget,
)

logger = logging.getLogger(__name__)

# In-memory widget store
# TODO: Migrate to database (SQLite/PostgreSQL) in future story
widgets_store: dict[str, Widget] = {}

router = APIRouter(prefix="/api/widgets", tags=["widgets"])


@router.get("/")  # type: ignore[misc]
async def list_widgets() -> list[Widget]:
    """Get all widgets sorted by position.

    Returns:
        list[Widget]: All widgets ordered by position
    """
    logger.info("Listing all widgets - count: %d", len(widgets_store))
    return sorted(widgets_store.values(), key=lambda w: w.position)


@router.post("/")  # type: ignore[misc]
async def create_widget(request: CreateWidgetRequest) -> Widget:
    """Create a new widget.

    Args:
        request: Widget creation request with type and properties

    Returns:
        Widget: The created widget

    Raises:
        HTTPException: If widget creation fails
    """
    widget_id = str(uuid4())

    # Auto-assign position if not provided
    if request.position is None:
        positions = [w.position for w in widgets_store.values()] if widgets_store else [0]
        position = max(positions) + 1 if positions else 0
    else:
        position = request.position

    widget = Widget(
        id=widget_id,
        type=request.type,
        position=position,
        properties=request.properties,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    widgets_store[widget_id] = widget
    logger.info("Created widget - id: %s, type: %s, position: %d", widget_id, request.type, position)

    return widget


@router.get("/{widget_id}")  # type: ignore[misc]
async def get_widget(widget_id: str) -> Widget:
    """Get a specific widget by ID.

    Args:
        widget_id: Widget identifier

    Returns:
        Widget: The requested widget

    Raises:
        HTTPException: If widget not found
    """
    if widget_id not in widgets_store:
        logger.warning("Widget not found - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    return widgets_store[widget_id]


@router.put("/{widget_id}")  # type: ignore[misc]
async def update_widget(widget_id: str, request: UpdateWidgetRequest) -> Widget:
    """Update widget properties.

    Args:
        widget_id: Widget identifier
        request: Updated properties

    Returns:
        Widget: The updated widget

    Raises:
        HTTPException: If widget not found
    """
    if widget_id not in widgets_store:
        logger.warning("Widget not found for update - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    widget = widgets_store[widget_id]
    widget.properties = request.properties
    widget.updated_at = datetime.now(timezone.utc)

    logger.info("Updated widget - id: %s, properties: %s", widget_id, request.properties)

    return widget


@router.patch("/{widget_id}/position")  # type: ignore[misc]
async def update_widget_position(widget_id: str, request: UpdatePositionRequest) -> Widget:
    """Update widget position in the grid.

    Args:
        widget_id: Widget identifier
        request: New position

    Returns:
        Widget: The updated widget

    Raises:
        HTTPException: If widget not found
    """
    if widget_id not in widgets_store:
        logger.warning("Widget not found for position update - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    widget = widgets_store[widget_id]
    old_position = widget.position
    widget.position = request.position
    widget.updated_at = datetime.now(timezone.utc)

    logger.info("Updated widget position - id: %s, old: %d, new: %d", widget_id, old_position, request.position)

    return widget


@router.delete("/{widget_id}")  # type: ignore[misc]
async def delete_widget(widget_id: str) -> dict[str, Any]:
    """Delete a widget.

    Args:
        widget_id: Widget identifier

    Returns:
        dict: Deletion confirmation

    Raises:
        HTTPException: If widget not found
    """
    if widget_id not in widgets_store:
        logger.warning("Widget not found for deletion - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    del widgets_store[widget_id]
    logger.info("Deleted widget - id: %s", widget_id)

    return {"status": "deleted", "id": widget_id}
