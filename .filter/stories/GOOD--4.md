# GOOD--4: Enhance shortcut widget with automatic favicon fetching

**Created:** 2025-10-18T17:52:30.064112+00:00
**Status:** Planning

## Description

Improve the visual experience of shortcut widgets by automatically fetching and displaying favicons from the target URLs. Currently, users must manually specify an icon (emoji or URL) for each shortcut. This enhancement will automatically retrieve the site's favicon, providing accurate, recognizable icons without manual effort.

Users can still override the automatic favicon with a custom icon if desired.

## Acceptance Criteria

### Backend - Favicon Fetching Service

- [ ] Create `/api/favicon` endpoint that accepts a URL and returns favicon
- [ ] Implement favicon discovery with multiple fallback strategies:
  - [ ] Try `/favicon.ico` at domain root
  - [ ] Parse HTML `<link rel="icon">` tags
  - [ ] Parse HTML `<link rel="shortcut icon">` tags
  - [ ] Try `/apple-touch-icon.png` for iOS icons
  - [ ] Support various favicon formats (ico, png, svg, jpg)
- [ ] Return favicon as base64-encoded data URL for easy frontend use
- [ ] Implement caching to avoid repeated fetches for same domain
- [ ] Handle HTTPS/HTTP redirects properly
- [ ] Timeout requests after reasonable duration (5 seconds)
- [ ] Return appropriate error response when favicon not found
- [ ] Log favicon fetch attempts and results

### Frontend - Shortcut Widget Integration

- [ ] Modify shortcut widget to automatically fetch favicon when URL is provided
- [ ] Display loading indicator while fetching favicon
- [ ] Show fetched favicon in normal view
- [ ] Allow manual override of automatic favicon in edit form
- [ ] Add "Use Favicon" button/checkbox in edit form
- [ ] Fall back to emoji icon if favicon fetch fails
- [ ] Update icon immediately when URL changes in edit form
- [ ] Cache fetched favicons client-side (localStorage or memory)
- [ ] Display favicon in widget creation dialog preview

### UI/UX Improvements

- [ ] Show visual feedback when favicon is loading
- [ ] Gracefully handle favicon fetch failures (show default icon)
- [ ] Provide option to manually refresh/retry favicon fetch
- [ ] Display favicon size/format info in edit mode (optional)
- [ ] Ensure favicons scale properly in widget display
- [ ] Support both light and dark mode favicons if available

### Error Handling & Edge Cases

- [ ] Handle CORS issues (favicon fetch through backend proxy)
- [ ] Handle invalid URLs gracefully
- [ ] Handle missing favicons (404 responses)
- [ ] Handle malformed HTML responses
- [ ] Handle timeout scenarios
- [ ] Handle very large favicon files (size limit: 100KB)
- [ ] Handle animated favicons (convert to static or use first frame)
- [ ] Sanitize fetched content for security

### Testing

- [ ] Backend tests for favicon discovery methods
- [ ] Backend tests for caching behavior
- [ ] Backend tests for error scenarios (404, timeout, malformed)
- [ ] Frontend tests for automatic favicon fetching
- [ ] Frontend tests for manual override
- [ ] Frontend tests for fallback behavior
- [ ] Integration test with real websites
- [ ] Test with various favicon formats and locations

### Documentation

- [ ] Document favicon fetching behavior in README
- [ ] Add inline comments explaining favicon discovery logic
- [ ] Document caching strategy and TTL
- [ ] Provide examples of manual icon override

## Implementation Notes

### Favicon Discovery Strategy

Favicons can be located in multiple places. Implement a waterfall approach:

**Discovery Order:**

1. **Parse HTML `<head>` for `<link>` tags:**

   ```html
   <link rel="icon" href="/favicon.ico">
   <link rel="shortcut icon" href="/favicon.png">
   <link rel="apple-touch-icon" href="/apple-icon.png">
   <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
   ```

1. **Try common default locations:**

   - `https://example.com/favicon.ico`
   - `https://example.com/apple-touch-icon.png`
   - `https://example.com/favicon.png`

1. **Use Google's Favicon Service as fallback:**

   - `https://www.google.com/s2/favicons?domain=example.com`
   - `https://www.google.com/s2/favicons?domain=example.com&sz=128`

**Priority by size/quality:**

- Prefer larger sizes (32x32 or higher)
- Prefer PNG/SVG over ICO
- Prefer exact match over generic icons

### Backend API Design

**New Endpoint:**

