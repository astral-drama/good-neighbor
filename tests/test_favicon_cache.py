"""Tests for favicon cache module."""

import time

import pytest

from good_neighbor.services.favicon_cache import FaviconCache


def test_cache_initialization() -> None:
    """Test cache initialization with default values."""
    cache = FaviconCache()
    assert cache.ttl == 86400  # 24 hours
    assert cache.max_size == 1000
    stats = cache.get_stats()
    assert stats["size"] == 0
    assert stats["max_size"] == 1000
    assert stats["ttl"] == 86400


def test_cache_initialization_custom_values() -> None:
    """Test cache initialization with custom values."""
    cache = FaviconCache(ttl=3600, max_size=100)
    assert cache.ttl == 3600
    assert cache.max_size == 100


def test_cache_set_and_get() -> None:
    """Test basic cache set and get operations."""
    cache = FaviconCache()
    favicon_data = {"data_url": "data:image/png;base64,test", "format": "png", "source": "test.com"}

    cache.set("https://example.com", favicon_data)

    result = cache.get("https://example.com")
    assert result is not None
    assert result["data_url"] == "data:image/png;base64,test"
    assert result["format"] == "png"
    assert result["source"] == "test.com"


def test_cache_get_nonexistent() -> None:
    """Test getting a nonexistent cache entry."""
    cache = FaviconCache()
    result = cache.get("https://nonexistent.com")
    assert result is None


def test_cache_expiration() -> None:
    """Test that cache entries expire after TTL."""
    cache = FaviconCache(ttl=1)  # 1 second TTL
    favicon_data = {"data_url": "data:image/png;base64,test", "format": "png", "source": "test.com"}

    cache.set("https://example.com", favicon_data)

    # Should be available immediately
    result = cache.get("https://example.com")
    assert result is not None

    # Wait for expiration
    time.sleep(1.1)

    # Should be expired now
    result = cache.get("https://example.com")
    assert result is None


def test_cache_size_limit() -> None:
    """Test that cache evicts oldest entries when full."""
    cache = FaviconCache(max_size=3)

    # Add 3 entries
    for i in range(3):
        cache.set(f"https://example{i}.com", {"data_url": f"test{i}", "format": "png", "source": f"test{i}.com"})

    stats = cache.get_stats()
    assert stats["size"] == 3

    # Add one more - should evict oldest
    cache.set("https://example3.com", {"data_url": "test3", "format": "png", "source": "test3.com"})

    stats = cache.get_stats()
    assert stats["size"] == 3  # Still at max size

    # Oldest entry (example0) should be gone
    assert cache.get("https://example0.com") is None
    # Newest entries should still be there
    assert cache.get("https://example1.com") is not None
    assert cache.get("https://example2.com") is not None
    assert cache.get("https://example3.com") is not None


def test_cache_lru_eviction() -> None:
    """Test that LRU eviction removes the oldest by timestamp."""
    cache = FaviconCache(max_size=2)

    cache.set("https://first.com", {"data_url": "first", "format": "png", "source": "first.com"})
    time.sleep(0.1)  # Ensure different timestamps
    cache.set("https://second.com", {"data_url": "second", "format": "png", "source": "second.com"})
    time.sleep(0.1)

    # Cache is now full with first and second
    stats = cache.get_stats()
    assert stats["size"] == 2

    # Add third - should evict first (oldest)
    cache.set("https://third.com", {"data_url": "third", "format": "png", "source": "third.com"})

    assert cache.get("https://first.com") is None  # Evicted
    assert cache.get("https://second.com") is not None
    assert cache.get("https://third.com") is not None


def test_cache_clear_all() -> None:
    """Test clearing entire cache."""
    cache = FaviconCache()

    # Add multiple entries
    for i in range(5):
        cache.set(f"https://example{i}.com", {"data_url": f"test{i}", "format": "png", "source": f"test{i}.com"})

    stats = cache.get_stats()
    assert stats["size"] == 5

    # Clear all
    cache.clear()

    stats = cache.get_stats()
    assert stats["size"] == 0


def test_cache_clear_specific_key() -> None:
    """Test clearing specific cache entry."""
    cache = FaviconCache()

    cache.set("https://example1.com", {"data_url": "test1", "format": "png", "source": "test1.com"})
    cache.set("https://example2.com", {"data_url": "test2", "format": "png", "source": "test2.com"})

    stats = cache.get_stats()
    assert stats["size"] == 2

    # Clear only example1
    cache.clear("https://example1.com")

    stats = cache.get_stats()
    assert stats["size"] == 1
    assert cache.get("https://example1.com") is None
    assert cache.get("https://example2.com") is not None


def test_cache_clear_nonexistent_key() -> None:
    """Test clearing a nonexistent key doesn't raise error."""
    cache = FaviconCache()
    cache.set("https://example.com", {"data_url": "test", "format": "png", "source": "test.com"})

    # This should not raise an error
    cache.clear("https://nonexistent.com")

    # Original entry should still be there
    assert cache.get("https://example.com") is not None


def test_cache_update_existing_entry() -> None:
    """Test updating an existing cache entry."""
    cache = FaviconCache()

    # Set initial value
    cache.set("https://example.com", {"data_url": "old", "format": "png", "source": "old.com"})

    # Update with new value
    cache.set("https://example.com", {"data_url": "new", "format": "ico", "source": "new.com"})

    result = cache.get("https://example.com")
    assert result is not None
    assert result["data_url"] == "new"
    assert result["format"] == "ico"

    # Should still have only one entry
    stats = cache.get_stats()
    assert stats["size"] == 1


def test_get_stats() -> None:
    """Test cache statistics."""
    cache = FaviconCache(ttl=7200, max_size=500)

    stats = cache.get_stats()
    assert stats["size"] == 0
    assert stats["max_size"] == 500
    assert stats["ttl"] == 7200

    # Add some entries
    for i in range(10):
        cache.set(f"https://example{i}.com", {"data_url": f"test{i}", "format": "png", "source": f"test{i}.com"})

    stats = cache.get_stats()
    assert stats["size"] == 10
    assert stats["max_size"] == 500
    assert stats["ttl"] == 7200


def test_cache_thread_safety_simulation() -> None:
    """Test cache handles concurrent-like operations."""
    cache = FaviconCache(max_size=5)

    # Simulate rapid insertions
    for i in range(20):
        cache.set(f"https://example{i}.com", {"data_url": f"test{i}", "format": "png", "source": f"test{i}.com"})

    # Cache should never exceed max size
    stats = cache.get_stats()
    assert stats["size"] <= 5


@pytest.mark.parametrize(
    "ttl,wait_time,should_expire",
    [
        (2, 1, False),  # Not expired
        (1, 1.1, True),  # Expired
        (1, 0.6, False),  # Not expired with fractional wait time
        (10, 0.1, False),  # Definitely not expired
    ],
)
def test_cache_expiration_scenarios(ttl: int, wait_time: float, should_expire: bool) -> None:
    """Test various TTL expiration scenarios."""
    cache = FaviconCache(ttl=ttl)
    favicon_data = {"data_url": "data:image/png;base64,test", "format": "png", "source": "test.com"}

    cache.set("https://example.com", favicon_data)
    time.sleep(wait_time)

    result = cache.get("https://example.com")

    if should_expire:
        assert result is None, f"Expected expiration after {wait_time}s with TTL {ttl}s"
    else:
        assert result is not None, f"Unexpected expiration after {wait_time}s with TTL {ttl}s"
