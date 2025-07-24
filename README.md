# MCP Client Test Console

[![CI](https://github.com/dmartinol/mcp_client_console/actions/workflows/ci.yml/badge.svg)](https://github.com/dmartinol/mcp_client_console/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-50%25-yellow.svg)](https://codecov.io/gh/dmartinol/mcp_client_console)
[![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/dmartinol/mcp_client_console/blob/main/LICENSE)
[![MCP Version](https://img.shields.io/badge/MCP-1.0.0-blue.svg)](https://modelcontextprotocol.io/)

A simple Python UI to test MCP (Model Context Protocol) servers for compliance with the MCP protocol.

## Features

- **Multiple Transport Support**: Connect via STDIO, SSE, or HTTP
- **Server Exploration**: List and examine tools, prompts, and resources
- **Interactive Web UI**: Built with Streamlit for easy use
- **Protocol Compliance Testing**: Verify MCP server implementations
- **Tool Execution**: Execute individual tools with dynamic form generation
- **Smart Form Generation**: Automatically creates input forms based on tool schemas
- **Default Value Handling**: Pre-fills forms with schema defaults or natural defaults
- **Comprehensive Error Handling**: Detailed error reporting for debugging

## Installation

### Modern Installation (Recommended - using uv)

1. Install [uv](https://github.com/astral-sh/uv) if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone or download this project

3. Install dependencies (uv handles virtual environment automatically):
   ```bash
   uv sync
   ```

### Legacy Installation (using pip)

If you prefer the traditional approach:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

### Running the Application

#### Modern way (using uv):
```bash
# Quick start (recommended)
./run_app_uv.sh

# Or using make
make run

# Or directly with uv
uv run streamlit run main.py
```

#### Legacy way (using pip):
```bash
# Using the provided script (auto-redirects to uv)
./run_app.sh

# Or manually with pip/venv
source venv/bin/activate
streamlit run main.py
```

The application will start on `http://localhost:8501`

### Connection Types

#### STDIO Connection
- **Use case**: Connect to local MCP server processes
- **Configuration**: 
  - Command: The executable command (e.g., `python`, `node`)
  - Arguments: Space-separated arguments (e.g., `server.py --port 8000`)

#### SSE Connection
- **Use case**: Connect via Server-Sent Events
- **Configuration**:
  - SSE URL: The SSE endpoint URL (e.g., `http://localhost:8000/sse`)

#### HTTP Connection
- **Use case**: Connect via HTTP transport
- **Configuration**:
  - Base URL: The server's base URL (e.g., `http://localhost:8000`)

## Project Structure

```
mcp-client/
├── mcp_client_console/          # Main Python package
│   ├── core/                    # Core business logic
│   │   ├── client.py           # MCP client service layer
│   │   ├── models.py           # Data models
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── __init__.py
│   ├── connections/            # Connection implementations
│   │   ├── base.py            # Abstract connection interface
│   │   ├── stdio_connection.py # STDIO transport
│   │   ├── sse_connection.py   # SSE transport
│   │   ├── http_connection.py  # HTTP transport
│   │   ├── factory.py         # Connection factory
│   │   └── __init__.py
│   ├── utils/                  # Utility modules
│   │   ├── error_handler.py   # Centralized error handling
│   │   ├── logger.py          # Logging configuration
│   │   └── __init__.py
│   ├── ui/                     # UI components
│   │   ├── streamlit_app.py   # Streamlit application
│   │   └── __init__.py
│   └── __init__.py             # Package initialization
├── main.py                     # Application entry point
├── pyproject.toml             # Modern Python project config
├── Makefile                   # Development commands
├── run_app_uv.sh             # Modern uv-based startup script
├── setup_dev.sh              # Development environment setup
├── run_app.sh                # Legacy startup script (redirects)
├── .gitignore                 # Git ignore patterns
└── README.md                 # This file
```

## Dependencies

- `mcp>=1.0.0` - Model Context Protocol library
- `streamlit>=1.28.0` - Web UI framework
- `aiohttp>=3.8.0` - HTTP client for async operations
- `websockets>=11.0.0` - WebSocket support
- `requests>=2.28.0` - HTTP requests
- `json5>=0.9.0` - JSON5 parsing
- `pydantic>=2.0.0` - Data validation

## Testing Your MCP Server

1. Start your MCP server
2. Launch this client application
3. Choose the appropriate connection type
4. Configure the connection parameters
5. Click "Connect"
6. Explore the server's capabilities in the tabs:
   - **Tools**: Available tools and their schemas
   - **Prompts**: Available prompts and their parameters
   - **Resources**: Available resources and their metadata

### Tool Execution

Once connected, you can execute individual tools:

1. **Navigate to the Tools tab**
2. **Expand a tool** to see its details and execution form
3. **Fill in the parameters** - the form is automatically generated based on the tool's schema:
   - **String fields**: Text input boxes
   - **Number fields**: Numeric input with appropriate defaults (0 for numbers)
   - **Boolean fields**: Checkboxes with appropriate defaults (false)
   - **Array fields**: JSON text areas for complex data
4. **Click "Execute Tool"** to run the tool with your parameters
5. **View results** - success messages, return values, or detailed error information

#### Form Features:
- **Default Values**: Fields are pre-populated with schema defaults or natural type defaults
- **Type Validation**: Appropriate input types for different parameter types
- **Error Handling**: Clear error messages with detailed debugging information
- **Result Display**: Formatted output showing tool execution results

## Development

### Code Quality Tools

This project uses modern Python development tools for fast and reliable code quality:

- **Ruff**: Lightning-fast Python linter and formatter that replaces flake8, black, and isort
  - `make lint`: Check for code quality issues
  - `make format`: Format code and fix auto-fixable issues
  - Configured in `pyproject.toml` with sensible defaults

- **MyPy**: Static type checking for Python
  - `make type-check`: Run type checking

- **Pytest**: Testing framework with coverage reporting
  - `make test`: Run tests with coverage

### Tips for Using Ruff

```bash
# Check for issues without fixing
uv run ruff check mcp_client_console

# Check and fix auto-fixable issues
uv run ruff check --fix mcp_client_console

# Format code (like black)
uv run ruff format mcp_client_console

# Check specific files
uv run ruff check mcp_client_console/core/client.py

# Show what would be fixed without making changes
uv run ruff check --diff mcp_client_console
```

To extend this client:

1. **Add new connection types**: Implement new classes in `mcp_client_console/connections/` inheriting from `MCPConnection`
2. **Modify the UI**: Update `mcp_client_console/ui/streamlit_app.py` for UI changes
3. **Extend business logic**: Add features to `mcp_client_console/core/client.py`
4. **Add new UI frameworks**: Create new modules in `mcp_client_console/ui/` (e.g., `flask_app.py`, `fastapi_app.py`)

### Development Commands (uv):

```bash
# Setup development environment
./setup_dev.sh
# OR
make install-dev

# Run the application
make run

# Run tests
make test

# Code formatting and linting (using Ruff)
make format  # Format code and fix auto-fixable issues
make lint    # Check for linting issues

# Type checking
make type-check

# Run all quality checks
make check

# Build package
make build
```

### Architecture Benefits:
- **Modular Design**: Each component can be developed and tested independently
- **Easy UI Replacement**: Swap Streamlit for other frameworks without touching business logic
- **Extensible Connections**: Add new MCP transports by implementing the `MCPConnection` interface
- **Centralized Error Handling**: Consistent error management across all components
- **Modern Tooling**: Uses `uv` for fast dependency management and `pyproject.toml` for configuration
- **Fast Code Quality**: Uses `ruff` for lightning-fast linting and formatting (replaces flake8, black, and isort)

## Troubleshooting

- **Connection Issues**: Verify your MCP server is running and accessible
- **Import Errors**: Ensure all dependencies are installed in the virtual environment
- **Port Conflicts**: Change the Streamlit port in `run_app.sh` if 8501 is in use

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

Copyright 2025 dmartinol
