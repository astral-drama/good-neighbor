"""Tests for favicon API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from good_neighbor.server import app
from good_neighbor.services.favicon_cache import get_cache

client = TestClient(app)


def setup_function() -> None:
    """Clear favicon cache before each test."""
    cache = get_cache()
    cache.clear()


def test_get_favicon_missing_url() -> None:
    """Test favicon endpoint with missing URL parameter."""
    response = client.get("/api/favicon/")
    assert response.status_code == 422  # Validation error


def test_get_favicon_empty_url() -> None:
    """Test favicon endpoint with empty URL."""
    response = client.get("/api/favicon/?url=")
    assert response.status_code == 400
    assert "URL parameter is required" in response.json()["detail"]


@pytest.mark.asyncio
@patch("good_neighbor.api.favicon.discover_favicon")
async def test_get_favicon_success(mock_discover: AsyncMock) -> None:
    """Test successful favicon fetch."""
    # Mock the favicon discovery
    mock_discover.return_value = {
        "data_url": "data:image/png;base64,iVBORw0KGgoAAAANS",
        "format": "png",
        "source": "https://example.com/favicon.png",
    }

    response = client.get("/api/favicon/?url=https://example.com")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["favicon"] == "data:image/png;base64,iVBORw0KGgoAAAANS"
    assert data["format"] == "png"
    assert data["source"] == "https://example.com/favicon.png"
    assert data["error"] is None


@pytest.mark.asyncio
@patch("good_neighbor.api.favicon.discover_favicon")
async def test_get_favicon_not_found(mock_discover: AsyncMock) -> None:
    """Test favicon fetch when no favicon is found."""
    mock_discover.return_value = None

    response = client.get("/api/favicon/?url=https://example.com")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is False
    assert data["favicon"] is None
    assert data["format"] is None
    assert data["source"] is None
    assert data["error"] == "No favicon found"


@pytest.mark.asyncio
@patch("good_neighbor.api.favicon.discover_favicon")
async def test_get_favicon_caching(mock_discover: AsyncMock) -> None:
    """Test that favicons are properly cached."""
    mock_discover.return_value = {
        "data_url": "data:image/png;base64,iVBORw0KGgoAAAANS",
        "format": "png",
        "source": "https://example.com/favicon.png",
    }

    # First request - should call discover_favicon
    response1 = client.get("/api/favicon/?url=https://example.com")
    assert response1.status_code == 200
    assert mock_discover.call_count == 1

    # Second request - should use cache
    response2 = client.get("/api/favicon/?url=https://example.com")
    assert response2.status_code == 200
    assert mock_discover.call_count == 1  # Not called again

    data = response2.json()
    assert data["success"] is True
    assert "(cached)" in data["source"]


@pytest.mark.asyncio
@patch("good_neighbor.api.favicon.discover_favicon")
async def test_get_favicon_domain_extraction(mock_discover: AsyncMock) -> None:
    """Test that different URLs from same domain share cache."""
    mock_discover.return_value = {
        "data_url": "data:image/png;base64,iVBORw0KGgoAAAANS",
        "format": "png",
        "source": "https://example.com/favicon.png",
    }

    # Request for homepage
    response1 = client.get("/api/favicon/?url=https://example.com")
    assert response1.status_code == 200
    assert mock_discover.call_count == 1

    # Request for different path - should use same cached favicon
    response2 = client.get("/api/favicon/?url=https://example.com/about")
    assert response2.status_code == 200
    assert mock_discover.call_count == 1  # Not called again

    # Both should return success
    assert response1.json()["success"] is True
    assert response2.json()["success"] is True


def test_clear_favicon_cache_all() -> None:
    """Test clearing entire favicon cache."""
    # Add a favicon to cache
    cache = get_cache()
    cache.set(
        "https://example.com",
        {"data_url": "data:image/png;base64,test", "format": "png", "source": "test"},
    )

    # Verify it's in cache
    stats = cache.get_stats()
    assert stats["size"] == 1

    # Clear cache
    response = client.delete("/api/favicon/cache")
    assert response.status_code == 200
    assert response.json()["status"] == "cleared"
    assert response.json()["domain"] == "all"

    # Verify cache is empty
    stats = cache.get_stats()
    assert stats["size"] == 0


def test_clear_favicon_cache_specific_domain() -> None:
    """Test clearing specific domain from cache."""
    cache = get_cache()
    cache.set(
        "https://example.com",
        {"data_url": "data:image/png;base64,test1", "format": "png", "source": "test1"},
    )
    cache.set(
        "https://other.com",
        {"data_url": "data:image/png;base64,test2", "format": "png", "source": "test2"},
    )

    # Clear only example.com
    response = client.delete("/api/favicon/cache?domain=https://example.com")
    assert response.status_code == 200
    assert response.json()["domain"] == "https://example.com"

    # Verify only example.com was cleared
    assert cache.get("https://example.com") is None
    assert cache.get("https://other.com") is not None


def test_get_cache_stats() -> None:
    """Test getting cache statistics."""
    response = client.get("/api/favicon/stats")
    assert response.status_code == 200

    data = response.json()
    assert "size" in data
    assert "max_size" in data
    assert "ttl" in data
    assert data["max_size"] == 1000  # Default max size
    assert data["ttl"] == 86400  # Default TTL (24 hours)


def test_get_cache_stats_with_data() -> None:
    """Test cache stats reflect actual cache size."""
    # Add some favicons to cache
    cache = get_cache()
    for i in range(5):
        cache.set(
            f"https://example{i}.com",
            {"data_url": f"data:image/png;base64,test{i}", "format": "png", "source": f"test{i}"},
        )

    response = client.get("/api/favicon/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["size"] == 5


@pytest.mark.asyncio
@patch("good_neighbor.api.favicon.discover_favicon")
async def test_get_favicon_handles_exceptions(mock_discover: AsyncMock) -> None:
    """Test that exceptions during discovery are handled gracefully."""
    mock_discover.side_effect = Exception("Network error")

    response = client.get("/api/favicon/?url=https://example.com")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is False
    assert data["error"] is not None
    assert "Failed to fetch favicon" in data["error"]
