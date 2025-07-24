import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from mcp_client_console.core.client import MCPClientService
from mcp_client_console.core.exceptions import (
    ToolExecutionError,
    ConnectionError,
    MCPClientError,
)
from mcp_client_console.core.models import (
    ConnectionConfig,
    ServerInfo,
    ToolInfo,
    PromptInfo,
    ResourceInfo,
    ToolExecutionResult,
)


class TestMCPClientService:
    """Test cases for MCPClientService."""

    def test_initialization(self):
        """Test service initialization."""
        service = MCPClientService()
        assert service is not None
        assert service.connection is None
        assert service.connection_config is None
        assert service.server_info is None
        assert service.tools == []
        assert service.prompts == []
        assert service.resources == []
        assert service._connected is False

    def test_is_connected_when_not_connected(self):
        """Test is_connected when not connected."""
        service = MCPClientService()
        assert service.is_connected() is False

    def test_is_connected_when_connected(self):
        """Test is_connected when connected."""
        service = MCPClientService()
        service._connected = True
        service.connection = Mock()
        assert service.is_connected() is True

    def test_is_connected_when_connected_but_no_connection(self):
        """Test is_connected when marked as connected but no connection object."""
        service = MCPClientService()
        service._connected = True
        service.connection = None
        assert service.is_connected() is False

    def test_get_server_info_when_not_connected(self):
        """Test get_server_info when not connected."""
        service = MCPClientService()
        assert service.get_server_info() is None

    def test_get_server_info_when_connected(self):
        """Test get_server_info when connected."""
        service = MCPClientService()
        mock_server_info = Mock(spec=ServerInfo)
        service.server_info = mock_server_info
        assert service.get_server_info() == mock_server_info

    def test_get_tools_when_empty(self):
        """Test get_tools when no tools available."""
        service = MCPClientService()
        tools = service.get_tools()
        assert tools == []
        # Should return a copy, not the original list
        assert tools is not service.tools

    def test_get_tools_when_tools_available(self):
        """Test get_tools when tools are available."""
        service = MCPClientService()
        mock_tool = Mock(spec=ToolInfo)
        service.tools = [mock_tool]
        tools = service.get_tools()
        assert tools == [mock_tool]
        # Should return a copy, not the original list
        assert tools is not service.tools

    def test_get_tool_when_tool_exists(self):
        """Test get_tool when tool exists."""
        service = MCPClientService()
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]
        
        result = service.get_tool("test_tool")
        assert result == mock_tool

    def test_get_tool_when_tool_not_found(self):
        """Test get_tool when tool doesn't exist."""
        service = MCPClientService()
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "other_tool"
        service.tools = [mock_tool]
        
        result = service.get_tool("test_tool")
        assert result is None

    def test_get_prompts_when_empty(self):
        """Test get_prompts when no prompts available."""
        service = MCPClientService()
        prompts = service.get_prompts()
        assert prompts == []
        # Should return a copy, not the original list
        assert prompts is not service.prompts

    def test_get_prompts_when_prompts_available(self):
        """Test get_prompts when prompts are available."""
        service = MCPClientService()
        mock_prompt = Mock(spec=PromptInfo)
        service.prompts = [mock_prompt]
        prompts = service.get_prompts()
        assert prompts == [mock_prompt]
        # Should return a copy, not the original list
        assert prompts is not service.prompts

    def test_get_resources_when_empty(self):
        """Test get_resources when no resources available."""
        service = MCPClientService()
        resources = service.get_resources()
        assert resources == []
        # Should return a copy, not the original list
        assert resources is not service.resources

    def test_get_resources_when_resources_available(self):
        """Test get_resources when resources are available."""
        service = MCPClientService()
        mock_resource = Mock(spec=ResourceInfo)
        service.resources = [mock_resource]
        resources = service.get_resources()
        assert resources == [mock_resource]
        # Should return a copy, not the original list
        assert resources is not service.resources

    @pytest.mark.asyncio
    async def test_cleanup_connection_with_connection(self):
        """Test _cleanup_connection when connection exists."""
        service = MCPClientService()
        mock_connection = AsyncMock()
        service.connection = mock_connection
        service.connection_config = Mock()
        service.server_info = Mock()
        service.tools = [Mock()]
        service.prompts = [Mock()]
        service.resources = [Mock()]
        service._connected = True

        await service._cleanup_connection()

        mock_connection.disconnect.assert_called_once()
        assert service.connection is None
        assert service.connection_config is None
        assert service.server_info is None
        assert service.tools == []
        assert service.prompts == []
        assert service.resources == []
        assert service._connected is False

    @pytest.mark.asyncio
    async def test_cleanup_connection_without_connection(self):
        """Test _cleanup_connection when no connection exists."""
        service = MCPClientService()
        service.connection = None
        service._connected = True

        await service._cleanup_connection()

        assert service.connection is None
        assert service._connected is False

    @pytest.mark.asyncio
    async def test_cleanup_connection_with_disconnect_error(self):
        """Test _cleanup_connection when disconnect raises an exception."""
        service = MCPClientService()
        mock_connection = AsyncMock()
        mock_connection.disconnect.side_effect = Exception("Disconnect error")
        service.connection = mock_connection
        service._connected = True

        await service._cleanup_connection()

        mock_connection.disconnect.assert_called_once()
        assert service.connection is None
        assert service._connected is False

    def test_parse_server_info(self):
        """Test _parse_server_info with valid data."""
        service = MCPClientService()
        server_data = {
            "name": "Test Server",
            "version": "1.0.0",
            "protocolVersion": "1.0",
            "capabilities": ["tools", "prompts"],
            "extra": "data"
        }

        result = service._parse_server_info(server_data)

        assert isinstance(result, ServerInfo)
        assert result.name == "Test Server"
        assert result.version == "1.0.0"
        assert result.protocol_version == "1.0"
        assert result.capabilities == ["tools", "prompts"]
        assert result.raw_data == server_data

    def test_parse_server_info_with_minimal_data(self):
        """Test _parse_server_info with minimal data."""
        service = MCPClientService()
        server_data = {}

        result = service._parse_server_info(server_data)

        assert isinstance(result, ServerInfo)
        assert result.name is None
        assert result.version is None
        assert result.protocol_version is None
        assert result.capabilities is None
        assert result.raw_data == server_data

    def test_parse_tools_with_valid_data(self):
        """Test _parse_tools with valid data."""
        service = MCPClientService()
        # Create simple objects with attributes instead of Mock objects
        class MockTool:
            def __init__(self, name, description, input_schema):
                self.name = name
                self.description = description
                self.inputSchema = input_schema
        
        tool_data = [
            MockTool("tool1", "Tool 1", {"type": "object"}),
            MockTool("tool2", "Tool 2", None)
        ]

        result = service._parse_tools(tool_data)

        assert len(result) == 2
        assert all(isinstance(tool, ToolInfo) for tool in result)
        assert result[0].name == "tool1"
        assert result[0].description == "Tool 1"
        assert result[0].input_schema == {"type": "object"}
        assert result[1].name == "tool2"
        assert result[1].description == "Tool 2"
        assert result[1].input_schema is None

    def test_parse_tools_with_invalid_data(self):
        """Test _parse_tools with invalid data that raises exception."""
        service = MCPClientService()
        # Create a class that raises an exception when name is accessed
        class BadTool:
            @property
            def name(self):
                raise Exception("Parse error")
        
        tool_data = [BadTool()]

        result = service._parse_tools(tool_data)

        assert len(result) == 0

    def test_parse_tools_with_string_data(self):
        """Test _parse_tools with string data (fallback case)."""
        service = MCPClientService()
        tool_data = ["tool1", "tool2"]

        result = service._parse_tools(tool_data)

        assert len(result) == 2
        assert result[0].name == "tool1"
        assert result[0].description == ""
        assert result[1].name == "tool2"
        assert result[1].description == ""

    def test_parse_prompts_with_valid_data(self):
        """Test _parse_prompts with valid data."""
        service = MCPClientService()
        # Create simple objects with attributes instead of Mock objects
        class MockPrompt:
            def __init__(self, name, description, arguments):
                self.name = name
                self.description = description
                self.arguments = arguments
        
        prompt_data = [
            MockPrompt("prompt1", "Prompt 1", {"arg1": "string"}),
            MockPrompt("prompt2", "Prompt 2", None)
        ]

        result = service._parse_prompts(prompt_data)

        assert len(result) == 2
        assert all(isinstance(prompt, PromptInfo) for prompt in result)
        assert result[0].name == "prompt1"
        assert result[0].description == "Prompt 1"
        assert result[0].arguments == {"arg1": "string"}
        assert result[1].name == "prompt2"
        assert result[1].description == "Prompt 2"
        assert result[1].arguments is None

    def test_parse_prompts_with_invalid_data(self):
        """Test _parse_prompts with invalid data that raises exception."""
        service = MCPClientService()
        # Create a class that raises an exception when name is accessed
        class BadPrompt:
            @property
            def name(self):
                raise Exception("Parse error")
        
        prompt_data = [BadPrompt()]

        result = service._parse_prompts(prompt_data)

        assert len(result) == 0

    def test_parse_prompts_with_string_data(self):
        """Test _parse_prompts with string data (fallback case)."""
        service = MCPClientService()
        prompt_data = ["prompt1", "prompt2"]

        result = service._parse_prompts(prompt_data)

        assert len(result) == 2
        assert result[0].name == "prompt1"
        assert result[0].description == ""
        assert result[1].name == "prompt2"
        assert result[1].description == ""

    def test_parse_resources_with_valid_data(self):
        """Test _parse_resources with valid data."""
        service = MCPClientService()
        # Create simple objects with attributes instead of Mock objects
        class MockResource:
            def __init__(self, uri, name, description, mime_type):
                self.uri = uri
                self.name = name
                self.description = description
                self.mimeType = mime_type
        
        resource_data = [
            MockResource("file://test1.txt", "Test1", "Test file 1", "text/plain"),
            MockResource("file://test2.txt", None, None, None)
        ]

        result = service._parse_resources(resource_data)

        assert len(result) == 2
        assert all(isinstance(resource, ResourceInfo) for resource in result)
        assert result[0].uri == "file://test1.txt"
        assert result[0].name == "Test1"
        assert result[0].description == "Test file 1"
        assert result[0].mime_type == "text/plain"
        assert result[1].uri == "file://test2.txt"
        assert result[1].name is None
        assert result[1].description is None
        assert result[1].mime_type is None

    def test_parse_resources_with_invalid_data(self):
        """Test _parse_resources with invalid data that raises exception."""
        service = MCPClientService()
        # Create a class that raises an exception when uri is accessed
        class BadResource:
            @property
            def uri(self):
                raise Exception("Parse error")
        
        resource_data = [BadResource()]

        result = service._parse_resources(resource_data)

        assert len(result) == 0

    def test_parse_resources_with_string_data(self):
        """Test _parse_resources with string data (fallback case)."""
        service = MCPClientService()
        resource_data = ["resource1", "resource2"]

        result = service._parse_resources(resource_data)

        assert len(result) == 2
        assert result[0].uri == "resource1"
        assert result[0].name is None
        assert result[1].uri == "resource2"
        assert result[1].name is None

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        service = MCPClientService()
        connection_config = ConnectionConfig(
            connection_type="stdio",
            parameters={"command": "python", "args": ["server.py"]}
        )

        mock_connection = AsyncMock()
        mock_connection.connect.return_value = {
            "name": "Test Server",
            "version": "1.0.0",
            "tools": [],
            "prompts": [],
            "resources": []
        }

        with patch("mcp_client_console.connections.factory.ConnectionFactory.create_connection") as mock_factory:
            mock_factory.return_value = mock_connection

            result = await service.connect(connection_config)

            mock_factory.assert_called_once_with("stdio", command="python", args=["server.py"])
            mock_connection.connect.assert_called_once()
            assert isinstance(result, ServerInfo)
            assert result.name == "Test Server"
            assert service._connected is True
            assert service.connection == mock_connection
            assert service.connection_config == connection_config

    @pytest.mark.asyncio
    async def test_connect_success_with_data(self):
        """Test successful connection with tools, prompts, and resources."""
        service = MCPClientService()
        connection_config = ConnectionConfig(
            connection_type="http",
            parameters={"base_url": "http://localhost:8000"}
        )

        # Create simple objects with attributes instead of Mock objects
        class MockTool:
            def __init__(self, name, description, input_schema):
                self.name = name
                self.description = description
                self.inputSchema = input_schema
        
        class MockPrompt:
            def __init__(self, name, description, arguments):
                self.name = name
                self.description = description
                self.arguments = arguments
        
        class MockResource:
            def __init__(self, uri, name, description, mime_type):
                self.uri = uri
                self.name = name
                self.description = description
                self.mimeType = mime_type

        mock_connection = AsyncMock()
        mock_connection.connect.return_value = {
            "name": "Test Server",
            "version": "1.0.0",
            "tools": [MockTool("tool1", "Tool 1", None)],
            "prompts": [MockPrompt("prompt1", "Prompt 1", None)],
            "resources": [MockResource("file://test.txt", "Test", "Test file", "text/plain")]
        }

        with patch("mcp_client_console.connections.factory.ConnectionFactory.create_connection") as mock_factory:
            mock_factory.return_value = mock_connection

            result = await service.connect(connection_config)

            assert isinstance(result, ServerInfo)
            assert len(service.tools) == 1
            assert len(service.prompts) == 1
            assert len(service.resources) == 1
            assert service.tools[0].name == "tool1"
            assert service.prompts[0].name == "prompt1"
            assert service.resources[0].uri == "file://test.txt"

    @pytest.mark.asyncio
    async def test_connect_failure_with_mcp_error(self):
        """Test connection failure with MCPClientError."""
        service = MCPClientService()
        connection_config = ConnectionConfig(
            connection_type="stdio",
            parameters={"command": "python", "args": ["server.py"]}
        )

        mock_connection = AsyncMock()
        mock_connection.connect.side_effect = MCPClientError("MCP Error")

        with patch("mcp_client_console.connections.factory.ConnectionFactory.create_connection") as mock_factory:
            mock_factory.return_value = mock_connection

            with pytest.raises(MCPClientError, match="MCP Error"):
                await service.connect(connection_config)

            assert service._connected is False
            assert service.connection is None

    @pytest.mark.asyncio
    async def test_connect_failure_with_generic_error(self):
        """Test connection failure with generic error."""
        service = MCPClientService()
        connection_config = ConnectionConfig(
            connection_type="stdio",
            parameters={"command": "python", "args": ["server.py"]}
        )

        mock_connection = AsyncMock()
        mock_connection.connect.side_effect = Exception("Generic Error")

        with patch("mcp_client_console.connections.factory.ConnectionFactory.create_connection") as mock_factory:
            mock_factory.return_value = mock_connection

            with pytest.raises(ConnectionError, match="Connection failed: Generic Error"):
                await service.connect(connection_config)

            assert service._connected is False
            assert service.connection is None

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful disconnection."""
        service = MCPClientService()
        mock_connection = AsyncMock()
        service.connection = mock_connection
        service._connected = True

        await service.disconnect()

        mock_connection.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tool_not_connected(self):
        """Test execute_tool when not connected."""
        service = MCPClientService()
        service._connected = False

        with pytest.raises(ToolExecutionError, match="Not connected to MCP server"):
            await service.execute_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_tool_not_found(self):
        """Test execute_tool when tool is not found."""
        service = MCPClientService()
        service._connected = True
        service.connection = Mock()  # Need connection to pass the first check
        service.tools = []

        with pytest.raises(ToolExecutionError, match="Tool 'test_tool' not found"):
            await service.execute_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_success(self):
        """Test successful tool execution."""
        service = MCPClientService()
        service._connected = True
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]

        mock_connection = AsyncMock()
        mock_connection.call_tool.return_value = {"result": "success"}
        service.connection = mock_connection

        # Don't mock time.time() to avoid StopIteration issues
        result = await service.execute_tool("test_tool", {"arg1": "value1"})

        mock_connection.call_tool.assert_called_once_with("test_tool", {"arg1": "value1"})
        assert isinstance(result, ToolExecutionResult)
        assert result.success is True
        assert result.result == {"result": "success"}
        assert result.execution_time >= 0  # Just check it's a positive number
        assert result.raw_result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_execute_tool_connection_none(self):
        """Test execute_tool when connection is None."""
        service = MCPClientService()
        service._connected = True
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]
        service.connection = None

        with pytest.raises(ToolExecutionError, match="Not connected to MCP server"):
            await service.execute_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_tool_execution_error(self):
        """Test execute_tool when tool execution raises ToolExecutionError."""
        service = MCPClientService()
        service._connected = True
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]

        mock_connection = AsyncMock()
        mock_connection.call_tool.side_effect = ToolExecutionError("Tool failed", tool_name="test_tool")
        service.connection = mock_connection

        with pytest.raises(ToolExecutionError, match="Tool failed"):
            await service.execute_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_generic_error(self):
        """Test execute_tool when tool execution raises generic error."""
        service = MCPClientService()
        service._connected = True
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]

        mock_connection = AsyncMock()
        mock_connection.call_tool.side_effect = Exception("Generic error")
        service.connection = mock_connection

        with pytest.raises(ToolExecutionError, match="Tool execution failed: Generic error"):
            await service.execute_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_error_no_start_time(self):
        """Test execute_tool error handling when start_time is not defined."""
        service = MCPClientService()
        service._connected = True
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]

        mock_connection = AsyncMock()
        mock_connection.call_tool.side_effect = Exception("Error before start_time")
        service.connection = mock_connection

        with pytest.raises(ToolExecutionError, match="Tool execution failed: Error before start_time"):
            await service.execute_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_execute_tool_with_complex_result(self):
        """Test execute_tool with complex result object."""
        service = MCPClientService()
        service._connected = True
        mock_tool = Mock(spec=ToolInfo)
        mock_tool.name = "test_tool"
        service.tools = [mock_tool]

        mock_connection = AsyncMock()
        complex_result = {
            "status": "success",
            "data": {"key": "value"},
            "metadata": {"timestamp": "2023-01-01"}
        }
        mock_connection.call_tool.return_value = complex_result
        service.connection = mock_connection

        # Don't mock time.time() to avoid StopIteration issues
        result = await service.execute_tool("test_tool", {"complex_arg": {"nested": "value"}})

        assert result.success is True
        assert result.result == complex_result
        assert result.execution_time >= 0  # Just check it's a positive number
        assert result.raw_result == complex_result
