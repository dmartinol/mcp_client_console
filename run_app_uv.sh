#!/bin/bash
# Modern startup script using uv

set -e

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "🚀 Starting MCP Client Console with uv..."

# Run the application with uv, automatically handling virtual environment and dependencies
uv run streamlit run main.py --server.port 8501 --server.address localhost
