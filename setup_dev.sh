#!/bin/bash
# Development environment setup using uv

set -e

echo "🔧 Setting up development environment with uv..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sync development dependencies
echo "📦 Installing development dependencies..."
uv sync --extra dev --extra test

echo "✅ Development environment ready!"
echo ""
echo "🎯 Available commands:"
echo "   uv run pytest                    # Run tests"
echo "   uv run black .                   # Format code"
echo "   uv run isort .                   # Sort imports"
echo "   uv run flake8 mcp_client_console # Lint code"
echo "   uv run mypy mcp_client_console   # Type check"
echo "   uv run streamlit run main.py     # Run application"
