# GOOD--3: Implement widget system with iframe and shortcut widgets

**Created:** 2025-10-18T14:29:03.283203+00:00
**Status:** Planning

## Description

Create a flexible widget system using web components that supports iframe widgets (service monitors) and shortcut widgets (outbound links with icons). Each widget should have multiple view states (normal, hover, edit) and support add/remove/edit operations.

## Acceptance Criteria

### Backend - Widget Data Model & API

- [ ] Widget data model defined with Pydantic schemas
- [ ] Support for multiple widget types (iframe, shortcut, extensible for future types)
- [ ] Widget properties stored as JSON/dict for flexibility
- [ ] API endpoint: `GET /api/widgets` - List all widgets for current user
- [ ] API endpoint: `POST /api/widgets` - Create new widget
- [ ] API endpoint: `PUT /api/widgets/{id}` - Update widget properties
- [ ] API endpoint: `DELETE /api/widgets/{id}` - Remove widget
- [ ] API endpoint: `PATCH /api/widgets/{id}/position` - Update widget position/order
- [ ] Backend tests for all widget endpoints (CRUD operations)
- [ ] Widget data persisted (in-memory store acceptable for MVP, document future DB migration)

### Frontend - Web Component Architecture

- [ ] Base widget web component class defined (shared functionality)
- [ ] Web components use plain HTML/JS (no framework dependencies)
- [ ] Web components registered with CustomElementRegistry
- [ ] Widget view states implemented (normal, hover, edit)
- [ ] Smooth transitions between view states
- [ ] Widget container/grid system for layout

### Iframe Widget Component

- [ ] `<iframe-widget>` custom element created
- [ ] Properties: iframe URL, title, width, height, refresh interval
- [ ] Normal view: displays iframe with title
- [ ] Hover view: shows edit and delete buttons
- [ ] Edit view: form to update iframe URL, title, dimensions, refresh
- [ ] Iframe sandboxing configured for security
- [ ] Auto-refresh functionality (configurable interval)
- [ ] Handles iframe loading states (loading indicator)
- [ ] Examples from service-monitor can be embedded

### Shortcut Widget Component

- [ ] `<shortcut-widget>` custom element created
- [ ] Properties: URL, title, icon (URL or emoji), description
- [ ] Normal view: displays icon, title, clickable link
- [ ] Hover view: shows edit and delete buttons
- [ ] Edit view: form to update URL, title, icon, description
- [ ] Opens links in new tab with security attributes (noopener, noreferrer)
- [ ] Default icon if none provided
- [ ] Visual feedback on hover/click

### Widget Management UI

- [ ] "Add Widget" button/menu in main interface
- [ ] Widget type selector (iframe vs shortcut)
- [ ] Widget creation flow (select type → fill properties → save)
- [ ] Delete confirmation dialog
- [ ] Drag-and-drop to reorder widgets (optional for MVP, document if deferred)
- [ ] Responsive grid layout that adapts to screen size
- [ ] Widgets persist across page reloads

### Integration & Polish

- [ ] Widgets load on page load via API call
- [ ] New widgets appear immediately after creation (optimistic UI)
- [ ] Widget updates reflect immediately
- [ ] Widget deletion animates out smoothly
- [ ] Error handling for failed API calls
- [ ] Loading states while fetching widgets
- [ ] Empty state when no widgets exist ("Add your first widget!")
- [ ] Frontend tests for widget components

### Documentation

- [ ] Widget system architecture documented in code comments
- [ ] README section on adding new widget types
- [ ] Example widget configurations documented

## Implementation Notes

### Widget Data Model (Backend)

**Pydantic Schemas:**

```python
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, HttpUrl

class WidgetType(str, Enum):
    IFRAME = "iframe"
    SHORTCUT = "shortcut"
    # Future: WEATHER, RSS, CUSTOM, etc.

class BaseWidget(BaseModel):
    id: str = Field(..., description="Unique widget identifier (UUID)")
    type: WidgetType
    position: int = Field(default=0, description="Display order")
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class IframeWidgetProperties(BaseModel):
    url: HttpUrl
    title: str
    width: int = 400
    height: int = 300
    refresh_interval: int | None = None  # seconds, None = no refresh

class ShortcutWidgetProperties(BaseModel):
    url: HttpUrl
    title: str
    icon: str  # URL or emoji
    description: str | None = None
```

