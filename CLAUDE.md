# good-neighbor

## Project Overview

A project that manages custom widgets for the purpose of creating a default homepage in your web browser.

## Development Setup

This project uses Python with uv for fast, reliable dependency management.

### Quick Start

```bash
# Create and activate virtual environment using Make and uv
make install

# Or manually with uv:
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Quality Standards

This project follows clean code practices with:

- **Ruff** for linting and formatting (120 char line length)
- **Pre-commit hooks** for automated quality checks
- **Pytest** for testing with 80% minimum coverage
- **Type hints** throughout the codebase

## Development Commands

### Using Make (recommended)

#### Development:

- `make install` - Create venv and install dependencies with uv
- `make test` - Run tests with coverage
- `make lint` - Run linting checks
- `make format` - Format code
- `make type-check` - Run type checking
- `make all` - Run all checks
- `make clean` - Clean build artifacts
- `make help` - Show all available commands

#### Service Management (Production):

- `make install-service` - Install and start systemd user service
- `make uninstall-service` - Stop and remove systemd user service
- `make service-status` - Check service status
- `make service-logs` - View service logs (follows in real-time)
- `make service-restart` - Restart the service

### Direct commands

- `ruff format .` - Format code
- `ruff check .` - Run linting
- `ruff check --fix .` - Auto-fix linting issues
- `pytest --cov=. --cov-report=html` - Run tests with coverage
- `pre-commit run --all-files` - Run all quality checks

## Production Deployment

### Prerequisites

- **Python 3.x** and **uv** (Python package installer)
- **Node.js** and **npm** (for building the frontend)

### Installing as a System Service

Good Neighbor can be installed as a systemd user service that automatically starts on boot:

```bash
# From a fresh clone:
make install-service
```

This will:

1. Create a Python virtual environment using uv
1. Install all Python dependencies
1. Install frontend dependencies (npm install)
1. Build the frontend (compiles to dist/)
1. Configure a systemd user service
1. Enable the service to start on boot
1. Start the service immediately

The server will be accessible at `http://localhost:3000` (production) and will automatically restart on failure.

**Note**: The service runs the FastAPI server which serves both the API (`/api/*`) and the built frontend static files from the `dist/` directory.

**Port Configuration:**

- **Development**: Port 8000 (Vite dev proxy + Python backend)
- **Production**: Port 3000 (systemd service, configurable in Makefile `PROD_PORT`)
- This allows running dev and production servers side-by-side without conflicts

### Managing the Service

```bash
# Check if service is running
make service-status

# View live service logs
make service-logs

# After pulling updates, rebuild frontend and restart
cd frontend && npm run build && cd .. && make service-restart

# Or if only backend changes:
make service-restart

# Remove the service
make uninstall-service
```

### Service Details

- **Service Type**: systemd user service (runs as your user, not root)
- **Auto-start**: Enabled by default after installation
- **Auto-restart**: Service automatically restarts on failure
- **Logs**: Available via `journalctl --user -u good-neighbor`
- **Port**: 3000 (accessible at http://localhost:3000, configurable via `PROD_PORT` in Makefile)

## Project Structure

```
good-neighbor/
├── src/good_neighbor/     # Main package code
├── tests/                 # Test suite
├── .venv/                 # Virtual environment (not in git)
├── Makefile              # Build automation
└── pyproject.toml        # Project configuration
```

## Contributing Guidelines

1. All code must pass linting and formatting checks
1. Tests must maintain 80% minimum coverage
1. Use descriptive commit messages
1. Follow existing code patterns and conventions

## Author

Seth Lakowske <lakowske@gmail.com>