```python
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx
from bs4 import BeautifulSoup
import base64

router = APIRouter(prefix="/api/favicon", tags=["favicon"])

@router.get("/")
async def get_favicon(url: str = Query(..., description="Target URL to fetch favicon from")) -> dict:
    """
    Fetch favicon for a given URL.

    Returns:
        {
            "success": bool,
            "favicon": str | None,  # Base64 data URL
            "format": str | None,   # "ico", "png", "svg", etc.
            "source": str | None,   # Where the favicon was found
            "error": str | None     # Error message if failed
        }
    """
    try:
        # Extract domain from URL
        domain = extract_domain(url)

        # Check cache first
        cached = get_cached_favicon(domain)
        if cached:
            return cached

        # Try discovery methods
        favicon_data = await discover_favicon(url, domain)

        if favicon_data:
            # Cache for future requests
            cache_favicon(domain, favicon_data)
            return {
                "success": True,
                "favicon": favicon_data["data_url"],
                "format": favicon_data["format"],
                "source": favicon_data["source"],
                "error": None
            }
        else:
            return {
                "success": False,
                "favicon": None,
                "format": None,
                "source": None,
                "error": "No favicon found"
            }
    except Exception as e:
        return {
            "success": False,
            "favicon": None,
            "format": None,
            "source": None,
            "error": str(e)
        }
```

**Favicon Discovery Implementation:**

```python
async def discover_favicon(url: str, domain: str) -> dict | None:
    """
    Discover favicon using multiple strategies.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Strategy 1: Parse HTML for link tags
        try:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for various icon link tags
                for rel in ['icon', 'shortcut icon', 'apple-touch-icon']:
                    link = soup.find('link', rel=rel)
                    if link and link.get('href'):
                        icon_url = make_absolute_url(link['href'], url)
                        favicon = await fetch_favicon_from_url(client, icon_url)
                        if favicon:
                            return favicon
        except:
            pass

        # Strategy 2: Try default locations
        default_paths = ['/favicon.ico', '/favicon.png', '/apple-touch-icon.png']
        for path in default_paths:
            favicon_url = f"{domain}{path}"
            favicon = await fetch_favicon_from_url(client, favicon_url)
            if favicon:
                return favicon

        # Strategy 3: Use Google's favicon service as last resort
        google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        favicon = await fetch_favicon_from_url(client, google_url)
        if favicon:
            favicon['source'] = 'google-favicon-service'
            return favicon

    return None

async def fetch_favicon_from_url(client: httpx.AsyncClient, url: str) -> dict | None:
    """
    Fetch favicon from specific URL and convert to base64 data URL.
    """
    try:
        response = await client.get(url)
        if response.status_code == 200 and len(response.content) < 100_000:  # 100KB limit
            content_type = response.headers.get('content-type', 'image/x-icon')
            b64_data = base64.b64encode(response.content).decode('utf-8')

            return {
                'data_url': f"data:{content_type};base64,{b64_data}",
                'format': content_type.split('/')[-1],
                'source': url
            }
    except:
        pass

    return None
```

### Frontend Integration

**Update Shortcut Widget:**

```typescript
// shortcut-widget.ts
export class ShortcutWidget extends BaseWidget {
  private faviconCache: Map<string, string> = new Map()

  async connectedCallback() {
    super.connectedCallback()

    const url = this.getAttribute('url')
    const icon = this.getAttribute('icon')

    // If no custom icon provided, fetch favicon
    if (url && (!icon || icon === '🔗')) {
      await this.fetchFavicon(url)
    }
  }

  private async fetchFavicon(url: string): Promise<void> {
    // Check client-side cache
    const cached = this.faviconCache.get(url)
    if (cached) {
      this.setAttribute('icon', cached)
      this.render()
      return
    }

    try {
      const response = await fetch(`/api/favicon?url=${encodeURIComponent(url)}`)
      const data = await response.json()

      if (data.success && data.favicon) {
        this.setAttribute('icon', data.favicon)
        this.faviconCache.set(url, data.favicon)
        this.render()
      }
    } catch (error) {
      console.error('Failed to fetch favicon:', error)
      // Keep default emoji icon
    }
  }
}
```

**Update Edit Form:**

```typescript
private renderEditView(): void {
  // ... existing code ...
  this.innerHTML = `
    <div class="widget-container shortcut-widget widget-edit">
      <div class="widget-header">
        <h3 class="widget-title">Edit Shortcut Widget</h3>
      </div>
      <div class="widget-content">
        <form class="widget-edit-form">
          <div class="form-group">
            <label for="shortcut-url">URL:</label>
            <input type="url" id="shortcut-url" name="url" value="${url}" required />
          </div>
          <div class="form-group">
            <label for="shortcut-title">Title:</label>
            <input type="text" id="shortcut-title" name="title" value="${title}" required />
          </div>
          <div class="form-group">
            <label for="shortcut-icon">Icon:</label>
            <div class="icon-input-group">
              <input type="text" id="shortcut-icon" name="icon" value="${icon}" />
              <button type="button" class="fetch-favicon-btn" title="Fetch favicon">🔄</button>
              <label class="checkbox-label">
                <input type="checkbox" id="auto-favicon" checked /> Auto-fetch
              </label>
            </div>
          </div>
          <!-- ... rest of form ... -->
        </form>
      </div>
    </div>
  `

  // Attach fetch favicon button handler
  const fetchBtn = this.querySelector('.fetch-favicon-btn')
  fetchBtn?.addEventListener('click', () => {
    const urlInput = this.querySelector('#shortcut-url') as HTMLInputElement
    if (urlInput.value) {
      this.fetchFavicon(urlInput.value)
    }
  })
}
```

