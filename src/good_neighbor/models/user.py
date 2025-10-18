"""User domain model."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .types import HomepageId, UserId


@dataclass(frozen=True)
class User:
    """User domain model (immutable).

    Represents a user of the good-neighbor application.
    Currently single-user, but designed for future multi-user support.

    Attributes:
        user_id: Unique user identifier
        username: User's display name
        default_homepage_id: ID of the user's default homepage
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
    """

    user_id: UserId
    username: str
    default_homepage_id: Optional[HomepageId]
    created_at: datetime
    updated_at: datetime

    def with_default_homepage(self, homepage_id: HomepageId) -> "User":
        """Create a new User with updated default homepage.

        Since User is immutable, this returns a new instance.

        Args:
            homepage_id: The new default homepage ID

        Returns:
            New User instance with updated default_homepage_id and updated_at
        """
        return User(
            user_id=self.user_id,
            username=self.username,
            default_homepage_id=homepage_id,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"User({self.username}, id={self.user_id})"
