import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import subprocess
import json
from typing import Dict, Any

from mcp_client_console.connections.stdio_connection import StdioConnection
from mcp_client_console.connections.sse_connection import SSEConnection
from mcp_client_console.connections.http_connection import HTTPConnection
from mcp_client_console.core.exceptions import ConnectionError


class TestStdioConnection:
    """Test cases for StdioConnection class"""

    def test_init_with_valid_params(self):
        """Test initialization with valid parameters"""
        connection = StdioConnection(command="python", args=["-m", "server"])
        assert connection.command == "python"
        assert connection.args == ["-m", "server"]
        assert connection.process is None
        assert connection.is_connected is False

    def test_init_with_minimal_params(self):
        """Test initialization with minimal parameters"""
        connection = StdioConnection(command="echo")
        assert connection.command == "echo"
        assert connection.args == []
        assert connection.process is None

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection establishment"""
        with patch('asyncio.create_subprocess_exec') as mock_create_subprocess:
            mock_process = Mock()
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_process.returncode = None
            mock_create_subprocess.return_value = mock_process

            connection = StdioConnection(command="python", args=["-m", "server"])
            await connection.connect()

            assert connection.process == mock_process
            assert connection.is_connected is True
            mock_create_subprocess.assert_called_once_with(
                "python", "-m", "server",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

    @pytest.mark.asyncio
    async def test_connect_subprocess_error(self):
        """Test connection failure due to subprocess error"""
        with patch('asyncio.create_subprocess_exec') as mock_create_subprocess:
            mock_create_subprocess.side_effect = OSError("Command not found")

            connection = StdioConnection(command="nonexistent", args=[])
            
            with pytest.raises(ConnectionError) as exc_info:
                await connection.connect()
            
            assert "Failed to start subprocess" in str(exc_info.value)
            assert connection.is_connected is False

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending"""
        mock_process = Mock()
        mock_stdin = AsyncMock()
        mock_process.stdin = mock_stdin

        connection = StdioConnection(command="echo")
        connection.process = mock_process
        connection.is_connected = True

        message = {"method": "test", "params": {}}
        await connection.send_message(message)

        expected_data = json.dumps(message).encode() + b'\n'
        mock_stdin.write.assert_called_once_with(expected_data)
        mock_stdin.drain.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_not_connected(self):
        """Test sending message when not connected"""
        connection = StdioConnection(command="echo")
        
        with pytest.raises(ConnectionError) as exc_info:
            await connection.send_message({"method": "test"})
        
        assert "Not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_message_write_error(self):
        """Test error handling during message sending"""
        mock_process = Mock()
        mock_stdin = AsyncMock()
        mock_stdin.write.side_effect = BrokenPipeError("Pipe broken")
        mock_process.stdin = mock_stdin

        connection = StdioConnection(command="echo")
        connection.process = mock_process
        connection.is_connected = True

        with pytest.raises(ConnectionError) as exc_info:
            await connection.send_message({"method": "test"})
        
        assert "Failed to send message" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_receive_message_success(self):
        """Test successful message receiving"""
        mock_process = Mock()
        mock_stdout = AsyncMock()
        test_message = {"result": "success"}
        mock_stdout.readline.return_value = (json.dumps(test_message) + '\n').encode()
        mock_process.stdout = mock_stdout

        connection = StdioConnection(command="echo")
        connection.process = mock_process
        connection.is_connected = True

        result = await connection.receive_message()
        assert result == test_message

    @pytest.mark.asyncio
    async def test_receive_message_invalid_json(self):
        """Test receiving invalid JSON message"""
        mock_process = Mock()
        mock_stdout = AsyncMock()
        mock_stdout.readline.return_value = b'invalid json\n'
        mock_process.stdout = mock_stdout

        connection = StdioConnection(command="echo")
        connection.process = mock_process
        connection.is_connected = True

        with pytest.raises(ConnectionError) as exc_info:
            await connection.receive_message()
        
        assert "Failed to parse JSON message" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_receive_message_not_connected(self):
        """Test receiving message when not connected"""
        connection = StdioConnection(command="echo")
        
        with pytest.raises(ConnectionError) as exc_info:
            await connection.receive_message()
        
        assert "Not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection"""
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock(return_value=0)
        mock_stdin = Mock()
        mock_stdin.close = Mock()
        mock_process.stdin = mock_stdin

        connection = StdioConnection(command="echo")
        connection.process = mock_process
        connection.is_connected = True

        await connection.disconnect()

        mock_stdin.close.assert_called_once()
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        assert connection.is_connected is False
        assert connection.process is None

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        """Test disconnection when not connected"""
        connection = StdioConnection(command="echo")
        # Should not raise an error
        await connection.disconnect()
        assert connection.is_connected is False


