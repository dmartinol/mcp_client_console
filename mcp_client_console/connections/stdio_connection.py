"""
STDIO connection implementation for MCP.
"""

from typing import Any, Dict, List, Optional

from mcp import ClientSession as MCPClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

from ..core.exceptions import ConnectionError, ToolExecutionError
from ..utils.logger import get_logger
from .base import MCPConnection

logger = get_logger(__name__)


class StdioConnection(MCPConnection):
    """
    STDIO transport implementation for MCP connections.
    """

    def __init__(self, command: str, args: Optional[List[str]] = None):
        self.command = command
        self.args = args or []
        self.server_params = StdioServerParameters(command=command, args=self.args)
        logger.info(f"Initialized STDIO connection: {command} {' '.join(self.args)}")

    async def connect(self) -> Dict[str, Any]:
        """
        Test connection and initialize session to get server info.

        Returns:
            Server information dictionary

        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.debug("Attempting STDIO connection")
            async with stdio_client(self.server_params) as (read, write):
                async with MCPClientSession(read, write) as session:
                    # Initialize the session
                    result = await session.initialize()
                    server_info = result.dict() if result else {}

                    # Get tools, prompts, and resources
                    try:
                        tools_result = await session.list_tools()
                        server_info["tools"] = (
                            tools_result.tools if tools_result else []
                        )
                    except Exception as e:
                        logger.warning(f"Failed to list tools: {e}")
                        server_info["tools"] = []

                    try:
                        prompts_result = await session.list_prompts()
                        server_info["prompts"] = (
                            prompts_result.prompts if prompts_result else []
                        )
                    except Exception as e:
                        logger.warning(f"Failed to list prompts: {e}")
                        server_info["prompts"] = []

                    try:
                        resources_result = await session.list_resources()
                        server_info["resources"] = (
                            resources_result.resources if resources_result else []
                        )
                    except Exception as e:
                        logger.warning(f"Failed to list resources: {e}")
                        server_info["resources"] = []

                    logger.info("STDIO connection successful")
                    return server_info

        except Exception as e:
            logger.error(f"STDIO connection failed: {e}")
            raise ConnectionError(f"Failed to connect via STDIO: {e!s}") from e

    async def disconnect(self):
        """
        Disconnect from the MCP server.
        Note: STDIO connections are stateless and auto-cleanup.
        """
        logger.debug("STDIO connection disconnected (stateless)")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool by creating a fresh connection.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If tool execution fails
        """
        try:
            logger.debug(f"Executing tool '{tool_name}' with arguments: {arguments}")

            async with stdio_client(self.server_params) as (read, write):
                async with MCPClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()

                    # Execute the tool
                    result = await session.call_tool(tool_name, arguments)

                    logger.info(f"Tool '{tool_name}' executed successfully")
                    return result

        except Exception as e:
            logger.error(f"Tool execution failed for '{tool_name}': {e}")
            raise ToolExecutionError(
                f"Failed to execute tool '{tool_name}': {e!s}",
                tool_name=tool_name,
                arguments=arguments,
            ) from e
