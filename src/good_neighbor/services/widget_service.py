"""Widget service with business logic."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from good_neighbor.effects import IO, Effect, ErrorDetails, Failure, Result
from good_neighbor.models import HomepageId, Widget, WidgetId, WidgetType
from good_neighbor.storage import WidgetRepository


class WidgetService:
    """Service for widget-related business logic.

    Composes repository operations using IO/Result monads.
    Handles widget positioning and homepage association.

    Example:
        >>> repos = create_yaml_repositories()
        >>> service = WidgetService(repos.widgets)
        >>> result = service.create_widget(
        ...     homepage_id, WidgetType.SHORTCUT, {"url": "https://example.com", "title": "Example"}
        ... ).run()
    """

    def __init__(self, widget_repo: WidgetRepository) -> None:
        """Initialize service with repository.

        Args:
            widget_repo: WidgetRepository instance
        """
        self.widget_repo = widget_repo

    def get_widget(self, widget_id: WidgetId) -> IO[Result[ErrorDetails, Widget | None]]:
        """Get a widget by ID.

        Args:
            widget_id: The widget ID to retrieve

        Returns:
            IO containing Result with widget if found, None if not found, or error
        """
        return self.widget_repo.get(widget_id)

    def list_widgets_for_homepage(self, homepage_id: HomepageId) -> IO[Result[ErrorDetails, list[Widget]]]:
        """List all widgets for a specific homepage, sorted by position.

        Args:
            homepage_id: The homepage ID

        Returns:
            IO containing Result with list of widgets (sorted by position) or error
        """
        return self.widget_repo.list_by_homepage(homepage_id)

    def create_widget(
        self, homepage_id: HomepageId, widget_type: WidgetType, properties: dict[str, Any], position: int | None = None
    ) -> IO[Result[ErrorDetails, Widget]]:
        """Create a new widget for a homepage.

        If position is None, appends to the end (max position + 1).

        Args:
            homepage_id: The homepage ID
            widget_type: Type of widget (iframe or shortcut)
            properties: Widget-specific properties
            position: Optional position (defaults to end of list)

        Returns:
            IO containing Result with created widget or error

        Example:
            >>> result = service.create_widget(
            ...     homepage_id, WidgetType.SHORTCUT, {"url": "https://example.com", "title": "Example"}, position=0
            ... ).run()
        """

        def _create_with_position(max_pos: int) -> IO[Result[ErrorDetails, Widget]]:
            actual_position = position if position is not None else max_pos + 1
            now = datetime.now(timezone.utc)

            new_widget = Widget(
                widget_id=WidgetId(str(uuid4())),
                homepage_id=homepage_id,
                type=widget_type,
                position=actual_position,
                properties=properties,
                created_at=now,
                updated_at=now,
            )

            return self.widget_repo.insert(new_widget).map(lambda _: new_widget)

        return self.widget_repo.get_max_position(homepage_id).flat_map(
            lambda result: result.flat_map(_create_with_position)
        )

    def update_widget_properties(
        self, widget_id: WidgetId, properties: dict[str, Any]
    ) -> IO[Result[ErrorDetails, None]]:
        """Update a widget's properties.

        Args:
            widget_id: The widget ID
            properties: New properties dictionary

        Returns:
            IO containing Result with None on success or error
        """
        return self.widget_repo.update(widget_id, lambda w: w.with_properties(properties))

    def update_widget_position(self, widget_id: WidgetId, new_position: int) -> IO[Result[ErrorDetails, None]]:
        """Update a widget's position.

        Args:
            widget_id: The widget ID
            new_position: New position value

        Returns:
            IO containing Result with None on success or error
        """
        return self.widget_repo.update(widget_id, lambda w: w.with_position(new_position))

    def delete_widget(self, widget_id: WidgetId, homepage_id: HomepageId) -> IO[Result[ErrorDetails, None]]:
        """Delete a widget.

        Validates that the widget belongs to the specified homepage before deletion.

        Args:
            widget_id: The widget ID to delete
            homepage_id: The homepage ID (for validation)

        Returns:
            IO containing Result with None on success or error
        """

        def _validate_and_delete(widget: Widget | None) -> IO[Result[ErrorDetails, None]]:
            if widget is None:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="NOT_FOUND", message="Widget not found", details={"widget_id": str(widget_id)}
                        )
                    )
                )

            if widget.homepage_id != homepage_id:
                return Effect(
                    lambda: Failure(
                        ErrorDetails(
                            code="FORBIDDEN",
                            message="Widget does not belong to homepage",
                            details={"widget_id": str(widget_id), "homepage_id": str(homepage_id)},
                        )
                    )
                )

            return self.widget_repo.delete(widget_id)

        return self.widget_repo.get(widget_id).flat_map(lambda result: result.flat_map(_validate_and_delete))

    def reorder_widgets(self, homepage_id: HomepageId, widget_order: list[WidgetId]) -> IO[Result[ErrorDetails, None]]:
        """Reorder widgets on a homepage.

        Updates positions based on the order in the widget_order list.

        Args:
            homepage_id: The homepage ID
            widget_order: List of widget IDs in desired order

        Returns:
            IO containing Result with None on success or error

        Example:
            >>> result = service.reorder_widgets(homepage_id, [widget3_id, widget1_id, widget2_id]).run()
        """

        def _update_positions(widgets: list[Widget]) -> IO[Result[ErrorDetails, None]]:
            # Create a map of widget_id to Widget
            widget_map = {w.widget_id: w for w in widgets}

            # Validate all widgets exist and belong to this homepage
            for widget_id in widget_order:
                widget = widget_map.get(widget_id)
                if widget is None:
                    # Capture widget_id in closure using default parameter
                    return Effect(
                        lambda wid=widget_id: Failure(
                            ErrorDetails(
                                code="NOT_FOUND",
                                message="Widget not found in reorder list",
                                details={"widget_id": str(wid)},
                            )
                        )
                    )
                if widget.homepage_id != homepage_id:
                    # Capture widget_id in closure using default parameter
                    return Effect(
                        lambda wid=widget_id: Failure(
                            ErrorDetails(
                                code="FORBIDDEN",
                                message="Widget does not belong to homepage",
                                details={"widget_id": str(wid), "homepage_id": str(homepage_id)},
                            )
                        )
                    )

            # Update positions sequentially
            def _update_all(index: int) -> IO[Result[ErrorDetails, None]]:
                if index >= len(widget_order):
                    return Effect(lambda: Result[ErrorDetails, None](None))

                widget_id = widget_order[index]
                return self.widget_repo.update(widget_id, lambda w: w.with_position(index)).flat_map(
                    lambda _: _update_all(index + 1)
                )

            return _update_all(0)

        return self.widget_repo.list_by_homepage(homepage_id).flat_map(
            lambda result: result.flat_map(_update_positions)
        )
