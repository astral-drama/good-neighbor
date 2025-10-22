"""Widget API endpoints."""

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from good_neighbor.models import HomepageId, WidgetId
from good_neighbor.models.widget import (
    CreateWidgetRequest,
    UpdatePositionRequest,
    UpdateWidgetRequest,
)
from good_neighbor.models.widget import (
    Widget as ApiWidget,
)
from good_neighbor.models.widget_domain import Widget as DomainWidget
from good_neighbor.models.widget_domain import WidgetType
from good_neighbor.storage.shared import get_shared_repositories

logger = logging.getLogger(__name__)

# Initialize repositories and services using shared storage
repos = get_shared_repositories()

router = APIRouter(prefix="/api/widgets", tags=["widgets"])


def _get_default_homepage_id() -> HomepageId:
    """Get the default homepage ID for the default user.

    Returns:
        HomepageId: The default homepage ID

    Raises:
        HTTPException: If no default homepage found
    """
    # Get default user
    users = repos.storage.get_users()
    if not users:
        raise HTTPException(status_code=500, detail="No users found")

    # Get first user (for now, multi-user support in future)
    user = next(iter(users.values()))

    # Get user's default homepage or first homepage
    homepages = repos.storage.get_homepages()
    user_homepages = [hp for hp in homepages.values() if str(hp.user_id) == str(user.user_id)]

    if not user_homepages:
        raise HTTPException(status_code=500, detail="No homepages found for user")

    # Find default homepage or use first one
    default_hp = next((hp for hp in user_homepages if hp.is_default), user_homepages[0])
    return default_hp.homepage_id


def _domain_to_api(domain_widget: DomainWidget) -> ApiWidget:
    """Convert domain Widget to API Widget.

    Args:
        domain_widget: Domain widget model

    Returns:
        ApiWidget: API widget model
    """
    return ApiWidget(
        id=str(domain_widget.widget_id),
        type=domain_widget.type.value,
        position=domain_widget.position,
        properties=domain_widget.properties,
        created_at=domain_widget.created_at,
        updated_at=domain_widget.updated_at,
    )


def _api_to_domain(api_widget: ApiWidget, homepage_id: HomepageId, widget_id: WidgetId) -> DomainWidget:
    """Convert API Widget to domain Widget.

    Args:
        api_widget: API widget model
        homepage_id: Homepage ID to associate with
        widget_id: Widget ID

    Returns:
        DomainWidget: Domain widget model
    """
    return DomainWidget(
        widget_id=widget_id,
        homepage_id=homepage_id,
        type=WidgetType(api_widget.type),
        position=api_widget.position,
        properties=api_widget.properties,
        created_at=api_widget.created_at,
        updated_at=api_widget.updated_at,
    )


@router.get("/")  # type: ignore[misc]
async def list_widgets() -> list[ApiWidget]:
    """Get all widgets sorted by position.

    Returns:
        list[ApiWidget]: All widgets ordered by position
    """
    domain_widgets = repos.storage.get_widgets()
    logger.info("Listing all widgets - count: %d", len(domain_widgets))

    # Convert to API widgets and sort by position
    api_widgets = [_domain_to_api(w) for w in domain_widgets.values()]
    return sorted(api_widgets, key=lambda w: w.position)


@router.post("/")  # type: ignore[misc]
async def create_widget(request: CreateWidgetRequest) -> ApiWidget:
    """Create a new widget.

    Args:
        request: Widget creation request with type and properties

    Returns:
        ApiWidget: The created widget

    Raises:
        HTTPException: If widget creation fails
    """
    widget_id = WidgetId(str(uuid4()))
    homepage_id = _get_default_homepage_id()

    # Auto-assign position if not provided
    domain_widgets = repos.storage.get_widgets()
    if request.position is None:
        positions = [w.position for w in domain_widgets.values()] if domain_widgets else [0]
        position = max(positions) + 1 if positions else 0
    else:
        position = request.position

    # Create domain widget
    domain_widget = DomainWidget(
        widget_id=widget_id,
        homepage_id=homepage_id,
        type=WidgetType(request.type),
        position=position,
        properties=request.properties,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Save to storage
    repos.storage.set_widget(domain_widget)
    repos.storage.save()

    logger.info("Created widget - id: %s, type: %s, position: %d", widget_id, request.type, position)

    return _domain_to_api(domain_widget)


@router.get("/{widget_id}")  # type: ignore[misc]
async def get_widget(widget_id: str) -> ApiWidget:
    """Get a specific widget by ID.

    Args:
        widget_id: Widget identifier

    Returns:
        ApiWidget: The requested widget

    Raises:
        HTTPException: If widget not found
    """
    domain_widgets = repos.storage.get_widgets()
    if widget_id not in domain_widgets:
        logger.warning("Widget not found - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    return _domain_to_api(domain_widgets[widget_id])


@router.put("/{widget_id}")  # type: ignore[misc]
async def update_widget(widget_id: str, request: UpdateWidgetRequest) -> ApiWidget:
    """Update widget properties.

    Args:
        widget_id: Widget identifier
        request: Updated properties

    Returns:
        ApiWidget: The updated widget

    Raises:
        HTTPException: If widget not found
    """
    domain_widgets = repos.storage.get_widgets()
    if widget_id not in domain_widgets:
        logger.warning("Widget not found for update - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    # Use immutable domain model helper method
    old_widget = domain_widgets[widget_id]
    updated_widget = old_widget.with_properties(request.properties)

    # Save to storage
    repos.storage.set_widget(updated_widget)
    repos.storage.save()

    logger.info("Updated widget - id: %s, properties: %s", widget_id, request.properties)

    return _domain_to_api(updated_widget)


@router.patch("/{widget_id}/position")  # type: ignore[misc]
async def update_widget_position(widget_id: str, request: UpdatePositionRequest) -> ApiWidget:
    """Update widget position in the grid.

    Args:
        widget_id: Widget identifier
        request: New position

    Returns:
        ApiWidget: The updated widget

    Raises:
        HTTPException: If widget not found
    """
    domain_widgets = repos.storage.get_widgets()
    if widget_id not in domain_widgets:
        logger.warning("Widget not found for position update - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    # Use immutable domain model helper method
    old_widget = domain_widgets[widget_id]
    old_position = old_widget.position
    updated_widget = old_widget.with_position(request.position)

    # Save to storage
    repos.storage.set_widget(updated_widget)
    repos.storage.save()

    logger.info("Updated widget position - id: %s, old: %d, new: %d", widget_id, old_position, request.position)

    return _domain_to_api(updated_widget)


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
    domain_widgets = repos.storage.get_widgets()
    if widget_id not in domain_widgets:
        logger.warning("Widget not found for deletion - id: %s", widget_id)
        raise HTTPException(status_code=404, detail="Widget not found")

    # Delete from storage
    repos.storage.delete_widget(widget_id)
    repos.storage.save()

    logger.info("Deleted widget - id: %s", widget_id)

    return {"status": "deleted", "id": widget_id}
