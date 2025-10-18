"""Phantom types for type-safe IDs.

Phantom types prevent mixing different kinds of IDs at compile time.
For example, you cannot accidentally pass a HomepageId where a UserId
is expected - mypy will catch this error.
"""

from typing import NewType

# Phantom types for IDs
# These are distinct types at type-check time but are just strings at runtime
UserId = NewType("UserId", str)
HomepageId = NewType("HomepageId", str)
WidgetId = NewType("WidgetId", str)

__all__ = ["UserId", "HomepageId", "WidgetId"]
