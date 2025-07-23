#!/bin/bash
# Legacy startup script - redirects to modern uv-based script

echo "⚠️  This script is deprecated. Please use the modern uv-based script:"
echo "   ./run_app_uv.sh"
echo "   OR"
echo "   make run"
echo ""
echo "🔄 Automatically redirecting to uv-based script..."
echo ""

# Check if uv is available
if command -v uv &> /dev/null; then
    exec ./run_app_uv.sh
else
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or use the legacy pip method:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -e ."
    echo "   streamlit run main.py --server.port 8501 --server.address localhost"
    exit 1
fi
