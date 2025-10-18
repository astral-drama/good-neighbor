# good-neighbor

A customizable homepage widget manager with OAuth authentication, user preferences, and analytics tracking.

## Features

### Full-Stack Architecture

- **Frontend:** TypeScript + Vite with hot module replacement
- **Backend:** Python FastAPI with async support
- **Testing:** Vitest (frontend) + pytest (backend) with 80% coverage minimum
- **Code Quality:** ESLint + Ruff with pre-commit hooks

### Current Features

- **Widget System:** Full CRUD operations for iframe and shortcut widgets
  - Iframe widgets for embedding external content (e.g., service monitors)
  - Shortcut widgets for quick links with custom icons and descriptions
  - Drag-and-drop repositioning (coming soon)
  - Inline editing with live preview
  - Auto-refresh for iframe widgets
- **Web Components:** Framework-agnostic custom elements
  - State management (normal, hover, edit)
  - Built-in security (HTML escaping, iframe sandboxing)
  - Responsive grid layout

### Planned Features

- OAuth authentication for multi-user support
- Link click tracking and analytics
- User preference persistence across devices
- Drag-and-drop widget repositioning
- Database persistence (currently in-memory)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/astral-drama/good-neighbor.git
cd good-neighbor
```

2. Install Python dependencies:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with uv (fastest)
uv pip install -e ".[dev]"

# Or use Make
make install
```

3. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

4. Install pre-commit hooks:

```bash
pre-commit install
```

## Development

### Running the Development Servers

**Option 1: Run both servers in separate terminals**

Terminal 1 - Backend Server:

```bash
source .venv/bin/activate
python -m good_neighbor.server
# Server runs on http://localhost:8000
```

Terminal 2 - Frontend Dev Server:

```bash
cd frontend
npm run dev
# Server runs on http://localhost:5173
# Visit this URL in your browser
```

**Option 2: Using Make (if configured)**

```bash
make dev  # Runs both servers (if configured)
```

The Vite dev server will proxy `/api/*` requests to the Python backend at `localhost:8000`.

## Widget System

The widget system provides a flexible way to create customizable homepage widgets using plain Web Components (no framework dependencies).

### Widget Types

#### Iframe Widget

Embeds external content in a sandboxed iframe.

**Properties:**

- `url` (required): URL of the content to embed
- `title` (required): Display title for the widget
- `width` (default: 400): Width in pixels
- `height` (default: 300): Height in pixels
- `refresh_interval` (optional): Auto-refresh interval in seconds

**Example API Request:**

```json
{
  "type": "iframe",
  "properties": {
    "url": "https://status.example.com",
    "title": "Service Monitor",
    "width": 600,
    "height": 400,
    "refresh_interval": 60
  }
}
```

#### Shortcut Widget

Creates a clickable link with icon and description. **Automatic favicon fetching** is supported - when creating a shortcut with the default icon (🔗), the system will automatically fetch and display the website's favicon.

**Properties:**

- `url` (required): Target URL for the shortcut
- `title` (required): Display title
- `icon` (default: 🔗): Icon (emoji, image URL, or auto-fetched favicon)
- `description` (optional): Optional description text

**Example API Request:**

```json
{
  "type": "shortcut",
  "properties": {
    "url": "https://github.com",
    "title": "GitHub",
    "icon": "🐙",
    "description": "Code hosting and collaboration"
  }
}
```

**Automatic Favicon Fetching:**

- Leave `icon` as "🔗" (or omit it) to auto-fetch the website's favicon
- The system tries multiple strategies:
  1. Parse HTML for `<link rel="icon">` tags
  1. Try default locations (`/favicon.ico`, `/favicon.png`, etc.)
  1. Fall back to Google's favicon service
- Favicons are cached server-side for 24 hours
- Supported formats: PNG, ICO, SVG, and more

### Widget Interactions

**Normal View:** Displays the widget content

**Hover View:** Shows edit and delete buttons when hovering over a widget

**Edit View:** Inline form for editing widget properties

### Security Features

- **HTML Escaping:** All user-provided text is escaped to prevent XSS
- **Iframe Sandboxing:** Iframes use `sandbox="allow-scripts allow-same-origin allow-forms"`
- **External Links:** Shortcuts use `rel="noopener noreferrer"` for security

### API Endpoints

#### Widget CRUD Operations

- `GET /api/widgets` - List all widgets (sorted by position)
- `POST /api/widgets` - Create a new widget
- `GET /api/widgets/{widget_id}` - Get a specific widget
- `PUT /api/widgets/{widget_id}` - Update widget properties
- `PATCH /api/widgets/{widget_id}/position` - Update widget position
- `DELETE /api/widgets/{widget_id}` - Delete a widget

**Example: Creating a Widget**

```bash
curl -X POST http://localhost:8000/api/widgets \
  -H "Content-Type: application/json" \
  -d '{
    "type": "shortcut",
    "properties": {
      "url": "https://example.com",
      "title": "Example Site",
      "icon": "🌐",
      "description": "An example shortcut"
    }
  }'
```

