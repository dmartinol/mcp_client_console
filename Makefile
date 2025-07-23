.PHONY: help install install-dev run test lint format type-check clean build

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
	@echo "  lint         Run code linting (flake8)"
	@echo "  format       Format code (autoflake + isort + black)"
	@echo "  type-check   Run type checking (mypy)"
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
	uv run flake8 mcp_client_console

format:
	@echo "🎨 Formatting code..."
	uv run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive .
	uv run isort .
	uv run black .

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
check: lint type-check test
	@echo "✅ All quality checks passed!"
