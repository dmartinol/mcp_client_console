import pytest

from mcp_client_console.connections.factory import ConnectionFactory
from mcp_client_console.connections.sse_connection import SSEConnection
from mcp_client_console.connections.stdio_connection import StdioConnection
from mcp_client_console.core.exceptions import MCPClientError


class TestConnectionFactory:

    def test_create_stdio_connection(self):
        connection = ConnectionFactory.create_connection("stdio", command="echo", args=["hello"])
        assert isinstance(connection, StdioConnection)

    def test_create_sse_connection(self):
        connection = ConnectionFactory.create_connection("sse", url="http://localhost:8080")
        assert isinstance(connection, SSEConnection)

    def test_unsupported_transport_error(self):
        with pytest.raises(MCPClientError):
            ConnectionFactory.create_connection("unsupported")
