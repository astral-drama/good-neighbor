"""Shared storage instance for all API endpoints.

This module provides a single, shared storage instance that is used
by all API routers to ensure data consistency. The storage is loaded
once at module import time and reused across all requests.
"""

from .factory import Repositories, create_yaml_repositories

# Create and load shared storage instance
_shared_repos: Repositories | None = None


def get_shared_repositories() -> Repositories:
    """Get the shared repositories instance.

    Creates and loads the storage on first call. Subsequent calls return
    the same instance to ensure all API endpoints work with the same data.

    Returns:
        Repositories: Shared repository container with loaded storage
    """
    global _shared_repos

    if _shared_repos is None:
        _shared_repos = create_yaml_repositories()
        _shared_repos.storage.load()

    return _shared_repos
