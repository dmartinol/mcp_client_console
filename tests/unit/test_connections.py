import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import subprocess
import json
from typing import Dict, Any

from mcp_client_console.connections.stdio_connection import StdioConnection
from mcp_client_console.connections.sse_connection import SSEConnection
from mcp_client_console.connections.http_connection import HTTPConnection
from mcp_client_console.core.exceptions import ConnectionError, ToolExecutionError


class TestStdioConnection:
    """Test cases for StdioConnection class"""

    def test_init_with_valid_params(self):
        """Test initialization with valid parameters"""
        connection = StdioConnection(command="python", args=["-m", "server"])
        assert connection.command == "python"
        assert connection.args == ["-m", "server"]

    def test_init_with_minimal_params(self):
        """Test initialization with minimal parameters"""
        connection = StdioConnection(command="echo")
        assert connection.command == "echo"
        assert connection.args == []

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection establishment"""
        with patch('mcp_client_console.connections.stdio_connection.stdio_client') as mock_stdio_client:
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_session = AsyncMock()
            
            # Mock the context managers
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_session.initialize.return_value = Mock(dict=lambda: {"name": "test_server"})
            mock_session.list_tools.return_value = Mock(tools=[])
            mock_session.list_prompts.return_value = Mock(prompts=[])
            mock_session.list_resources.return_value = Mock(resources=[])
            
            with patch('mcp_client_console.connections.stdio_connection.MCPClientSession') as mock_session_class:
                mock_session_class.return_value.__aenter__.return_value = mock_session
                
                connection = StdioConnection(command="python", args=["-m", "server"])
                result = await connection.connect()
                
                assert result == {"name": "test_server", "tools": [], "prompts": [], "resources": []}

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure"""
        with patch('mcp_client_console.connections.stdio_connection.stdio_client') as mock_stdio_client:
            mock_stdio_client.side_effect = Exception("Connection failed")
            
            connection = StdioConnection(command="nonexistent", args=[])
            
            with pytest.raises(ConnectionError) as exc_info:
                await connection.connect()
            
            assert "Failed to connect via STDIO" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool execution"""
        with patch('mcp_client_console.connections.stdio_connection.stdio_client') as mock_stdio_client:
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_session = AsyncMock()
            
            # Mock the context managers
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_session.call_tool.return_value = {"result": "success"}
            
            with patch('mcp_client_console.connections.stdio_connection.MCPClientSession') as mock_session_class:
                mock_session_class.return_value.__aenter__.return_value = mock_session
                
                connection = StdioConnection(command="python", args=["-m", "server"])
                result = await connection.call_tool("test_tool", {"param": "value"})
                
                assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_call_tool_failure(self):
        """Test tool execution failure"""
        with patch('mcp_client_console.connections.stdio_connection.stdio_client') as mock_stdio_client:
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_session = AsyncMock()
            
            # Mock the context managers
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_session.call_tool.side_effect = Exception("Tool failed")
            
            with patch('mcp_client_console.connections.stdio_connection.MCPClientSession') as mock_session_class:
                mock_session_class.return_value.__aenter__.return_value = mock_session
                
                connection = StdioConnection(command="python", args=["-m", "server"])
                
                with pytest.raises(ToolExecutionError) as exc_info:
                    await connection.call_tool("test_tool", {"param": "value"})
                
                assert "Failed to execute tool" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection"""
        connection = StdioConnection(command="echo")
        # Should not raise an error
        await connection.disconnect()


