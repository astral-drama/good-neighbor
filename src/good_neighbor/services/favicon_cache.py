"""In-memory cache for favicons with TTL support."""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Cache TTL in seconds (24 hours)
DEFAULT_TTL = 24 * 60 * 60


class FaviconCache:
    """Simple in-memory cache for favicons with TTL and LRU eviction."""

    def __init__(self, ttl: int = DEFAULT_TTL, max_size: int = 1000):
        """Initialize the favicon cache.

        Args:
            ttl: Time to live in seconds (default: 24 hours)
            max_size: Maximum number of cached items (default: 1000)
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[dict[str, str], float]] = {}
        logger.info(f"Initialized favicon cache - ttl: {ttl}s, max_size: {max_size}")

    def get(self, key: str) -> Optional[dict[str, str]]:
        """Get a favicon from cache if not expired.

        Args:
            key: Cache key (usually domain name)

        Returns:
            Cached favicon data or None if not found/expired
        """
        if key not in self._cache:
            return None

        favicon_data, timestamp = self._cache[key]

        # Check if expired
        if time.time() - timestamp > self.ttl:
            logger.debug(f"Cache entry expired - key: {key}")
            del self._cache[key]
            return None

        logger.debug(f"Cache hit - key: {key}")
        return favicon_data

    def set(self, key: str, value: dict[str, str]) -> None:
        """Store a favicon in cache.

        Args:
            key: Cache key (usually domain name)
            value: Favicon data to cache
        """
        # Implement simple LRU: if cache is full, remove oldest entry
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            logger.debug(f"Cache full, evicting oldest entry - key: {oldest_key}")
            del self._cache[oldest_key]

        self._cache[key] = (value, time.time())
        logger.debug(f"Cached favicon - key: {key}, cache_size: {len(self._cache)}")

    def clear(self, key: Optional[str] = None) -> None:
        """Clear cache entries.

        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Cleared cache entry - key: {key}")
        else:
            self._cache.clear()
            logger.info("Cleared entire favicon cache")

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        return {"size": len(self._cache), "max_size": self.max_size, "ttl": self.ttl}


# Global cache instance
_favicon_cache = FaviconCache()


def get_cache() -> FaviconCache:
    """Get the global favicon cache instance.

    Returns:
        FaviconCache instance
    """
    return _favicon_cache