class TestSSEConnection:
    """Test cases for SSEConnection class"""

    def test_init_with_valid_url(self):
        """Test initialization with valid URL"""
        connection = SSEConnection(url="http://localhost:8080/events")
        assert connection.url == "http://localhost:8080/events"
        assert connection.session is None
        assert connection.is_connected is False

    def test_init_with_headers(self):
        """Test initialization with custom headers"""
        headers = {"Authorization": "Bearer token"}
        connection = SSEConnection(url="http://localhost:8080", headers=headers)
        assert connection.headers == headers

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful SSE connection"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.get.return_value.__aenter__.return_value = mock_response

            connection = SSEConnection(url="http://localhost:8080/events")
            await connection.connect()

            assert connection.session == mock_session
            assert connection.is_connected is True
            mock_session.get.assert_called_once_with(
                "http://localhost:8080/events",
                headers={}
            )

    @pytest.mark.asyncio
    async def test_connect_http_error(self):
        """Test connection failure due to HTTP error"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_session.get.return_value.__aenter__.return_value = mock_response

            connection = SSEConnection(url="http://localhost:8080/events")
            
            with pytest.raises(ConnectionError) as exc_info:
                await connection.connect()
            
            assert "HTTP error" in str(exc_info.value)
            assert connection.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_network_error(self):
        """Test connection failure due to network error"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            import aiohttp
            mock_session.get.side_effect = aiohttp.ClientError("Network error")

            connection = SSEConnection(url="http://localhost:8080/events")
            
            with pytest.raises(ConnectionError) as exc_info:
                await connection.connect()
            
            assert "Failed to connect to SSE endpoint" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_message_not_supported(self):
        """Test that send_message is not supported for SSE"""
        connection = SSEConnection(url="http://localhost:8080")
        connection.is_connected = True
        
        with pytest.raises(ConnectionError) as exc_info:
            await connection.send_message({"method": "test"})
        
        assert "SSE connections do not support sending messages" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_receive_message_success(self):
        """Test successful message receiving from SSE"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        
        # Mock SSE event data
        mock_event_data = json.dumps({"event": "message", "data": "test"})
        mock_response.content.readline = AsyncMock(side_effect=[
            b'data: ' + mock_event_data.encode() + b'\n',
            b'\n',  # End of event
            b''  # EOF
        ])
        
        connection = SSEConnection(url="http://localhost:8080")
        connection.session = mock_session
        connection.response = mock_response
        connection.is_connected = True

        result = await connection.receive_message()
        assert result == {"event": "message", "data": "test"}

    @pytest.mark.asyncio
    async def test_receive_message_not_connected(self):
        """Test receiving message when not connected"""
        connection = SSEConnection(url="http://localhost:8080")
        
        with pytest.raises(ConnectionError) as exc_info:
            await connection.receive_message()
        
        assert "Not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        
        connection = SSEConnection(url="http://localhost:8080")
        connection.session = mock_session
        connection.response = mock_response
        connection.is_connected = True

        await connection.disconnect()

        mock_response.close.assert_called_once()
        mock_session.close.assert_called_once()
        assert connection.is_connected is False
        assert connection.session is None
        assert connection.response is None

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        """Test disconnection when not connected"""
        connection = SSEConnection(url="http://localhost:8080")
        # Should not raise an error
        await connection.disconnect()
        assert connection.is_connected is False


class TestHTTPConnection:
    """Test cases for HTTPConnection class"""

    def test_init_with_valid_url(self):
        """Test initialization with valid URL"""
        connection = HTTPConnection(url="http://localhost:8080/mcp")
        assert connection.url == "http://localhost:8080/mcp"
        assert connection.session is None
        assert connection.is_connected is False

    def test_init_with_headers(self):
        """Test initialization with custom headers"""
        headers = {"Content-Type": "application/json"}
        connection = HTTPConnection(url="http://localhost:8080", headers=headers)
        assert connection.headers == headers

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful HTTP connection"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            connection = HTTPConnection(url="http://localhost:8080/mcp")
            await connection.connect()

            assert connection.session == mock_session
            assert connection.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_already_connected(self):
        """Test connecting when already connected"""
        mock_session = AsyncMock()
        
        connection = HTTPConnection(url="http://localhost:8080")
        connection.session = mock_session
        connection.is_connected = True

        # Should not create a new session
        await connection.connect()
        assert connection.session == mock_session

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending via HTTP POST"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"result": "success"}
            mock_session.post.return_value.__aenter__.return_value = mock_response

            connection = HTTPConnection(url="http://localhost:8080/mcp")
            connection.session = mock_session
            connection.is_connected = True

            message = {"method": "test", "params": {}}
            result = await connection.send_message(message)

            assert result == {"result": "success"}
            mock_session.post.assert_called_once_with(
                "http://localhost:8080/mcp",
                json=message,
                headers={}
            )

    @pytest.mark.asyncio
    async def test_send_message_not_connected(self):
        """Test sending message when not connected"""
        connection = HTTPConnection(url="http://localhost:8080")
        
        with pytest.raises(ConnectionError) as exc_info:
            await connection.send_message({"method": "test"})
        
        assert "Not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_message_http_error(self):
        """Test error handling during HTTP message sending"""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_session.post.return_value.__aenter__.return_value = mock_response

        connection = HTTPConnection(url="http://localhost:8080")
        connection.session = mock_session
        connection.is_connected = True

        with pytest.raises(ConnectionError) as exc_info:
            await connection.send_message({"method": "test"})
        
        assert "HTTP error 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_message_network_error(self):
        """Test network error during HTTP message sending"""
        mock_session = AsyncMock()
        import aiohttp
        mock_session.post.side_effect = aiohttp.ClientError("Network error")

        connection = HTTPConnection(url="http://localhost:8080")
        connection.session = mock_session
        connection.is_connected = True

        with pytest.raises(ConnectionError) as exc_info:
            await connection.send_message({"method": "test"})
        
        assert "Failed to send HTTP message" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_receive_message_not_supported(self):
        """Test that receive_message is not supported for HTTP"""
        connection = HTTPConnection(url="http://localhost:8080")
        connection.is_connected = True
        
        with pytest.raises(ConnectionError) as exc_info:
            await connection.receive_message()
        
        assert "HTTP connections do not support receiving messages" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection"""
        mock_session = AsyncMock()
        
        connection = HTTPConnection(url="http://localhost:8080")
        connection.session = mock_session
        connection.is_connected = True

        await connection.disconnect()

        mock_session.close.assert_called_once()
        assert connection.is_connected is False
        assert connection.session is None

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        """Test disconnection when not connected"""
        connection = HTTPConnection(url="http://localhost:8080")
        # Should not raise an error
        await connection.disconnect()
        assert connection.is_connected is False


# Integration-style tests for connection factory with actual connection types
class TestConnectionIntegration:
    """Integration tests for connections with factory"""

    def test_factory_creates_stdio_connection(self):
        """Test that factory creates correct STDIO connection type"""
        from mcp_client_console.connections.factory import ConnectionFactory
        
        connection = ConnectionFactory.create_connection("stdio", command="echo", args=["test"])
        assert isinstance(connection, StdioConnection)
        assert connection.command == "echo"
        assert connection.args == ["test"]

    def test_factory_creates_sse_connection(self):
        """Test that factory creates correct SSE connection type"""
        from mcp_client_console.connections.factory import ConnectionFactory
        
        connection = ConnectionFactory.create_connection("sse", url="http://localhost:8080")
        assert isinstance(connection, SSEConnection)
        assert connection.url == "http://localhost:8080"

    def test_factory_creates_http_connection(self):
        """Test that factory creates correct HTTP connection type"""
        from mcp_client_console.connections.factory import ConnectionFactory
        
        connection = ConnectionFactory.create_connection("http", url="http://localhost:8080")
        assert isinstance(connection, HTTPConnection)
        assert connection.url == "http://localhost:8080"
