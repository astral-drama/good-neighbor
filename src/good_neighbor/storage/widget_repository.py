"""Widget repository protocol."""

from abc import abstractmethod

from good_neighbor.effects import IO, ErrorDetails, Result
from good_neighbor.models import HomepageId, Widget, WidgetId

from .base import Repository


class WidgetRepository(Repository[Widget, WidgetId]):
    """Repository for Widget entities.

    Extends the generic Repository[Widget, WidgetId] protocol with widget-specific queries.

    All generic repository laws apply:
    - Get-Insert: inserting then getting returns the widget
    - Update-Get: updating then getting returns the updated widget
    - Delete-Get: deleting then getting returns None
    - Idempotent Delete: deleting twice succeeds

    Additional domain considerations:
    - Widgets are ordered by position within a homepage
    - Position reordering is handled by the service layer
    - Widget properties are validated by Pydantic at the API layer

    Example:
        >>> widget_repo: WidgetRepository = YAMLWidgetRepository(storage)
        >>>
        >>> # Generic operations
        >>> result = widget_repo.get(WidgetId("widget-123")).run()
        >>>
        >>> # Specialized operations - list all widgets for a homepage
        >>> homepage_widgets = widget_repo.list_by_homepage(HomepageId("home-123")).run()
    """

    @abstractmethod
    def list_by_homepage(self, homepage_id: HomepageId) -> IO[Result[ErrorDetails, list[Widget]]]:
        """List all widgets for a specific homepage, ordered by position.

        Widgets are returned sorted by position (ascending), so they can be
        displayed in the correct order.

        Args:
            homepage_id: The homepage ID to filter by

        Returns:
            IO containing Result with list of homepage's widgets (ordered) or error

        Example:
            >>> result = widget_repo.list_by_homepage(homepage_id).run()
            >>> match result:
            ...     case Success(widgets):
            ...         for w in widgets:
            ...             print(f"{w.position}: {w.type} - {w.properties.get('title')}")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...

    @abstractmethod
    def get_max_position(self, homepage_id: HomepageId) -> IO[Result[ErrorDetails, int]]:
        """Get the maximum position value for widgets in a homepage.

        Useful for auto-assigning positions when creating new widgets.

        Args:
            homepage_id: The homepage ID

        Returns:
            IO containing Result with max position (or 0 if no widgets) or error

        Example:
            >>> result = widget_repo.get_max_position(homepage_id).run()
            >>> match result:
            ...     case Success(max_pos):
            ...         new_position = max_pos + 1
            ...         print(f"Next position: {new_position}")
            ...     case Failure(error):
            ...         print(f"Error: {error}")
        """
        ...
