"""
Data models for MCP Client Console.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class ServerInfo:
    """
    Information about an MCP server.
    """
    name: Optional[str] = None
    version: Optional[str] = None
    protocol_version: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class ToolInfo:
    """
    Information about an MCP tool.
    """
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    raw_data: Optional[Any] = None

@dataclass
class PromptInfo:
    """
    Information about an MCP prompt.
    """
    name: str
    description: str
    arguments: Optional[Dict[str, Any]] = None
    raw_data: Optional[Any] = None

@dataclass
class ResourceInfo:
    """
    Information about an MCP resource.
    """
    uri: str
    name: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None
    raw_data: Optional[Any] = None

@dataclass
class ConnectionConfig:
    """
    Configuration for MCP connection.
    """
    connection_type: str
    parameters: Dict[str, Any]
    
    def __post_init__(self):
        self.connection_type = self.connection_type.lower()

@dataclass
class ToolExecutionResult:
    """
    Result of tool execution.
    """
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    raw_result: Optional[Any] = None
