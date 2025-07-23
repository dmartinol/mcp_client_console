import pytest

from mcp_client_console.core.client import MCPClientService
from mcp_client_console.core.exceptions import ToolExecutionError


def test_initialization():
    service = MCPClientService()
    assert service is not None


def test_connection_handling(mocker):
    mock_connection = mocker.patch("mcp_client_console.connections.base.MCPConnection")
    mock_connection.connect.return_value = True
    service = MCPClientService()
    service.connection = mock_connection
    assert service.is_connected() is False


def test_execution_error_handling():
    service = MCPClientService()
    # The service should not be connected initially
    assert service.is_connected() is False
