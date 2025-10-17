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

- `make install` - Create venv and install dependencies with uv
- `make test` - Run tests with coverage
- `make lint` - Run linting checks
- `make format` - Format code
- `make type-check` - Run type checking
- `make all` - Run all checks
- `make clean` - Clean build artifacts
- `make help` - Show all available commands

### Direct commands

- `ruff format .` - Format code
- `ruff check .` - Run linting
- `ruff check --fix .` - Auto-fix linting issues
- `pytest --cov=. --cov-report=html` - Run tests with coverage
- `pre-commit run --all-files` - Run all quality checks

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
