"""
Custom exceptions for MCP Client Console.
"""

from typing import Dict, Any, Optional
import traceback

class MCPClientError(Exception):
    """
    Base exception for MCP Client errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.traceback_info = traceback.format_exc()

class ConnectionError(MCPClientError):
    """
    Exception raised when connection to MCP server fails.
    """
    
    def __init__(self, message: str, connection_type: Optional[str] = None, 
                 connection_params: Optional[Dict[str, Any]] = None):
        details = {
            "connection_type": connection_type,
            "connection_params": connection_params
        }
        super().__init__(message, details)
        self.connection_type = connection_type
        self.connection_params = connection_params

class ToolExecutionError(MCPClientError):
    """
    Exception raised when tool execution fails.
    """
    
    def __init__(self, message: str, tool_name: Optional[str] = None, 
                 arguments: Optional[Dict[str, Any]] = None, 
                 execution_context: Optional[Dict[str, Any]] = None):
        details = {
            "tool_name": tool_name,
            "arguments": arguments,
            "execution_context": execution_context
        }
        super().__init__(message, details)
        self.tool_name = tool_name
        self.arguments = arguments
        self.execution_context = execution_context

class ValidationError(MCPClientError):
    """
    Exception raised when input validation fails.
    """
    
    def __init__(self, message: str, field_name: Optional[str] = None, 
                 field_value: Optional[Any] = None, 
                 validation_rules: Optional[Dict[str, Any]] = None):
        details = {
            "field_name": field_name,
            "field_value": field_value,
            "validation_rules": validation_rules
        }
        super().__init__(message, details)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rules = validation_rules

class ConfigurationError(MCPClientError):
    """
    Exception raised when configuration is invalid.
    """
    pass
