"""Homepage domain model."""

from dataclasses import dataclass
from datetime import datetime, timezone

from .types import HomepageId, UserId


@dataclass(frozen=True)
class Homepage:
    """Homepage domain model (immutable).

    Represents a collection of widgets organized as a homepage.
    Users can have multiple homepages for different contexts
    (e.g., "Work", "Personal", "News").

    Note: Widgets are NOT stored on the Homepage object (normalization).
    Use WidgetRepository.list_by_homepage(homepage_id) to get widgets.

    Attributes:
        homepage_id: Unique homepage identifier
        user_id: ID of the user who owns this homepage
        name: Display name (e.g., "Work", "Personal")
        is_default: Whether this is the user's default homepage
        created_at: Timestamp when homepage was created
        updated_at: Timestamp when homepage was last updated
    """

    homepage_id: HomepageId
    user_id: UserId
    name: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    def with_name(self, name: str) -> "Homepage":
        """Create a new Homepage with updated name.

        Since Homepage is immutable, this returns a new instance.

        Args:
            name: The new name

        Returns:
            New Homepage instance with updated name and updated_at
        """
        return Homepage(
            homepage_id=self.homepage_id,
            user_id=self.user_id,
            name=name,
            is_default=self.is_default,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def set_as_default(self) -> "Homepage":
        """Create a new Homepage marked as default.

        Args:
            None

        Returns:
            New Homepage instance with is_default=True and updated_at
        """
        return Homepage(
            homepage_id=self.homepage_id,
            user_id=self.user_id,
            name=self.name,
            is_default=True,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def unset_as_default(self) -> "Homepage":
        """Create a new Homepage marked as not default.

        Returns:
            New Homepage instance with is_default=False and updated_at
        """
        return Homepage(
            homepage_id=self.homepage_id,
            user_id=self.user_id,
            name=self.name,
            is_default=False,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        default_marker = " (default)" if self.is_default else ""
        return f"Homepage({self.name}{default_marker}, id={self.homepage_id})"