**In-Memory Store (MVP):**

```python
# For MVP, use a simple dict
# TODO: Migrate to database (SQLite/PostgreSQL) in future story
widgets_store: dict[str, BaseWidget] = {}
```

### Web Component Architecture

**Base Widget Component Pattern:**

```typescript
// base-widget.ts
export abstract class BaseWidget extends HTMLElement {
  protected state: 'normal' | 'hover' | 'edit' = 'normal'

  connectedCallback() {
    this.render()
    this.attachEventListeners()
  }

  abstract render(): void

  protected setState(newState: 'normal' | 'hover' | 'edit') {
    this.state = newState
    this.render()
  }

  protected createDeleteButton(): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.textContent = '🗑️ Delete'
    btn.onclick = () => this.handleDelete()
    return btn
  }

  protected createEditButton(): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.textContent = '✏️ Edit'
    btn.onclick = () => this.setState('edit')
    return btn
  }

  protected async handleDelete() {
    const confirmed = confirm('Delete this widget?')
    if (confirmed) {
      await this.deleteWidget()
    }
  }

  protected abstract deleteWidget(): Promise<void>
  protected abstract saveWidget(): Promise<void>
}
```

**Iframe Widget Component:**

```typescript
// iframe-widget.ts
class IframeWidget extends BaseWidget {
  static get observedAttributes() {
    return ['url', 'title', 'width', 'height', 'refresh-interval']
  }

  render() {
    switch(this.state) {
      case 'normal':
        this.renderNormalView()
        break
      case 'hover':
        this.renderHoverView()
        break
      case 'edit':
        this.renderEditView()
        break
    }
  }

  private renderNormalView() {
    this.innerHTML = `
      <div class="widget-container">
        <h3>${this.getAttribute('title')}</h3>
        <iframe
          src="${this.getAttribute('url')}"
          width="${this.getAttribute('width')}"
          height="${this.getAttribute('height')}"
          sandbox="allow-scripts allow-same-origin"
          loading="lazy"
        ></iframe>
      </div>
    `
  }

  // ... hover and edit views
}

customElements.define('iframe-widget', IframeWidget)
```

**Shortcut Widget Component:**

```typescript
// shortcut-widget.ts
class ShortcutWidget extends BaseWidget {
  static get observedAttributes() {
    return ['url', 'title', 'icon', 'description']
  }

  render() {
    // Similar pattern to iframe widget
    // Normal view: icon + title as clickable link
    // Hover: add edit/delete overlay
    // Edit: form for properties
  }
}

customElements.define('shortcut-widget', ShortcutWidget)
```

### Widget Grid Layout

**CSS Grid for responsive layout:**

```css
.widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.widget-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.widget-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
```

### API Endpoints Design

**FastAPI Routes:**

```python
from fastapi import APIRouter, HTTPException
from uuid import uuid4

router = APIRouter(prefix="/api/widgets", tags=["widgets"])

@router.get("/")
async def list_widgets() -> list[BaseWidget]:
    """Get all widgets for current user (no auth yet, return all)."""
    return list(widgets_store.values())

@router.post("/")
async def create_widget(widget_data: CreateWidgetRequest) -> BaseWidget:
    """Create a new widget."""
    widget_id = str(uuid4())
    widget = BaseWidget(
        id=widget_id,
        type=widget_data.type,
        position=len(widgets_store),
        properties=widget_data.properties,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    widgets_store[widget_id] = widget
    return widget

@router.put("/{widget_id}")
async def update_widget(widget_id: str, update: UpdateWidgetRequest) -> BaseWidget:
    """Update widget properties."""
    if widget_id not in widgets_store:
        raise HTTPException(status_code=404, detail="Widget not found")

    widget = widgets_store[widget_id]
    widget.properties.update(update.properties)
    widget.updated_at = datetime.now()
    return widget

@router.delete("/{widget_id}")
async def delete_widget(widget_id: str) -> dict:
    """Delete a widget."""
    if widget_id not in widgets_store:
        raise HTTPException(status_code=404, detail="Widget not found")

    del widgets_store[widget_id]
    return {"status": "deleted", "id": widget_id}
```

### File Structure

