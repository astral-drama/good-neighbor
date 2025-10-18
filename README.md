# good-neighbor

A customizable homepage widget manager with OAuth authentication, user preferences, and analytics tracking.

## Features

### Full-Stack Architecture

- **Frontend:** TypeScript + Vite with hot module replacement
- **Backend:** Python FastAPI with async support
- **Testing:** Vitest (frontend) + pytest (backend) with 80% coverage minimum
- **Code Quality:** ESLint + Ruff with pre-commit hooks

### Planned Features

- OAuth authentication for multi-user support
- Customizable widget system (iframes + native widgets)
- Link click tracking and analytics
- User preference persistence across devices

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
│   │   ├── main.ts                # Application entry point
│   │   ├── main.test.ts           # Frontend tests
│   │   └── style.css              # Styles
│   ├── vite.config.ts             # Vite configuration with API proxy
│   ├── tsconfig.json              # TypeScript configuration
│   ├── eslint.config.js           # ESLint configuration
│   └── package.json               # Frontend dependencies
├── src/good_neighbor/             # Python backend
│   ├── __init__.py
│   ├── server.py                  # FastAPI server
│   └── core.py                    # Core business logic
├── tests/                         # Backend tests
│   ├── test_server.py             # API endpoint tests
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

### API Endpoints

- `GET /api/health` - Health check endpoint
- More endpoints coming soon (authentication, widgets, preferences, analytics)

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
