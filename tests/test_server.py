"""Tests for the FastAPI server."""

from fastapi.testclient import TestClient

from good_neighbor.server import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint returns expected data."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "good-neighbor"
    assert data["version"] == "0.1.0"


def test_health_endpoint_returns_json():
    """Test the health check endpoint returns JSON."""
    response = client.get("/api/health")
    assert response.headers["content-type"] == "application/json"
