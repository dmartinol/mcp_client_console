.PHONY: help install install-dev run test lint format format-check type-check clean build

# Default target
help:
	@echo "🚀 MCP Client Console - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run          Run the Streamlit application"
	@echo "  test         Run all tests"
	@echo "  lint         Run code linting (ruff)"
	@echo "  format       Format code (ruff)"
	@echo "  format-check Check if code is properly formatted (ruff)"
	@echo "  type-check   Run type checking (mypy)"
	@echo ""
	@echo "Quality:"
	@echo "  check        Run all quality checks (lint + format-check + type-check + test)"
	@echo ""
	@echo "Build:"
	@echo "  build        Build the package"
	@echo "  clean        Clean build artifacts"

# Installation
install:
	@echo "📦 Installing production dependencies..."
	uv sync

install-dev:
	@echo "🔧 Installing development dependencies..."
	uv sync --extra dev --extra test

# Development
run:
	@echo "🚀 Starting MCP Client Console..."
	uv run python -m streamlit run main.py --server.port 8501 --server.address localhost

test:
	@echo "🧪 Running tests with coverage..."
	uv run pytest --cov=mcp_client_console --cov-report=term-missing --cov-report=html

lint:
	@echo "🔍 Running linter..."
	uv run ruff check mcp_client_console

format:
	@echo "🎨 Formatting code..."
	uv run ruff check --fix mcp_client_console
	uv run ruff format mcp_client_console

format-check:
	@echo "🔍 Checking code formatting..."
	uv run ruff check mcp_client_console
	uv run ruff format --check mcp_client_console

type-check:
	@echo "🔎 Running type checks..."
	uv run mypy mcp_client_console

# Build
build:
	@echo "🏗️ Building package..."
	uv build

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Quality checks (run all checks)
check: lint format-check type-check test
	@echo "✅ All quality checks passed!"
