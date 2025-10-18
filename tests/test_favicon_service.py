"""Tests for favicon service module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from good_neighbor.services.favicon_service import (
    discover_favicon,
    discover_favicon_from_defaults,
    discover_favicon_from_google,
    discover_favicon_from_html,
    extract_domain,
    fetch_favicon_from_url,
    make_absolute_url,
)


def test_extract_domain() -> None:
    """Test domain extraction from URLs."""
    assert extract_domain("https://example.com/page") == "https://example.com"
    assert extract_domain("http://example.com/page") == "http://example.com"
    assert extract_domain("https://example.com") == "https://example.com"
    assert extract_domain("example.com") == "https://example.com"  # Adds https
    assert extract_domain("example.com/page") == "https://example.com"


def test_extract_domain_with_port() -> None:
    """Test domain extraction preserves port numbers."""
    assert extract_domain("https://example.com:8080/page") == "https://example.com:8080"
    assert extract_domain("http://localhost:3000") == "http://localhost:3000"


def test_make_absolute_url() -> None:
    """Test converting relative URLs to absolute."""
    base = "https://example.com"

    # Absolute URLs should remain unchanged
    assert make_absolute_url("https://other.com/favicon.ico", base) == "https://other.com/favicon.ico"

    # Relative URLs should be resolved
    assert make_absolute_url("/favicon.ico", base) == "https://example.com/favicon.ico"
    assert make_absolute_url("favicon.ico", base) == "https://example.com/favicon.ico"
    assert make_absolute_url("../favicon.ico", base) == "https://example.com/favicon.ico"


@pytest.mark.asyncio
async def test_fetch_favicon_from_url_success() -> None:
    """Test successful favicon fetch."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"fake-image-data"
    mock_response.headers = {"content-type": "image/png"}

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await fetch_favicon_from_url(mock_client, "https://example.com/favicon.png")

    assert result is not None
    assert result["format"] == "png"
    assert result["source"] == "https://example.com/favicon.png"
    assert result["data_url"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_fetch_favicon_from_url_not_found() -> None:
    """Test favicon fetch with 404 response."""
    mock_response = Mock()
    mock_response.status_code = 404

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await fetch_favicon_from_url(mock_client, "https://example.com/favicon.png")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_favicon_from_url_too_large() -> None:
    """Test favicon fetch rejects files over size limit."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"x" * (100 * 1024 + 1)  # 100KB + 1 byte
    mock_response.headers = {"content-type": "image/png"}

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await fetch_favicon_from_url(mock_client, "https://example.com/favicon.png")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_favicon_from_url_invalid_content_type() -> None:
    """Test favicon fetch rejects non-image content types."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"fake-data"
    mock_response.headers = {"content-type": "text/html"}

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    result = await fetch_favicon_from_url(mock_client, "https://example.com/favicon.png")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_favicon_from_url_exception() -> None:
    """Test favicon fetch handles exceptions gracefully."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.RequestError("Connection failed")

    result = await fetch_favicon_from_url(mock_client, "https://example.com/favicon.png")

    assert result is None


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.fetch_favicon_from_url")
async def test_discover_favicon_from_html(mock_fetch: AsyncMock) -> None:
    """Test discovering favicon from HTML link tags."""
    html_content = """
    <html>
        <head>
            <link rel="icon" href="/favicon.png">
        </head>
    </html>
    """

    mock_html_response = Mock()
    mock_html_response.status_code = 200
    mock_html_response.text = html_content

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_html_response

    mock_fetch.return_value = {
        "data_url": "data:image/png;base64,test",
        "format": "png",
        "source": "https://example.com/favicon.png",
    }

    result = await discover_favicon_from_html(mock_client, "https://example.com", "https://example.com")

    assert result is not None
    assert result["format"] == "png"
    mock_fetch.assert_called_once()


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.fetch_favicon_from_url")
async def test_discover_favicon_from_html_multiple_icons(mock_fetch: AsyncMock) -> None:
    """Test favicon discovery prefers larger icons."""
    html_content = """
    <html>
        <head>
            <link rel="icon" sizes="16x16" href="/favicon-16.png">
            <link rel="icon" sizes="32x32" href="/favicon-32.png">
            <link rel="icon" sizes="64x64" href="/favicon-64.png">
        </head>
    </html>
    """

    mock_html_response = Mock()
    mock_html_response.status_code = 200
    mock_html_response.text = html_content

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_html_response

    # Return None for first two attempts, success for 64x64
    mock_fetch.side_effect = [
        None,
        None,
        {"data_url": "data:image/png;base64,test", "format": "png", "source": "https://example.com/favicon-64.png"},
    ]

    result = await discover_favicon_from_html(mock_client, "https://example.com", "https://example.com")

    assert result is not None
    # Should try largest size first (64x64)
    calls = mock_fetch.call_args_list
    assert "/favicon-64.png" in str(calls[0])


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.fetch_favicon_from_url")
async def test_discover_favicon_from_defaults(mock_fetch: AsyncMock) -> None:
    """Test discovering favicon from default locations."""
    mock_fetch.side_effect = [
        None,  # /favicon.ico
        {
            "data_url": "data:image/png;base64,test",
            "format": "png",
            "source": "https://example.com/favicon.png",
        },  # /favicon.png
    ]

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    result = await discover_favicon_from_defaults(mock_client, "https://example.com")

    assert result is not None
    assert result["format"] == "png"
    assert mock_fetch.call_count == 2


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.fetch_favicon_from_url")
async def test_discover_favicon_from_google(mock_fetch: AsyncMock) -> None:
    """Test using Google's favicon service as fallback."""
    mock_fetch.return_value = {
        "data_url": "data:image/png;base64,test",
        "format": "png",
        "source": "https://www.google.com/s2/favicons",
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)

    result = await discover_favicon_from_google(mock_client, "https://example.com")

    assert result is not None
    assert result["source"] == "google-favicon-service"
    mock_fetch.assert_called_once()
    # Verify Google URL was used
    call_args = mock_fetch.call_args
    assert "google.com/s2/favicons" in call_args[0][1]
    assert "domain=example.com" in call_args[0][1]


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.discover_favicon_from_html")
@patch("good_neighbor.services.favicon_service.discover_favicon_from_defaults")
@patch("good_neighbor.services.favicon_service.discover_favicon_from_google")
async def test_discover_favicon_strategy_order(
    mock_google: AsyncMock, mock_defaults: AsyncMock, mock_html: AsyncMock
) -> None:
    """Test that discovery strategies are tried in correct order."""
    # HTML succeeds
    mock_html.return_value = {"data_url": "data:image/png;base64,test", "format": "png", "source": "html"}

    result = await discover_favicon("https://example.com", "https://example.com")

    assert result is not None
    mock_html.assert_called_once()
    mock_defaults.assert_not_called()  # Should not try defaults if HTML succeeds
    mock_google.assert_not_called()  # Should not try Google if HTML succeeds


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.discover_favicon_from_html")
@patch("good_neighbor.services.favicon_service.discover_favicon_from_defaults")
@patch("good_neighbor.services.favicon_service.discover_favicon_from_google")
async def test_discover_favicon_fallback_chain(
    mock_google: AsyncMock, mock_defaults: AsyncMock, mock_html: AsyncMock
) -> None:
    """Test fallback chain when earlier strategies fail."""
    # HTML and defaults fail, Google succeeds
    mock_html.return_value = None
    mock_defaults.return_value = None
    mock_google.return_value = {"data_url": "data:image/png;base64,test", "format": "png", "source": "google"}

    result = await discover_favicon("https://example.com", "https://example.com")

    assert result is not None
    assert result["source"] == "google"
    mock_html.assert_called_once()
    mock_defaults.assert_called_once()
    mock_google.assert_called_once()


@pytest.mark.asyncio
@patch("good_neighbor.services.favicon_service.discover_favicon_from_html")
@patch("good_neighbor.services.favicon_service.discover_favicon_from_defaults")
@patch("good_neighbor.services.favicon_service.discover_favicon_from_google")
async def test_discover_favicon_all_fail(
    mock_google: AsyncMock, mock_defaults: AsyncMock, mock_html: AsyncMock
) -> None:
    """Test when all discovery strategies fail."""
    mock_html.return_value = None
    mock_defaults.return_value = None
    mock_google.return_value = None

    result = await discover_favicon("https://example.com", "https://example.com")

    assert result is None
