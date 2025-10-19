"""Tests for query widget API endpoints."""

from fastapi.testclient import TestClient

from good_neighbor.server import app

client = TestClient(app)


def test_create_query_widget() -> None:
    """Test creating a query widget."""
    response = client.post(
        "/api/widgets",
        json={
            "type": "query",
            "properties": {
                "url_template": "https://google.com/search?q={query}",
                "title": "Google Search",
                "icon": "🔍",
                "placeholder": "Search Google...",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["type"] == "query"
    assert data["id"] is not None
    assert data["position"] >= 0
    assert data["properties"]["url_template"] == "https://google.com/search?q={query}"
    assert data["properties"]["title"] == "Google Search"
    assert data["properties"]["icon"] == "🔍"
    assert data["properties"]["placeholder"] == "Search Google..."
    assert "created_at" in data
    assert "updated_at" in data


def test_create_query_widget_with_claude_ai() -> None:
    """Test creating a query widget for Claude AI."""
    response = client.post(
        "/api/widgets",
        json={
            "type": "query",
            "properties": {
                "url_template": "https://claude.ai/new?q={query}",
                "title": "Ask Claude",
                "icon": "🤖",
                "placeholder": "Ask Claude...",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["type"] == "query"
    assert data["properties"]["url_template"] == "https://claude.ai/new?q={query}"
    assert data["properties"]["title"] == "Ask Claude"


def test_update_query_widget_properties() -> None:
    """Test updating query widget properties."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "query",
            "properties": {
                "url_template": "https://google.com/search?q={query}",
                "title": "Google",
                "icon": "🔍",
                "placeholder": "Search...",
            },
        },
    )
    widget_id = create_response.json()["id"]

    # Update the widget
    response = client.put(
        f"/api/widgets/{widget_id}",
        json={
            "properties": {
                "url_template": "https://duckduckgo.com/?q={query}",
                "title": "DuckDuckGo",
                "icon": "🦆",
                "placeholder": "Search DuckDuckGo...",
            }
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == widget_id
    assert data["properties"]["url_template"] == "https://duckduckgo.com/?q={query}"
    assert data["properties"]["title"] == "DuckDuckGo"
    assert data["properties"]["icon"] == "🦆"
    assert data["properties"]["placeholder"] == "Search DuckDuckGo..."


def test_get_query_widget_by_id() -> None:
    """Test retrieving a specific query widget by ID."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "query",
            "properties": {
                "url_template": "https://github.com/search?q={query}",
                "title": "GitHub Search",
                "icon": "🐙",
                "placeholder": "Search GitHub...",
            },
        },
    )
    widget_id = create_response.json()["id"]

    # Get the widget
    response = client.get(f"/api/widgets/{widget_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == widget_id
    assert data["type"] == "query"
    assert data["properties"]["title"] == "GitHub Search"


def test_delete_query_widget() -> None:
    """Test deleting a query widget."""
    # Create a widget
    create_response = client.post(
        "/api/widgets",
        json={
            "type": "query",
            "properties": {
                "url_template": "https://google.com/search?q={query}",
                "title": "Search",
                "icon": "🔍",
                "placeholder": "Search...",
            },
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


def test_list_widgets_with_query_widget() -> None:
    """Test listing widgets includes query widgets."""
    # Create widgets of different types
    client.post(
        "/api/widgets",
        json={
            "type": "shortcut",
            "position": 0,
            "properties": {"url": "https://example.com", "title": "Example", "icon": "🔗"},
        },
    )
    client.post(
        "/api/widgets",
        json={
            "type": "query",
            "position": 1,
            "properties": {
                "url_template": "https://google.com/search?q={query}",
                "title": "Search",
                "icon": "🔍",
                "placeholder": "Search...",
            },
        },
    )

    response = client.get("/api/widgets")
    assert response.status_code == 200
    widgets = response.json()

    assert len(widgets) == 2
    # Verify sorted by position
    assert widgets[0]["type"] == "shortcut"
    assert widgets[1]["type"] == "query"


def test_query_widget_url_template_validation() -> None:
    """Test that query widget requires {query} placeholder in url_template."""
    # This test documents expected behavior - in the future we might want
    # to add validation that url_template contains {query}
    response = client.post(
        "/api/widgets",
        json={
            "type": "query",
            "properties": {
                "url_template": "https://google.com/search",  # Missing {query}
                "title": "Search",
                "icon": "🔍",
                "placeholder": "Search...",
            },
        },
    )
    # Currently this succeeds - we might want to add validation in the future
    assert response.status_code == 200
    data = response.json()
    assert data["properties"]["url_template"] == "https://google.com/search"
