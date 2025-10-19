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

### Installing as a System Service

Good Neighbor can be installed as a systemd user service that automatically starts on boot:

```bash
# From a fresh clone:
make install-service
```

This will:

1. Create a Python virtual environment using uv
1. Install all dependencies
1. Configure a systemd user service
1. Enable the service to start on boot
1. Start the service immediately

The server will be accessible at `http://localhost:8000` and will automatically restart on failure.

### Managing the Service

```bash
# Check if service is running
make service-status

# View live service logs
make service-logs

# Restart the service (e.g., after pulling updates)
make service-restart

# Remove the service
make uninstall-service
```

### Service Details

- **Service Type**: systemd user service (runs as your user, not root)
- **Auto-start**: Enabled by default after installation
- **Auto-restart**: Service automatically restarts on failure
- **Logs**: Available via `journalctl --user -u good-neighbor`
- **Port**: Default 8000 (accessible at http://localhost:8000)

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
