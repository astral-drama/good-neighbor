"""Favicon fetching and discovery service."""

import base64
import logging
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Maximum size for favicon files (100KB)
MAX_FAVICON_SIZE = 100 * 1024

# Request timeout in seconds
REQUEST_TIMEOUT = 5.0


def extract_domain(url: str) -> str:
    """Extract the base domain from a URL.

    Args:
        url: Full URL string

    Returns:
        Base domain with protocol (e.g., 'https://example.com')
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        # Add https if no scheme provided
        url = f"https://{url}"
        parsed = urlparse(url)

    return f"{parsed.scheme}://{parsed.netloc}"


def make_absolute_url(href: str, base_url: str) -> str:
    """Convert a potentially relative URL to absolute.

    Args:
        href: URL that might be relative
        base_url: Base URL to resolve against

    Returns:
        Absolute URL
    """
    return urljoin(base_url, href)


async def fetch_favicon_from_url(client: httpx.AsyncClient, url: str) -> Optional[dict[str, str]]:
    """Fetch favicon from a specific URL and convert to base64 data URL.

    Args:
        client: HTTP client to use for requests
        url: URL to fetch favicon from

    Returns:
        Dict with favicon data or None if fetch failed:
        {
            'data_url': str,  # Base64 encoded data URL
            'format': str,    # Image format (ico, png, svg, etc.)
            'source': str     # Where favicon was found
        }
    """
    try:
        logger.debug(f"Attempting to fetch favicon from: {url}")
        response = await client.get(url, follow_redirects=True)

        if response.status_code == 200 and len(response.content) <= MAX_FAVICON_SIZE:
            content_type = response.headers.get("content-type", "image/x-icon")

            # Validate it's an image
            if not content_type.startswith("image/"):
                logger.debug(f"Invalid content-type for favicon: {content_type}")
                return None

            b64_data = base64.b64encode(response.content).decode("utf-8")
            img_format = content_type.split("/")[-1].split(";")[0]

            logger.info(
                f"Successfully fetched favicon - url: {url}, format: {img_format}, size: {len(response.content)}"
            )
            return {"data_url": f"data:{content_type};base64,{b64_data}", "format": img_format, "source": url}
        logger.debug(
            f"Favicon fetch failed - url: {url}, status: {response.status_code}, size: {len(response.content)}"
        )  # noqa: E501

    except Exception as e:
        logger.debug(f"Exception fetching favicon from {url}: {str(e)}")

    return None


async def discover_favicon_from_html(client: httpx.AsyncClient, url: str, domain: str) -> Optional[dict[str, str]]:
    """Discover favicon by parsing HTML link tags.

    Args:
        client: HTTP client to use
        url: Page URL to parse
        domain: Base domain

    Returns:
        Favicon data or None
    """
    try:
        logger.debug(f"Parsing HTML for favicon - url: {url}")
        response = await client.get(url, follow_redirects=True)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for various icon link tags in order of preference
        icon_rels = [
            "icon",
            "shortcut icon",
            "apple-touch-icon",
            "apple-touch-icon-precomposed",
        ]

        for icon_rel in icon_rels:
            # Find all matching link tags
            def _match_rel(r: str, rel_type: str = icon_rel) -> bool:
                return bool(r and rel_type in r.lower()) if r else False

            links = soup.find_all("link", rel=_match_rel)

            # Sort by size preference (larger is better)
            for link in sorted(links, key=lambda link_tag: _get_icon_size(link_tag), reverse=True):
                href = link.get("href")
                if href:
                    icon_url = make_absolute_url(href, domain)
                    favicon = await fetch_favicon_from_url(client, icon_url)
                    if favicon:
                        logger.info(f"Found favicon in HTML - rel: {icon_rel}, url: {icon_url}")
                        return favicon

    except Exception as e:
        logger.debug(f"Error parsing HTML for favicon: {str(e)}")

    return None


def _get_icon_size(link_tag) -> int:  # type: ignore[no-untyped-def]
    """Extract icon size from link tag for sorting preference.

    Args:
        link_tag: BeautifulSoup link tag

    Returns:
        Size in pixels (or 0 if not specified)
    """
    sizes = link_tag.get("sizes", "")
    if sizes and sizes != "any":
        # Parse "32x32" or "64x64" format
        try:
            return int(sizes.split("x")[0])
        except (ValueError, IndexError):
            pass
    return 0


async def discover_favicon_from_defaults(client: httpx.AsyncClient, domain: str) -> Optional[dict[str, str]]:
    """Try common default favicon locations.

    Args:
        client: HTTP client to use
        domain: Base domain

    Returns:
        Favicon data or None
    """
    default_paths = [
        "/favicon.ico",
        "/favicon.png",
        "/apple-touch-icon.png",
        "/apple-touch-icon-precomposed.png",
    ]

    for path in default_paths:
        favicon_url = f"{domain}{path}"
        favicon = await fetch_favicon_from_url(client, favicon_url)
        if favicon:
            logger.info(f"Found favicon at default location: {favicon_url}")
            return favicon

    return None


async def discover_favicon_from_google(client: httpx.AsyncClient, domain: str) -> Optional[dict[str, str]]:
    """Use Google's favicon service as last resort.

    Args:
        client: HTTP client to use
        domain: Base domain

    Returns:
        Favicon data or None
    """
    # Extract just the domain name without protocol
    domain_name = urlparse(domain).netloc or domain.replace("https://", "").replace("http://", "")

    # Use larger size for better quality
    google_url = f"https://www.google.com/s2/favicons?domain={domain_name}&sz=64"

    favicon = await fetch_favicon_from_url(client, google_url)
    if favicon:
        favicon["source"] = "google-favicon-service"
        logger.info(f"Retrieved favicon from Google service for domain: {domain_name}")
        return favicon

    return None


async def discover_favicon(url: str, domain: str) -> Optional[dict[str, str]]:
    """Discover favicon using multiple strategies.

    Tries in order:
    1. Parse HTML for link tags
    2. Try default locations (/favicon.ico, etc.)
    3. Use Google's favicon service as fallback

    Args:
        url: Full URL to the page
        domain: Base domain

    Returns:
        Dict with favicon data or None if not found
    """
    logger.info(f"Starting favicon discovery - url: {url}, domain: {domain}")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        # Strategy 1: Parse HTML for link tags
        favicon = await discover_favicon_from_html(client, url, domain)
        if favicon:
            return favicon

        # Strategy 2: Try default locations
        favicon = await discover_favicon_from_defaults(client, domain)
        if favicon:
            return favicon

        # Strategy 3: Use Google's favicon service
        favicon = await discover_favicon_from_google(client, domain)
        if favicon:
            return favicon

    logger.info(f"No favicon found for url: {url}")
    return None