class TestSSEConnection:
    """Test cases for SSEConnection class"""

    def test_init_with_valid_url(self):
        """Test initialization with valid URL"""
        connection = SSEConnection(url="http://localhost:8080/events")
        assert connection.url == "http://localhost:8080/events"

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful SSE connection"""
        with patch('mcp_client_console.connections.sse_connection.sse_client') as mock_sse_client:
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_session = AsyncMock()
            
            # Mock the context managers
            mock_sse_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_session.initialize.return_value = Mock(dict=lambda: {"name": "test_server"})
            mock_session.list_tools.return_value = Mock(tools=[])
            mock_session.list_prompts.return_value = Mock(prompts=[])
            mock_session.list_resources.return_value = Mock(resources=[])
            
            with patch('mcp_client_console.connections.sse_connection.MCPClientSession') as mock_session_class:
                mock_session_class.return_value.__aenter__.return_value = mock_session
                
                connection = SSEConnection(url="http://localhost:8080/events")
                result = await connection.connect()
                
                assert result == {"name": "test_server", "tools": [], "prompts": [], "resources": []}

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure"""
        with patch('mcp_client_console.connections.sse_connection.sse_client') as mock_sse_client:
            mock_sse_client.side_effect = Exception("Connection failed")
            
            connection = SSEConnection(url="http://localhost:8080/events")
            
            with pytest.raises(ConnectionError) as exc_info:
                await connection.connect()
            
            assert "Failed to connect via SSE" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool execution"""
        with patch('mcp_client_console.connections.sse_connection.sse_client') as mock_sse_client:
            mock_read = AsyncMock()
            mock_write = AsyncMock()
            mock_session = AsyncMock()
            
            # Mock the context managers
            mock_sse_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_session.call_tool.return_value = {"result": "success"}
            
            with patch('mcp_client_console.connections.sse_connection.MCPClientSession') as mock_session_class:
                mock_session_class.return_value.__aenter__.return_value = mock_session
                
                connection = SSEConnection(url="http://localhost:8080/events")
                result = await connection.call_tool("test_tool", {"param": "value"})
                
                assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection"""
        connection = SSEConnection(url="http://localhost:8080/events")
        # Should not raise an error
        await connection.disconnect()


class TestHTTPConnection:
    """Test cases for HTTPConnection class"""

    def test_init_with_valid_url(self):
        """Test initialization with valid URL"""
        connection = HTTPConnection(base_url="http://localhost:8080/mcp")
        assert connection.base_url == "http://localhost:8080/mcp"

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful HTTP connection"""
        with patch('mcp_client_console.connections.http_connection.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"name": "test_server"}
            mock_get.return_value = mock_response
            
            connection = HTTPConnection(base_url="http://localhost:8080/mcp")
            result = await connection.connect()
            
            assert result == {"name": "test_server"}
            mock_get.assert_called_once_with("http://localhost:8080/mcp/mcp/info", timeout=10)

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure"""
        with patch('mcp_client_console.connections.http_connection.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            connection = HTTPConnection(base_url="http://localhost:8080/mcp")
            
            with pytest.raises(Exception) as exc_info:
                await connection.connect()
            
            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool execution"""
        with patch('mcp_client_console.connections.http_connection.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "success"}
            mock_post.return_value = mock_response
            
            connection = HTTPConnection(base_url="http://localhost:8080/mcp")
            result = await connection.call_tool("test_tool", {"param": "value"})
            
            assert result == {"result": "success"}
            mock_post.assert_called_once_with(
                "http://localhost:8080/mcp/mcp/tools/execute",
                json={"tool_name": "test_tool", "arguments": {"param": "value"}},
                timeout=30
            )

    @pytest.mark.asyncio
    async def test_call_tool_failure(self):
        """Test tool execution failure"""
        with patch('mcp_client_console.connections.http_connection.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            connection = HTTPConnection(base_url="http://localhost:8080/mcp")
            
            with pytest.raises(ToolExecutionError) as exc_info:
                await connection.call_tool("test_tool", {"param": "value"})
            
            assert "Tool execution failed with status 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection"""
        connection = HTTPConnection(base_url="http://localhost:8080/mcp")
        # Should not raise an error
        await connection.disconnect()


class TestConnectionIntegration:
    """Integration tests for connection factory"""

    def test_factory_creates_stdio_connection(self):
        """Test that factory creates correct STDIO connection type"""
        from mcp_client_console.connections.factory import ConnectionFactory
        
        connection = ConnectionFactory.create_connection("stdio", command="python", args=["-m", "server"])
        assert isinstance(connection, StdioConnection)
        assert connection.command == "python"
        assert connection.args == ["-m", "server"]

    def test_factory_creates_sse_connection(self):
        """Test that factory creates correct SSE connection type"""
        from mcp_client_console.connections.factory import ConnectionFactory
        
        connection = ConnectionFactory.create_connection("sse", url="http://localhost:8080/events")
        assert isinstance(connection, SSEConnection)
        assert connection.url == "http://localhost:8080/events"

    def test_factory_creates_http_connection(self):
        """Test that factory creates correct HTTP connection type"""
        from mcp_client_console.connections.factory import ConnectionFactory
        
        connection = ConnectionFactory.create_connection("http", base_url="http://localhost:8080")
        assert isinstance(connection, HTTPConnection)
        assert connection.base_url == "http://localhost:8080"