**Example: Updating a Widget**

```bash
curl -X PUT http://localhost:8000/api/widgets/{widget_id} \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "url": "https://updated.com",
      "title": "Updated Title",
      "icon": "⭐"
    }
  }'
```

#### Favicon API

- `GET /api/favicon/?url={url}` - Fetch favicon for a given URL
- `DELETE /api/favicon/cache?domain={domain}` - Clear favicon cache (optional domain parameter)
- `GET /api/favicon/stats` - Get favicon cache statistics

**Example: Fetching a Favicon**

```bash
curl "http://localhost:8000/api/favicon/?url=https://github.com"
```

**Response:**

```json
{
  "success": true,
  "favicon": "data:image/png;base64,iVBORw0KG...",
  "format": "png",
  "source": "https://github.com/favicon.ico",
  "error": null
}
```

**Features:**

- Multi-strategy discovery (HTML parsing → default locations → Google fallback)
- Server-side caching with 24-hour TTL
- Base64 data URLs (avoids CORS issues)
- Support for PNG, ICO, SVG, and other image formats
- Automatic size validation (max 100KB)
- Cache management endpoints for manual cache control

### Testing

**Backend Tests:**

```bash
# Run all backend tests
make test

# Or use pytest directly
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

**Frontend Tests:**

```bash
cd frontend

# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui
```

### Code Quality

**Backend (Python):**

```bash
# Format code
make format
# or: ruff format .

# Lint code
make lint
# or: ruff check .

# Type check
make type-check
# or: mypy .

# Run all checks
make all
```

**Frontend (TypeScript):**

```bash
cd frontend

# Lint
npm run lint

# Lint with auto-fix
npm run lint:fix
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build
# Output goes to ../dist/

# Run backend in production mode (serves static files from dist/)
cd ..
python -m good_neighbor.server
# Visit http://localhost:8000
```

## Project Structure

```
good-neighbor/
├── frontend/                       # Vite + TypeScript frontend
│   ├── src/
│   │   ├── components/            # Web Components
│   │   │   ├── base-widget.ts     # Abstract base class for widgets
│   │   │   ├── iframe-widget.ts   # Iframe widget component
│   │   │   ├── shortcut-widget.ts # Shortcut widget component
│   │   │   ├── widget-grid.ts     # Widget container/grid
│   │   │   ├── add-widget-dialog.ts # Widget creation dialog
│   │   │   └── *.test.ts          # Component tests
│   │   ├── services/              # API service layer
│   │   │   ├── widget-api.ts      # Widget API client
│   │   │   └── widget-api.test.ts # API client tests
│   │   ├── types/                 # TypeScript type definitions
│   │   │   └── widget.ts          # Widget types (matches backend)
│   │   ├── main.ts                # Application entry point
│   │   ├── main.test.ts           # Frontend tests
│   │   └── style.css              # Styles (including widget styles)
│   ├── vite.config.ts             # Vite configuration with API proxy
│   ├── tsconfig.json              # TypeScript configuration
│   ├── eslint.config.js           # ESLint configuration
│   └── package.json               # Frontend dependencies
├── src/good_neighbor/             # Python backend
│   ├── api/                       # API routers
│   │   └── widgets.py             # Widget CRUD endpoints
│   ├── models/                    # Pydantic models
│   │   └── widget.py              # Widget data models
│   ├── __init__.py
│   ├── server.py                  # FastAPI server
│   └── core.py                    # Core business logic
├── tests/                         # Backend tests
│   ├── test_server.py             # API endpoint tests
│   ├── test_widget_api.py         # Widget API tests (14 tests)
│   └── test_core.py               # Core logic tests
├── dist/                          # Frontend build output (gitignored)
├── .filter/                       # Kanban project management
├── .claude/                       # Claude Code skills
├── pyproject.toml                 # Python project configuration
└── README.md                      # This file
```

## Architecture

### Development Mode

- **Frontend:** Vite dev server (port 5173) with HMR
- **Backend:** Python/FastAPI server (port 8000) for API endpoints
- **Proxy:** Vite proxies `/api/*` requests to backend

### Production Mode

- Frontend builds to `dist/` directory
- Python server serves static files from `dist/` AND handles API requests
- Single deployment with FastAPI serving everything

## Test Coverage

- **Backend:** 83 tests with comprehensive coverage
  - 43 favicon service tests (API, cache, and service layer)
  - 40 widget and core functionality tests
- **Frontend:** 32 tests covering all widget components
- All code passes strict linting (ESLint + Ruff) and type checking (TypeScript + mypy)

## Contributing

1. Fork the repository
1. Create a feature branch: `git checkout -b feature/amazing-feature`
1. Make your changes and run the quality checks
1. Commit your changes: `git commit -m 'Add amazing feature'`
1. Push to the branch: `git push origin feature/amazing-feature`
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Seth Lakowske - lakowske@gmail.com
