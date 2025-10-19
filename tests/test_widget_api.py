"""Tests for widget API endpoints."""

from fastapi.testclient import TestClient

from good_neighbor.server import app

client = TestClient(app)


def test_list_widgets_empty() -> None:
    """Test listing widgets when store is empty."""
    response = client.get("/api/widgets")
    assert response.status_code == 200
    assert response.json() == []


def test_create_iframe_widget() -> None:
    """Test creating an iframe widget."""
    response = client.post(
        "/api/widgets",
        json={
            "type": "iframe",
            "properties": {
                "url": "http://localhost:8000/widget/service",
                "title": "Service Monitor",
                "width": 400,
                "height": 300,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["type"] == "iframe"
    assert data["id"] is not None
    assert data["position"] >= 0  # Position auto-assigned
    assert data["properties"]["url"] == "http://localhost:8000/widget/service"
    assert data["properties"]["title"] == "Service Monitor"
    assert data["properties"]["width"] == 400
    assert data["properties"]["height"] == 300
    assert "created_at" in data
    assert "updated_at" in data


def test_create_shortcut_widget() -> None:
    """Test creating a shortcut widget."""
    response = client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "properties": {
                "url": "https://news.ycombinator.com",
                "title": "Hacker News",
                "icon": "📰",
                "description": "Tech news and discussions",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["type"] == "shortcut"
    assert data["id"] is not None
    assert "news.ycombinator.com" in data["properties"]["url"]  # URL may or may not have trailing slash
    assert data["properties"]["title"] == "Hacker News"
    assert data["properties"]["icon"] == "📰"


def test_create_widget_with_position() -> None:
    """Test creating a widget with explicit position."""
    response = client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "position": 5,
            "properties": {
                "url": "https://example.com",
                "title": "Example",
                "icon": "🔗",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["position"] == 5


def test_list_widgets_with_data() -> None:
    """Test listing widgets returns all widgets sorted by position."""
    # Create multiple widgets
    client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "position": 2,
            "properties": {"url": "https://example.com", "title": "Example", "icon": "🔗"},
        },
    )
    client.post(
        "/api/widgets",
        json={
            "type": "iframe",
            "position": 0,
            "properties": {
                "url": "http://localhost:8000/widget",
                "title": "Widget",
                "width": 300,
                "height": 200,
            },
        },
    )
    client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "position": 1,
            "properties": {"url": "https://test.com", "title": "Test", "icon": "✓"},
        },
    )

    response = client.get("/api/widgets")
    assert response.status_code == 200
    widgets = response.json()

    assert len(widgets) == 3
    # Verify sorted by position
    assert widgets[0]["position"] == 0
    assert widgets[1]["position"] == 1
    assert widgets[2]["position"] == 2


def test_get_widget_by_id() -> None:
    """Test retrieving a specific widget by ID."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "iframe",
            "properties": {"url": "http://example.com", "title": "Test", "width": 400, "height": 300},
        },
    )
    widget_id = create_response.json()["id"]

    # Get the widget
    response = client.get(f"/api/widgets/{widget_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == widget_id
    assert data["type"] == "iframe"


def test_get_widget_not_found() -> None:
    """Test retrieving a non-existent widget returns 404."""
    response = client.get("/api/widgets/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Widget not found"


def test_update_widget_properties() -> None:
    """Test updating widget properties."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "properties": {"url": "https://example.com", "title": "Old Title", "icon": "🔗"},
        },
    )
    widget_id = create_response.json()["id"]

    # Update the widget
    response = client.put(
        f"/api/widgets/{widget_id}",
        json={
            "properties": {
                "url": "https://new-url.com",
                "title": "New Title",
                "icon": "✨",
                "description": "Updated description",
            }
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == widget_id
    assert "new-url.com" in data["properties"]["url"]  # URL may or may not have trailing slash
    assert data["properties"]["title"] == "New Title"
    assert data["properties"]["icon"] == "✨"
    assert data["properties"]["description"] == "Updated description"


def test_update_widget_not_found() -> None:
    """Test updating a non-existent widget returns 404."""
    response = client.put(
        "/api/widgets/nonexistent-id",
        json={"properties": {"url": "https://example.com", "title": "Test", "icon": "🔗"}},
    )
    assert response.status_code == 404


def test_update_widget_position() -> None:
    """Test updating widget position."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "properties": {"url": "https://example.com", "title": "Test", "icon": "🔗"},
        },
    )
    widget_id = create_response.json()["id"]

    # Update position
    response = client.patch(f"/api/widgets/{widget_id}/position", json={"position": 10})
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == widget_id
    assert data["position"] == 10


def test_update_position_not_found() -> None:
    """Test updating position of non-existent widget returns 404."""
    response = client.patch("/api/widgets/nonexistent-id/position", json={"position": 5})
    assert response.status_code == 404


def test_delete_widget() -> None:
    """Test deleting a widget."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "properties": {"url": "https://example.com", "title": "Test", "icon": "🔗"},
        },
    )
    widget_id = create_response.json()["id"]

    # Delete the widget
    response = client.delete(f"/api/widgets/{widget_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "deleted"
    assert data["id"] == widget_id

    # Verify widget is gone
    get_response = client.get(f"/api/widgets/{widget_id}")
    assert get_response.status_code == 404


def test_delete_widget_not_found() -> None:
    """Test deleting a non-existent widget returns 404."""
    response = client.delete("/api/widgets/nonexistent-id")
    assert response.status_code == 404


def test_full_workflow() -> None:
    """Test complete widget lifecycle: create, update, delete."""
    # Create
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "iframe",
            "properties": {"url": "http://localhost:8000/widget", "title": "Test Widget", "width": 400, "height": 300},
        },
    )
    assert create_response.status_code == 200
    widget_id = create_response.json()["id"]

    # List
    list_response = client.get("/api/widgets")
    assert len(list_response.json()) == 1

    # Update properties
    update_response = client.put(
        f"/api/widgets/{widget_id}",
        json={"properties": {"url": "http://new-url.com", "title": "Updated Widget", "width": 500, "height": 400}},
    )
    assert update_response.status_code == 200
    assert update_response.json()["properties"]["title"] == "Updated Widget"

    # Update position
    position_response = client.patch(f"/api/widgets/{widget_id}/position", json={"position": 5})
    assert position_response.status_code == 200
    assert position_response.json()["position"] == 5

    # Delete
    delete_response = client.delete(f"/api/widgets/{widget_id}")
    assert delete_response.status_code == 200

    # Verify deleted
    final_list = client.get("/api/widgets")
    assert len(final_list.json()) == 0
