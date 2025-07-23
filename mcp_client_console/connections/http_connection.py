"""
HTTP connection implementation for MCP.
"""

from typing import Dict, Any
import requests

from .base import MCPConnection
from ..core.exceptions import ConnectionError, ToolExecutionError
from ..utils.logger import get_logger

logger = get_logger(__name__)

class HTTPConnection(MCPConnection):
    """
    HTTP transport implementation for MCP connections.
    Note: This is a basic implementation for testing purposes.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        logger.info(f"Initialized HTTP connection: {base_url}")
    
    async def connect(self) -> Dict[str, Any]:
        """
        Test connection and get server info via HTTP.
        
        Returns:
            Server information dictionary
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.debug("Attempting HTTP connection")
            response = requests.get(f"{self.base_url}/mcp/info", timeout=10)
            
            if response.status_code == 200:
                server_info = response.json()
                logger.info("HTTP connection successful")
                return server_info
            else:
                raise ConnectionError(f"HTTP connection failed with status {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"HTTP connection failed: {e}")
            raise ConnectionError(f"Failed to connect via HTTP: {str(e)}") from e
    
    async def disconnect(self):
        """
        Disconnect from the MCP server.
        Note: HTTP connections are stateless.
        """
        logger.debug("HTTP connection disconnected (stateless)")
        pass
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool via HTTP.
        
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
            
            payload = {
                "tool_name": tool_name,
                "arguments": arguments
            }
            
            response = requests.post(
                f"{self.base_url}/mcp/tools/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Tool '{tool_name}' executed successfully")
                return result
            else:
                raise ToolExecutionError(
                    f"Tool execution failed with status {response.status_code}: {response.text}",
                    tool_name=tool_name,
                    arguments=arguments
                )
                
        except requests.RequestException as e:
            logger.error(f"Tool execution failed for '{tool_name}': {e}")
            raise ToolExecutionError(
                f"Failed to execute tool '{tool_name}': {str(e)}", 
                tool_name=tool_name,
                arguments=arguments
            ) from e
