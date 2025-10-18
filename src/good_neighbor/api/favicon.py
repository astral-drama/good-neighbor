"""Favicon API endpoints."""

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from good_neighbor.services.favicon_cache import get_cache
from good_neighbor.services.favicon_service import discover_favicon, extract_domain

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/favicon", tags=["favicon"])


@router.get("/")  # type: ignore[misc]
async def get_favicon(url: str = Query(..., description="URL to fetch favicon for")) -> dict[str, Any]:
    """Fetch favicon for a given URL.

    Tries multiple strategies in order:
    1. Check in-memory cache
    2. Parse HTML for link tags
    3. Try default locations (/favicon.ico, etc.)
    4. Use Google's favicon service as fallback

    Args:
        url: The URL to fetch favicon for

    Returns:
        dict: Favicon data with format:
            {
                'success': bool,
                'favicon': str | null,  # Base64 data URL
                'format': str | null,   # Image format (ico, png, svg)
                'source': str | null,   # Where favicon was found
                'error': str | null     # Error message if failed
            }

    Raises:
        HTTPException: If URL validation fails
    """
    if not url or not url.strip():
        logger.warning("Empty URL provided for favicon fetch")
        raise HTTPException(status_code=400, detail="URL parameter is required")

    logger.info(f"Favicon request received - url: {url}")

    try:
        # Extract domain for caching and discovery
        domain = extract_domain(url)
        logger.debug(f"Extracted domain - url: {url}, domain: {domain}")

        # Check cache first
        cache = get_cache()
        cached_favicon = cache.get(domain)

        if cached_favicon:
            logger.info(f"Favicon cache hit - domain: {domain}")
            return {
                "success": True,
                "favicon": cached_favicon["data_url"],
                "format": cached_favicon["format"],
                "source": f"{cached_favicon['source']} (cached)",
                "error": None,
            }

        # Not in cache - discover favicon
        logger.info(f"Favicon cache miss - discovering - domain: {domain}")
        favicon_data: Optional[dict[str, str]] = await discover_favicon(url, domain)

        if favicon_data:
            # Cache the result
            cache.set(domain, favicon_data)
            logger.info(f"Favicon discovered and cached - domain: {domain}, source: {favicon_data['source']}")

            return {
                "success": True,
                "favicon": favicon_data["data_url"],
                "format": favicon_data["format"],
                "source": favicon_data["source"],
                "error": None,
            }

        # No favicon found
        logger.info(f"No favicon found - domain: {domain}")
        return {"success": False, "favicon": None, "format": None, "source": None, "error": "No favicon found"}

    except ValueError as e:
        logger.warning(f"Invalid URL provided - url: {url}, error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error fetching favicon - url: {url}, error: {str(e)}")
        return {
            "success": False,
            "favicon": None,
            "format": None,
            "source": None,
            "error": f"Failed to fetch favicon: {str(e)}",
        }


@router.delete("/cache")  # type: ignore[misc]
async def clear_favicon_cache(
    domain: Optional[str] = Query(None, description="Specific domain to clear"),
) -> dict[str, Any]:
    """Clear the favicon cache.

    Args:
        domain: Optional specific domain to clear, or None to clear all

    Returns:
        dict: Status message
    """
    cache = get_cache()
    cache.clear(domain)

    if domain:
        logger.info(f"Cleared favicon cache for domain: {domain}")
        return {"status": "cleared", "domain": domain}

    logger.info("Cleared entire favicon cache")
    return {"status": "cleared", "domain": "all"}


@router.get("/stats")  # type: ignore[misc]
async def get_cache_stats() -> dict[str, Any]:
    """Get favicon cache statistics.

    Returns:
        dict: Cache statistics (size, max_size, ttl)
    """
    cache = get_cache()
    stats = cache.get_stats()
    logger.debug(f"Cache stats requested - size: {stats['size']}/{stats['max_size']}")
    return stats  # type: ignore[no-any-return]
