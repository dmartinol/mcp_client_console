"""
Service layer for MCP client operations.
"""

import time
from typing import Any, Dict, List, Optional

from ..connections.base import MCPConnection
from ..connections.factory import ConnectionFactory
from ..utils.error_handler import handle_errors
from ..utils.logger import get_logger
from .exceptions import ConnectionError, MCPClientError, ToolExecutionError
from .models import (
    ConnectionConfig,
    PromptInfo,
    ResourceInfo,
    ServerInfo,
    ToolExecutionResult,
    ToolInfo,
)

logger = get_logger(__name__)


class MCPClientService:
    """
    Service layer for MCP client operations.
    Handles connection management, tool execution, and data transformation.
    """

    def __init__(self):
        self.connection: Optional[MCPConnection] = None
        self.connection_config: Optional[ConnectionConfig] = None
        self.server_info: Optional[ServerInfo] = None
        self.tools: List[ToolInfo] = []
        self.prompts: List[PromptInfo] = []
        self.resources: List[ResourceInfo] = []
        self._connected = False

        logger.info("MCP Client Service initialized")

    @handle_errors("connection")
    async def connect(self, connection_config: ConnectionConfig) -> ServerInfo:
        """
        Connect to an MCP server and initialize session.

        Args:
            connection_config: Configuration for the connection

        Returns:
            Server information

        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(
                f"Connecting to MCP server via {connection_config.connection_type}"
            )

            # Create connection using factory
            self.connection = ConnectionFactory.create_connection(
                connection_config.connection_type, **connection_config.parameters
            )

            # Test connection and get server info
            server_data = await self.connection.connect()

            # Transform raw data to models
            self.server_info = self._parse_server_info(server_data)
            self.tools = self._parse_tools(server_data.get("tools", []))
            self.prompts = self._parse_prompts(server_data.get("prompts", []))
            self.resources = self._parse_resources(server_data.get("resources", []))

            self.connection_config = connection_config
            self._connected = True

            logger.info(
                f"Successfully connected to MCP server. Found {len(self.tools)} "
                f"tools, {len(self.prompts)} prompts, {len(self.resources)} "
                f"resources"
            )

            return self.server_info

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            await self._cleanup_connection()

            if isinstance(e, MCPClientError):
                raise
            else:
                raise ConnectionError(
                    f"Connection failed: {e!s}",
                    connection_type=connection_config.connection_type,
                    connection_params=connection_config.parameters,
                ) from e

    @handle_errors("disconnection")
    async def disconnect(self):
        """
        Disconnect from the MCP server and cleanup resources.
        """
        logger.info("Disconnecting from MCP server")
        await self._cleanup_connection()

    @handle_errors("tool_execution")
    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ToolExecutionResult:
        """
        Execute a tool with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If tool execution fails
        """
        if not self.is_connected():
            raise ToolExecutionError(
                "Not connected to MCP server", tool_name=tool_name, arguments=arguments
            )

        # Find tool info
        tool_info = self.get_tool(tool_name)
        if not tool_info:
            raise ToolExecutionError(
                f"Tool '{tool_name}' not found",
                tool_name=tool_name,
                arguments=arguments,
            )

        try:
            logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
            start_time = time.time()

            # Execute tool through connection
            if self.connection is None:
                raise ToolExecutionError(
                    "Not connected to MCP server",
                    tool_name=tool_name,
                    arguments=arguments,
                )
            result = await self.connection.call_tool(tool_name, arguments)

            execution_time = time.time() - start_time

            logger.info(
                f"Tool '{tool_name}' executed successfully in {execution_time:.2f}s"
            )

            return ToolExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time,
                raw_result=result,
            )

        except Exception as e:
            execution_time = (
                time.time() - start_time if "start_time" in locals() else 0.0
            )

            logger.error(f"Tool execution failed for '{tool_name}': {e}")

            if isinstance(e, ToolExecutionError):
                raise
            else:
                raise ToolExecutionError(
                    f"Tool execution failed: {e!s}",
                    tool_name=tool_name,
                    arguments=arguments,
                    execution_context={"execution_time": execution_time},
                ) from e

    def is_connected(self) -> bool:
        """
        Check if connected to an MCP server.

        Returns:
            True if connected, False otherwise
        """
        return self._connected and self.connection is not None

    def get_server_info(self) -> Optional[ServerInfo]:
        """
        Get server information.

        Returns:
            Server information or None if not connected
        """
        return self.server_info

    def get_tools(self) -> List[ToolInfo]:
        """
        Get list of available tools.

        Returns:
            List of tool information
        """
        return self.tools.copy()

    def get_tool(self, tool_name: str) -> Optional[ToolInfo]:
        """
        Get information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool information or None if not found
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def get_prompts(self) -> List[PromptInfo]:
        """
        Get list of available prompts.

        Returns:
            List of prompt information
        """
        return self.prompts.copy()

    def get_resources(self) -> List[ResourceInfo]:
        """
        Get list of available resources.

        Returns:
            List of resource information
        """
        return self.resources.copy()

    async def _cleanup_connection(self):
        """
        Clean up connection resources.
        """
        if self.connection:
            try:
                await self.connection.disconnect()
            except Exception as e:
                logger.warning(f"Error during connection cleanup: {e}")

        self.connection = None
        self.connection_config = None
        self.server_info = None
        self.tools = []
        self.prompts = []
        self.resources = []
        self._connected = False

        logger.debug("Connection cleanup completed")

    def _parse_server_info(self, server_data: Dict[str, Any]) -> ServerInfo:
        """
        Parse raw server data into ServerInfo model.

        Args:
            server_data: Raw server data

        Returns:
            ServerInfo instance
        """
        return ServerInfo(
            name=server_data.get("name"),
            version=server_data.get("version"),
            protocol_version=server_data.get("protocolVersion"),
            capabilities=server_data.get("capabilities"),
            raw_data=server_data,
        )

    def _parse_tools(self, tools_data: List[Any]) -> List[ToolInfo]:
        """
        Parse raw tools data into ToolInfo models.

        Args:
            tools_data: Raw tools data

        Returns:
            List of ToolInfo instances
        """
        tools = []
        for tool_data in tools_data:
            try:
                tool = ToolInfo(
                    name=getattr(tool_data, "name", str(tool_data)),
                    description=getattr(tool_data, "description", ""),
                    input_schema=getattr(tool_data, "inputSchema", None),
                    raw_data=tool_data,
                )
                tools.append(tool)
            except Exception as e:
                logger.warning(f"Failed to parse tool data: {e}")

        return tools

    def _parse_prompts(self, prompts_data: List[Any]) -> List[PromptInfo]:
        """
        Parse raw prompts data into PromptInfo models.

        Args:
            prompts_data: Raw prompts data

        Returns:
            List of PromptInfo instances
        """
        prompts = []
        for prompt_data in prompts_data:
            try:
                prompt = PromptInfo(
                    name=getattr(prompt_data, "name", str(prompt_data)),
                    description=getattr(prompt_data, "description", ""),
                    arguments=getattr(prompt_data, "arguments", None),
                    raw_data=prompt_data,
                )
                prompts.append(prompt)
            except Exception as e:
                logger.warning(f"Failed to parse prompt data: {e}")

        return prompts

    def _parse_resources(self, resources_data: List[Any]) -> List[ResourceInfo]:
        """
        Parse raw resources data into ResourceInfo models.

        Args:
            resources_data: Raw resources data

        Returns:
            List of ResourceInfo instances
        """
        resources = []
        for resource_data in resources_data:
            try:
                resource = ResourceInfo(
                    uri=getattr(resource_data, "uri", str(resource_data)),
                    name=getattr(resource_data, "name", None),
                    description=getattr(resource_data, "description", None),
                    mime_type=getattr(resource_data, "mimeType", None),
                    raw_data=resource_data,
                )
                resources.append(resource)
            except Exception as e:
                logger.warning(f"Failed to parse resource data: {e}")

        return resources
