"""YAML-based storage backend with atomic writes and file locking.

Provides thread-safe, atomic file operations for persisting data to storage.yaml.
"""

from __future__ import annotations

import fcntl
import shutil
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from good_neighbor.models import Homepage, User, Widget


@dataclass
class StorageData:
    """Root storage structure for YAML file.

    This matches the YAML format defined in GOOD--6 spec.
    """

    version: str
    users: list[dict[str, Any]]
    homepages: list[dict[str, Any]]
    widgets: list[dict[str, Any]]


class YAMLStorage:
    """Thread-safe YAML storage with atomic writes and file locking.

    Features:
    - Atomic writes (write to temp file, then rename)
    - File locking using fcntl to prevent concurrent access
    - Automatic backups before each write
    - In-memory cache of loaded data
    - Thread-safe operations using locks

    Example:
        >>> storage = YAMLStorage("storage.yaml")
        >>> storage.load()  # Load data from file
        >>> # Modify data in memory
        >>> storage.save()  # Atomically save to file
    """

    def __init__(self, file_path: str | Path = "storage.yaml") -> None:
        """Initialize YAML storage.

        Args:
            file_path: Path to storage.yaml file (default: "storage.yaml")
        """
        self.file_path = Path(file_path)
        self.backup_path = Path(str(file_path) + ".backup")
        self._lock = threading.Lock()

        # In-memory cache
        self._users: dict[str, User] = {}
        self._homepages: dict[str, Homepage] = {}
        self._widgets: dict[str, Widget] = {}
        self._loaded = False

    def load(self) -> None:
        """Load data from YAML file into memory.

        Creates an empty file if it doesn't exist.
        Restores from backup if main file is corrupt.

        Thread-safe operation.
        """
        with self._lock:
            self._load_unsafe()

    def _load_unsafe(self) -> None:
        """Load data without acquiring lock (internal use only)."""
        if not self.file_path.exists():
            # Initialize with empty storage
            self._users = {}
            self._homepages = {}
            self._widgets = {}
            self._loaded = True
            self._save_unsafe()  # Create initial file
            return

        try:
            with self.file_path.open(encoding="utf-8") as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data_dict = yaml.safe_load(f) or {}
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Parse data into domain models
            self._users = {
                user_data["user_id"]: self._dict_to_user(user_data) for user_data in data_dict.get("users", [])
            }

            self._homepages = {
                hp_data["homepage_id"]: self._dict_to_homepage(hp_data) for hp_data in data_dict.get("homepages", [])
            }

            self._widgets = {
                widget_data["widget_id"]: self._dict_to_widget(widget_data)
                for widget_data in data_dict.get("widgets", [])
            }

            self._loaded = True

        except (yaml.YAMLError, KeyError, ValueError) as e:
            # Try to restore from backup
            if self.backup_path.exists():
                shutil.copy(self.backup_path, self.file_path)
                # Retry loading
                self._load_unsafe()
            else:
                # No backup available, start fresh
                self._users = {}
                self._homepages = {}
                self._widgets = {}
                self._loaded = True
                msg = f"Corrupt YAML file and no backup available: {e}"
                raise RuntimeError(msg) from e

    def save(self) -> None:
        """Save in-memory data to YAML file.

        Creates a backup before saving.
        Uses atomic write (temp file + rename).

        Thread-safe operation.
        """
        with self._lock:
            self._save_unsafe()

    def _save_unsafe(self) -> None:
        """Save data without acquiring lock (internal use only)."""
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup of existing file
        if self.file_path.exists():
            shutil.copy(self.file_path, self.backup_path)

        # Convert domain models to dicts
        data = {
            "version": "1.0",
            "users": [self._user_to_dict(user) for user in self._users.values()],
            "homepages": [self._homepage_to_dict(hp) for hp in self._homepages.values()],
            "widgets": [self._widget_to_dict(widget) for widget in self._widgets.values()],
        }

        # Atomic write: write to temp file, then rename
        temp_path = self.file_path.with_suffix(".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as f:
                # Acquire exclusive lock for writing
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomic rename
            temp_path.replace(self.file_path)

            # Set restrictive permissions (user read/write only)
            self.file_path.chmod(0o600)

        except Exception:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise

    def get_users(self) -> dict[str, User]:
        """Get all users (in-memory cache).

        Returns:
            Dictionary mapping user_id to User
        """
        with self._lock:
            self._ensure_loaded()
            return dict(self._users)

    def get_homepages(self) -> dict[str, Homepage]:
        """Get all homepages (in-memory cache).

        Returns:
            Dictionary mapping homepage_id to Homepage
        """
        with self._lock:
            self._ensure_loaded()
            return dict(self._homepages)

    def get_widgets(self) -> dict[str, Widget]:
        """Get all widgets (in-memory cache).

        Returns:
            Dictionary mapping widget_id to Widget
        """
        with self._lock:
            self._ensure_loaded()
            return dict(self._widgets)

    def set_user(self, user: User) -> None:
        """Update or insert a user in cache.

        Args:
            user: The user to store

        Note: Call save() to persist to disk.
        """
        with self._lock:
            self._ensure_loaded()
            self._users[str(user.user_id)] = user

    def set_homepage(self, homepage: Homepage) -> None:
        """Update or insert a homepage in cache.

        Args:
            homepage: The homepage to store

        Note: Call save() to persist to disk.
        """
        with self._lock:
            self._ensure_loaded()
            self._homepages[str(homepage.homepage_id)] = homepage

    def set_widget(self, widget: Widget) -> None:
        """Update or insert a widget in cache.

        Args:
            widget: The widget to store

        Note: Call save() to persist to disk.
        """
        with self._lock:
            self._ensure_loaded()
            self._widgets[str(widget.widget_id)] = widget

    def delete_user(self, user_id: str) -> None:
        """Delete a user from cache.

        Args:
            user_id: The user ID

        Note: Call save() to persist to disk.
        """
        with self._lock:
            self._ensure_loaded()
            self._users.pop(user_id, None)

    def delete_homepage(self, homepage_id: str) -> None:
        """Delete a homepage from cache.

        Args:
            homepage_id: The homepage ID

        Note: Call save() to persist to disk.
        """
        with self._lock:
            self._ensure_loaded()
            self._homepages.pop(homepage_id, None)

    def delete_widget(self, widget_id: str) -> None:
        """Delete a widget from cache.

        Args:
            widget_id: The widget ID

        Note: Call save() to persist to disk.
        """
        with self._lock:
            self._ensure_loaded()
            self._widgets.pop(widget_id, None)

    def _ensure_loaded(self) -> None:
        """Ensure data is loaded from disk."""
        if not self._loaded:
            self._load_unsafe()

    @staticmethod
    def _user_to_dict(user: User) -> dict[str, Any]:
        """Convert User to dict for YAML serialization."""
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "default_homepage_id": str(user.default_homepage_id) if user.default_homepage_id else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

    @staticmethod
    def _homepage_to_dict(homepage: Homepage) -> dict[str, Any]:
        """Convert Homepage to dict for YAML serialization."""
        return {
            "homepage_id": str(homepage.homepage_id),
            "user_id": str(homepage.user_id),
            "name": homepage.name,
            "is_default": homepage.is_default,
            "created_at": homepage.created_at.isoformat(),
            "updated_at": homepage.updated_at.isoformat(),
        }

    @staticmethod
    def _widget_to_dict(widget: Widget) -> dict[str, Any]:
        """Convert Widget to dict for YAML serialization."""
        return {
            "widget_id": str(widget.widget_id),
            "homepage_id": str(widget.homepage_id),
            "type": widget.type.value,
            "position": widget.position,
            "properties": widget.properties,
            "created_at": widget.created_at.isoformat(),
            "updated_at": widget.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_user(data: dict[str, Any]) -> User:
        """Convert dict from YAML to User domain model."""
        from good_neighbor.models import HomepageId, UserId

        return User(
            user_id=UserId(data["user_id"]),
            username=data["username"],
            default_homepage_id=HomepageId(data["default_homepage_id"]) if data.get("default_homepage_id") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    @staticmethod
    def _dict_to_homepage(data: dict[str, Any]) -> Homepage:
        """Convert dict from YAML to Homepage domain model."""
        from good_neighbor.models import HomepageId, UserId

        return Homepage(
            homepage_id=HomepageId(data["homepage_id"]),
            user_id=UserId(data["user_id"]),
            name=data["name"],
            is_default=data["is_default"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    @staticmethod
    def _dict_to_widget(data: dict[str, Any]) -> Widget:
        """Convert dict from YAML to Widget domain model."""
        from good_neighbor.models import HomepageId, WidgetId, WidgetType

        return Widget(
            widget_id=WidgetId(data["widget_id"]),
            homepage_id=HomepageId(data["homepage_id"]),
            type=WidgetType(data["type"]),
            position=data["position"],
            properties=data["properties"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
