"""Services package for Good Neighbor."""

from good_neighbor.services.favicon_cache import FaviconCache, get_cache
from good_neighbor.services.favicon_service import discover_favicon, extract_domain
from good_neighbor.services.homepage_service import HomepageService
from good_neighbor.services.user_service import UserService
from good_neighbor.services.widget_service import WidgetService

__all__ = [
    # Favicon services
    "FaviconCache",
    "get_cache",
    "discover_favicon",
    "extract_domain",
    # Business logic services
    "UserService",
    "HomepageService",
    "WidgetService",
]