### Caching Strategy

**Backend Cache:**

- In-memory cache with TTL (Time To Live)
- Cache key: domain name
- Cache duration: 24 hours (favicons rarely change)
- Implement LRU (Least Recently Used) eviction
- Consider Redis for production (future enhancement)

**Frontend Cache:**

- Store in memory during session
- Optional: persist to localStorage for cross-session caching
- Cache key: full URL
- Clear cache on widget deletion

```typescript
// Simple in-memory cache
class FaviconCache {
  private cache: Map<string, { data: string; timestamp: number }> = new Map()
  private ttl: number = 24 * 60 * 60 * 1000 // 24 hours

  get(url: string): string | null {
    const entry = this.cache.get(url)
    if (entry && Date.now() - entry.timestamp < this.ttl) {
      return entry.data
    }
    this.cache.delete(url)
    return null
  }

  set(url: string, data: string): void {
    this.cache.set(url, { data, timestamp: Date.now() })
  }
}
```

### Security Considerations

**CORS Handling:**

- Fetch favicons through backend proxy to avoid CORS issues
- Backend makes the external HTTP requests
- Return data URLs to frontend (no external resource loading in browser)

**Content Validation:**

- Verify content-type is an image format
- Limit file size to prevent DoS (max 100KB)
- Scan for malicious content (optional)
- Use content security policy to restrict inline images if needed

**URL Validation:**

- Validate URL format before fetching
- Block localhost/private IP ranges
- Use allowlist for protocols (http, https only)

### File Structure

```
src/good_neighbor/
├── api/
│   └── favicon.py              # New favicon API endpoint
├── services/
│   └── favicon_service.py      # Favicon discovery logic
└── cache/
    └── favicon_cache.py        # Caching implementation

frontend/src/
├── components/
│   └── shortcut-widget.ts      # Updated with favicon fetching
└── services/
    ├── widget-api.ts
    └── favicon-cache.ts        # Client-side favicon cache
```

### Testing Strategy

**Backend Tests:**

```python
def test_fetch_favicon_from_html():
    """Test favicon discovery from HTML link tags."""

def test_fetch_favicon_from_default_location():
    """Test fallback to /favicon.ico."""

def test_fetch_favicon_timeout():
    """Test request timeout handling."""

def test_fetch_favicon_404():
    """Test handling of missing favicons."""

def test_favicon_caching():
    """Test that favicons are cached properly."""

def test_favicon_size_limit():
    """Test that oversized favicons are rejected."""
```

**Frontend Tests:**

```typescript
describe('ShortcutWidget Favicon Fetching', () => {
  it('should fetch favicon automatically on creation', async () => {
    const widget = document.createElement('shortcut-widget')
    widget.setAttribute('url', 'https://example.com')
    document.body.appendChild(widget)

    await waitForFaviconLoad()

    const icon = widget.querySelector('.shortcut-icon')
    expect(icon?.innerHTML).not.toBe('🔗')
  })

  it('should use manual icon override when provided', () => {
    const widget = document.createElement('shortcut-widget')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('icon', '⭐')

    const icon = widget.querySelector('.shortcut-icon')
    expect(icon?.innerHTML).toBe('⭐')
  })
})
```

## Notes

### Alternative Approaches Considered

**Google Favicon Service Only:**

- Pros: Simple, reliable, maintained by Google
- Cons: External dependency, privacy concerns, limited customization
- Decision: Use as fallback, prefer direct fetching

**Client-Side Fetching:**

- Pros: No backend needed
- Cons: CORS issues, exposes user IP to target sites
- Decision: Use backend proxy for privacy and reliability

**Pre-fetch on Backend During Widget Creation:**

- Pros: Immediate display, no loading state
- Cons: Slower widget creation, requires storage
- Decision: Fetch on-demand, cache results

### Future Enhancements

- Support for multiple favicon sizes (16x16, 32x32, 64x64)
- Favicon quality scoring (prefer SVG > PNG > ICO)
- Periodic favicon refresh for updated sites
- Dark mode favicon detection and support
- Favicon gallery/browser for manual selection
- Batch favicon fetching for multiple shortcuts
- CDN caching for popular favicons

## Related Issues

- Builds on GOOD--3 (Widget system implementation) ✅ Complete
- Future: Favicon refresh job (periodic background task)
- Future: Favicon quality detection and auto-upgrade
