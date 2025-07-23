"""
MCP Client Console - A testing tool for MCP (Model Context Protocol) server compliance.
"""

__version__ = "1.0.0"
__author__ = "Daniele Martinoli (dmartino)"
__description__ = "A Python UI to test MCP servers for protocol compliance"

from .core.client import MCPClientService
from .core.exceptions import MCPClientError, ConnectionError, ToolExecutionError

__all__ = [
    "MCPClientService",
    "MCPClientError", 
    "ConnectionError",
    "ToolExecutionError"
]
