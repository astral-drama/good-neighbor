"""Tests for the health check endpoint."""

import time

from fastapi.testclient import TestClient

from good_neighbor.server import app

client = TestClient(app)


def test_health_endpoint_returns_200() -> None:
    """Test that health endpoint returns 200 OK."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_endpoint_returns_expected_fields() -> None:
    """Test that health endpoint returns all expected fields."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()

    # Check top-level fields
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data
    assert "uptime" in data
    assert "storage" in data

    # Verify values
    assert data["status"] == "healthy"
    assert data["service"] == "good-neighbor"
    assert data["version"] == "0.1.0"


def test_health_endpoint_uptime_structure() -> None:
    """Test that uptime information has the correct structure."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    uptime = data["uptime"]

    # Check uptime fields exist
    assert "seconds" in uptime
    assert "hours" in uptime
    assert "days" in uptime

    # Verify uptime values are reasonable (should be small for tests)
    assert uptime["seconds"] >= 0
    assert uptime["hours"] >= 0
    assert uptime["days"] >= 0


def test_health_endpoint_storage_status() -> None:
    """Test that storage status is included."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    storage = data["storage"]

    assert "status" in storage
    # Storage should be healthy in test environment
    assert storage["status"] in ["healthy", "unhealthy", "unknown"]


def test_health_endpoint_timestamp_format() -> None:
    """Test that timestamp is in ISO format."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    timestamp = data["timestamp"]

    # Verify it's a string and contains expected ISO format components
    assert isinstance(timestamp, str)
    assert "T" in timestamp  # ISO format has T separator
    # Should contain timezone info (ISO format with timezone)
    assert "+" in timestamp or "Z" in timestamp


def test_health_endpoint_uptime_increases() -> None:
    """Test that uptime increases between calls."""
    response1 = client.get("/api/health")
    uptime1 = response1.json()["uptime"]["seconds"]

    time.sleep(0.1)  # Sleep for 100ms

    response2 = client.get("/api/health")
    uptime2 = response2.json()["uptime"]["seconds"]

    # Second uptime should be greater than first
    assert uptime2 > uptime1