```
frontend/src/
├── components/
│   ├── base-widget.ts          # Abstract base class
│   ├── iframe-widget.ts        # Iframe widget component
│   ├── shortcut-widget.ts      # Shortcut widget component
│   ├── widget-grid.ts          # Grid container component
│   └── add-widget-dialog.ts    # Widget creation UI
├── services/
│   └── widget-api.ts           # API client for widget operations
├── types/
│   └── widget.ts               # TypeScript types matching backend
└── main.ts                     # Register components, init app

src/good_neighbor/
├── api/
│   └── widgets.py              # Widget API endpoints
├── models/
│   └── widget.py               # Pydantic models
└── server.py                   # Mount widget router

tests/
├── test_widget_api.py          # Backend API tests
└── ...

frontend/src/
└── components/
    └── __tests__/
        ├── iframe-widget.test.ts
        └── shortcut-widget.test.ts
```

### Security Considerations

**Iframe Security:**

- Use `sandbox` attribute with minimal permissions
- Consider CSP headers to restrict iframe sources
- Validate iframe URLs on backend (allowlist approach for future)

**Link Security:**

- Use `rel="noopener noreferrer"` on external links
- Sanitize user input for URLs and titles
- Prevent XSS in widget properties

### Future Enhancements (Document, Don't Implement)

- Database persistence (SQLite → PostgreSQL)
- User-specific widgets (after OAuth implementation)
- Widget templates/marketplace
- More widget types (weather, RSS, calendar, stocks)
- Import/export widget configurations
- Widget themes and customization
- Drag-and-drop reordering
- Widget resize handles
- Shared widgets between users
- Widget analytics (usage tracking)

## Testing Strategy

### Backend Tests

```python
def test_create_iframe_widget():
    response = client.post("/api/widgets", json={
        "type": "iframe",
        "properties": {
            "url": "http://localhost:8000/widget/service",
            "title": "Service Monitor",
            "width": 400,
            "height": 300
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "iframe"
    assert data["id"] is not None

def test_create_shortcut_widget():
    # Similar test for shortcut

def test_update_widget_properties():
    # Test PUT endpoint

def test_delete_widget():
    # Test DELETE endpoint

def test_list_widgets():
    # Test GET endpoint with multiple widgets
```

### Frontend Tests

```typescript
describe('IframeWidget', () => {
  it('renders iframe with correct attributes', () => {
    const widget = document.createElement('iframe-widget')
    widget.setAttribute('url', 'http://example.com')
    widget.setAttribute('title', 'Example')
    widget.setAttribute('width', '400')
    widget.setAttribute('height', '300')

    document.body.appendChild(widget)

    const iframe = widget.querySelector('iframe')
    expect(iframe).toBeTruthy()
    expect(iframe?.src).toBe('http://example.com')
  })

  it('shows edit and delete buttons on hover state', () => {
    // Test hover view
  })

  it('renders edit form in edit state', () => {
    // Test edit view
  })
})
```

## Notes

### Development Approach

1. **Start with backend:** Define data models and API endpoints first
1. **Create base widget component:** Establish the pattern for all widgets
1. **Implement iframe widget:** First concrete implementation
1. **Implement shortcut widget:** Second implementation, validate pattern
1. **Build widget grid and management UI:** Bring it all together
1. **Polish and test:** Smooth animations, error handling, comprehensive tests

### Design Philosophy

- **Minimal dependencies:** Use web standards (Web Components) over frameworks
- **Extensibility:** Easy to add new widget types
- **Type safety:** TypeScript types match Pydantic models
- **Progressive enhancement:** Start simple, add features incrementally
- **User feedback:** Clear loading states, error messages, confirmations

### Example Service Monitor Widgets

From `../service-monitor/src/service_monitor/templates/widgets/`:

- `service.html` - Individual service status widget
- `summary.html` - Overall status summary widget
- `critical.html` - Critical alerts widget

These can be embedded via iframe with URLs like:

- `http://localhost:8080/widget/service/my-service`
- `http://localhost:8080/widget/summary`
- `http://localhost:8080/widget/critical`

## Related Issues

- Depends on GOOD--2 (TypeScript/Vite setup) ✅ Complete
- Future: OAuth integration for user-specific widgets
- Future: Database migration for widget persistence
- Future: Widget drag-and-drop reordering
