"""
Connection factory for creating appropriate connection instances.
"""

from typing import Any, Dict, List

from ..core.exceptions import MCPClientError
from ..utils.logger import get_logger
from .base import MCPConnection
from .http_connection import HTTPConnection
from .sse_connection import SSEConnection
from .stdio_connection import StdioConnection

logger = get_logger(__name__)


class ConnectionFactory:
    """
    Factory class for creating MCP connections based on configuration.
    """

    @staticmethod
    def create_connection(connection_type: str, **kwargs) -> MCPConnection:
        """
        Create a connection instance based on the connection type.

        Args:
            connection_type: Type of connection ('stdio', 'sse', 'http')
            **kwargs: Connection-specific parameters

        Returns:
            MCPConnection instance

        Raises:
            MCPClientError: If connection type is unsupported or parameters are invalid
        """
        connection_type = connection_type.lower()

        try:
            if connection_type == "stdio":
                command = kwargs.get("command")
                args = kwargs.get("args", [])

                if not command:
                    raise MCPClientError(
                        "STDIO connection requires 'command' parameter"
                    )

                logger.info(f"Creating STDIO connection: {command} {' '.join(args)}")
                return StdioConnection(command=command, args=args)

            elif connection_type == "sse":
                url = kwargs.get("url")

                if not url:
                    raise MCPClientError("SSE connection requires 'url' parameter")

                logger.info(f"Creating SSE connection: {url}")
                return SSEConnection(url=url)

            elif connection_type == "http":
                base_url = kwargs.get("base_url")

                if not base_url:
                    raise MCPClientError(
                        "HTTP connection requires 'base_url' parameter"
                    )

                logger.info(f"Creating HTTP connection: {base_url}")
                return HTTPConnection(base_url=base_url)

            else:
                raise MCPClientError(f"Unsupported connection type: {connection_type}")

        except Exception as e:
            logger.error(f"Failed to create {connection_type} connection: {e}")
            raise

    @staticmethod
    def get_supported_types() -> List[str]:
        """
        Get list of supported connection types.

        Returns:
            List of supported connection type strings
        """
        return ["stdio", "sse", "http"]

    @staticmethod
    def get_connection_parameters(connection_type: str) -> Dict[str, Any]:
        """
        Get required parameters for a specific connection type.

        Args:
            connection_type: Type of connection

        Returns:
            Dictionary describing required parameters
        """
        connection_type = connection_type.lower()

        parameters = {
            "stdio": {
                "required": ["command"],
                "optional": ["args"],
                "description": "Execute MCP server as a subprocess",
            },
            "sse": {
                "required": ["url"],
                "optional": [],
                "description": "Connect to MCP server via Server-Sent Events",
            },
            "http": {
                "required": ["base_url"],
                "optional": [],
                "description": "Connect to MCP server via HTTP API",
            },
        }

        return parameters.get(connection_type, {})
