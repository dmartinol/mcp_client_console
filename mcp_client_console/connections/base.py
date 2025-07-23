"""
Base connection interface for MCP.
"""

from abc import ABC, abstractmethod
from typing import Any


class MCPConnection(ABC):
    """
    Abstract base class for MCP connections.
    """

    @abstractmethod
    async def connect(self) -> Any:
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: dict):
        pass
