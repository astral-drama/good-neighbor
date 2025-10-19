"""YAML implementation of WidgetRepository."""

from __future__ import annotations

from typing import Callable

from good_neighbor.effects import IO, Effect, ErrorDetails, Failure, Result, Success
from good_neighbor.models import HomepageId, Widget, WidgetId

from .widget_repository import WidgetRepository
from .yaml_storage import YAMLStorage


class YAMLWidgetRepository(WidgetRepository):
    """YAML-based implementation of WidgetRepository.

    Stores widgets in storage.yaml file using YAMLStorage.
    All operations return IO[Result[ErrorDetails, A]] for composability.
    """

    def __init__(self, storage: YAMLStorage) -> None:
        """Initialize repository.

        Args:
            storage: Shared YAMLStorage instance
        """
        self.storage = storage

    def get(self, id: WidgetId) -> IO[Result[ErrorDetails, Widget | None]]:
        """Retrieve a widget by ID."""

        def _get() -> Result[ErrorDetails, Widget | None]:
            try:
                widgets = self.storage.get_widgets()
                widget = widgets.get(str(id))
                return Success(widget)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR", message=f"Failed to get widget: {e}", details={"widget_id": str(id)}
                    )
                )

        return Effect(_get)

    def insert(self, entity: Widget) -> IO[Result[ErrorDetails, WidgetId]]:
        """Insert a new widget."""

        def _insert() -> Result[ErrorDetails, WidgetId]:
            try:
                # Check if widget already exists
                widgets = self.storage.get_widgets()
                if str(entity.widget_id) in widgets:
                    return Failure(
                        ErrorDetails(
                            code="DUPLICATE_ID",
                            message="Widget with this ID already exists",
                            details={"widget_id": str(entity.widget_id)},
                        )
                    )

                # Insert widget
                self.storage.set_widget(entity)
                self.storage.save()

                return Success(entity.widget_id)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to insert widget: {e}",
                        details={"widget_id": str(entity.widget_id)},
                    )
                )

        return Effect(_insert)

    def update(self, id: WidgetId, f: Callable[[Widget], Widget]) -> IO[Result[ErrorDetails, None]]:
        """Update a widget using a pure function."""

        def _update() -> Result[ErrorDetails, None]:
            try:
                widgets = self.storage.get_widgets()
                widget = widgets.get(str(id))

                if widget is None:
                    return Failure(
                        ErrorDetails(code="NOT_FOUND", message="Widget not found", details={"widget_id": str(id)})
                    )

                # Apply update function
                updated_widget = f(widget)

                # Save updated widget
                self.storage.set_widget(updated_widget)
                self.storage.save()

                return Success(None)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR", message=f"Failed to update widget: {e}", details={"widget_id": str(id)}
                    )
                )

        return Effect(_update)

    def delete(self, id: WidgetId) -> IO[Result[ErrorDetails, None]]:
        """Delete a widget by ID (idempotent)."""

        def _delete() -> Result[ErrorDetails, None]:
            try:
                self.storage.delete_widget(str(id))
                self.storage.save()
                return Success(None)  # Idempotent: success even if not found
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR", message=f"Failed to delete widget: {e}", details={"widget_id": str(id)}
                    )
                )

        return Effect(_delete)

    def list(self) -> IO[Result[ErrorDetails, list[Widget]]]:
        """List all widgets."""

        def _list() -> Result[ErrorDetails, list[Widget]]:
            try:
                widgets = self.storage.get_widgets()
                return Success(list(widgets.values()))
            except Exception as e:
                return Failure(ErrorDetails(code="STORAGE_ERROR", message=f"Failed to list widgets: {e}"))

        return Effect(_list)

    def list_by_homepage(self, homepage_id: HomepageId) -> IO[Result[ErrorDetails, list[Widget]]]:
        """List all widgets for a specific homepage."""

        def _list_by_homepage() -> Result[ErrorDetails, list[Widget]]:
            try:
                widgets = self.storage.get_widgets()
                homepage_widgets = [w for w in widgets.values() if w.homepage_id == homepage_id]
                # Sort by position
                homepage_widgets.sort(key=lambda w: w.position)
                return Success(homepage_widgets)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to list widgets for homepage: {e}",
                        details={"homepage_id": str(homepage_id)},
                    )
                )

        return Effect(_list_by_homepage)

    def get_max_position(self, homepage_id: HomepageId) -> IO[Result[ErrorDetails, int]]:
        """Get the maximum position value for widgets on a homepage."""

        def _get_max_position() -> Result[ErrorDetails, int]:
            try:
                widgets = self.storage.get_widgets()
                homepage_widgets = [w for w in widgets.values() if w.homepage_id == homepage_id]

                if not homepage_widgets:
                    return Success(0)

                max_pos = max(w.position for w in homepage_widgets)
                return Success(max_pos)
            except Exception as e:
                return Failure(
                    ErrorDetails(
                        code="STORAGE_ERROR",
                        message=f"Failed to get max position: {e}",
                        details={"homepage_id": str(homepage_id)},
                    )
                )

        return Effect(_get_max_position)
