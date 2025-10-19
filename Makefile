# Makefile for clean-python template
# This provides convenient shortcuts for common development tasks

SHELL := /bin/bash
PYTHON := python3
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
PROJECT_DIR := $(shell pwd)
SERVICE_NAME := good-neighbor
SYSTEMD_USER_DIR := $(HOME)/.config/systemd/user
SERVICE_FILE := $(SYSTEMD_USER_DIR)/$(SERVICE_NAME).service

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install test lint format type-check docs clean all pre-commit
.PHONY: install-service uninstall-service service-status service-logs service-restart

# Default target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Development:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install development dependencies using uv"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with ruff"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  docs         - Build documentation"
	@echo "  clean        - Clean build artifacts"
	@echo "  pre-commit   - Run all pre-commit checks"
	@echo "  all          - Run all checks (lint, format, type-check, test)"
	@echo ""
	@echo "Service Management:"
	@echo "  install-service   - Install and start systemd user service"
	@echo "  uninstall-service - Stop and remove systemd user service"
	@echo "  service-status    - Check service status"
	@echo "  service-logs      - View service logs"
	@echo "  service-restart   - Restart the service"

# Create virtual environment using uv
$(VENV_DIR):
	@echo -e "$(YELLOW)Creating virtual environment with uv...$(NC)"
	uv venv $(VENV_DIR)
	@echo -e "$(GREEN)✓ Virtual environment created at $(VENV_DIR)$(NC)"

# Install dependencies using uv
install: $(VENV_DIR)
	@echo "Installing development dependencies with uv..."
	uv pip install --python $(VENV_PYTHON) -e ".[dev]"

# Run tests with coverage
test:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80 --cov-report=html

# Run linting
lint:
	ruff check .

# Format code
format:
	ruff format .

# Run type checking
type-check:
	mypy src

# Build documentation
docs:
	@if [ -f "mkdocs.yml" ]; then \
		mkdocs build; \
	else \
		echo "No mkdocs.yml found. Run 'mkdocs new .' to initialize docs."; \
	fi

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run pre-commit checks
pre-commit:
	pre-commit run --all-files

# Run all checks
all: lint format type-check test
	@echo "All checks passed!"

# ============================================================================
# Service Management Targets
# ============================================================================

# Install systemd user service
install-service: install
	@echo -e "$(YELLOW)Installing Good Neighbor systemd service...$(NC)"
	@# Build frontend
	@echo -e "$(YELLOW)Building frontend...$(NC)"
	@cd frontend && npm install && npm run build
	@echo -e "$(GREEN)✓ Frontend built to dist/$(NC)"
	@# Create systemd user directory if it doesn't exist
	@mkdir -p $(SYSTEMD_USER_DIR)
	@# Generate service file from template
	@sed -e 's|{{WORKING_DIR}}|$(PROJECT_DIR)|g' \
	     -e 's|{{VENV_PYTHON}}|$(PROJECT_DIR)/$(VENV_PYTHON)|g' \
	     -e 's|{{VENV_DIR}}|$(PROJECT_DIR)/$(VENV_DIR)|g' \
	     systemd/$(SERVICE_NAME).service.template > $(SERVICE_FILE)
	@echo -e "$(GREEN)✓ Service file created at $(SERVICE_FILE)$(NC)"
	@# Reload systemd daemon
	@systemctl --user daemon-reload
	@echo -e "$(GREEN)✓ Systemd daemon reloaded$(NC)"
	@# Enable service to start on boot
	@systemctl --user enable $(SERVICE_NAME).service
	@echo -e "$(GREEN)✓ Service enabled for auto-start$(NC)"
	@# Start the service
	@systemctl --user start $(SERVICE_NAME).service
	@echo -e "$(GREEN)✓ Service started$(NC)"
	@echo ""
	@echo -e "$(GREEN)Good Neighbor service installed successfully!$(NC)"
	@echo "Check status with: make service-status"
	@echo "View logs with: make service-logs"

# Uninstall systemd user service
uninstall-service:
	@echo -e "$(YELLOW)Uninstalling Good Neighbor systemd service...$(NC)"
	@# Stop the service if running
	@systemctl --user stop $(SERVICE_NAME).service 2>/dev/null || true
	@echo -e "$(GREEN)✓ Service stopped$(NC)"
	@# Disable the service
	@systemctl --user disable $(SERVICE_NAME).service 2>/dev/null || true
	@echo -e "$(GREEN)✓ Service disabled$(NC)"
	@# Remove service file
	@rm -f $(SERVICE_FILE)
	@echo -e "$(GREEN)✓ Service file removed$(NC)"
	@# Reload systemd daemon
	@systemctl --user daemon-reload
	@echo -e "$(GREEN)✓ Systemd daemon reloaded$(NC)"
	@echo ""
	@echo -e "$(GREEN)Good Neighbor service uninstalled successfully!$(NC)"

# Check service status
service-status:
	@systemctl --user status $(SERVICE_NAME).service

# View service logs
service-logs:
	@journalctl --user -u $(SERVICE_NAME).service -f

# Restart the service
service-restart:
	@echo -e "$(YELLOW)Restarting Good Neighbor service...$(NC)"
	@systemctl --user restart $(SERVICE_NAME).service
	@echo -e "$(GREEN)✓ Service restarted$(NC)"
	@systemctl --user status $(SERVICE_NAME).service --no-pager
