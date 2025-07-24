import pytest
from unittest.mock import Mock, patch

from mcp_client_console.core.client import MCPClientService
from mcp_client_console.core.exceptions import ToolExecutionError


def test_initialization():
    service = MCPClientService()
    assert service is not None


def test_connection_handling():
    with patch("mcp_client_console.connections.base.MCPConnection") as mock_connection_class:
        mock_connection = Mock()
        mock_connection.connect.return_value = {}
        mock_connection_class.return_value = mock_connection
        
        service = MCPClientService()
        service.connection = mock_connection
        assert service.is_connected() is False


def test_execution_error_handling():
    service = MCPClientService()
    # The service should not be connected initially
    assert service.is_connected() is False
