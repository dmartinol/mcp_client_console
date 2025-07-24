import pytest
from abc import ABC
from typing import Dict, Any

from mcp_client_console.connections.base import MCPConnection


class TestMCPConnectionInterface:
    """Test cases for the MCPConnection abstract base class"""

    def test_mcp_connection_is_abstract(self):
        """Test that MCPConnection cannot be instantiated directly"""
        with pytest.raises(TypeError):
            MCPConnection()

    def test_mcp_connection_defines_required_methods(self):
        """Test that MCPConnection defines the required abstract methods"""
        # Check that the abstract methods are defined
        abstract_methods = MCPConnection.__abstractmethods__
        expected_methods = {'connect', 'disconnect', 'call_tool'}
        
        assert expected_methods.issubset(abstract_methods)

    def test_concrete_implementation_works(self):
        """Test that a concrete implementation of MCPConnection can be created"""
        
        class ConcreteConnection(MCPConnection):
            def __init__(self):
                self.is_connected = False
            
            async def connect(self) -> Dict[str, Any]:
                self.is_connected = True
                return {}
            
            async def disconnect(self) -> None:
                self.is_connected = False
            
            async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
                return {"status": "executed", "tool": tool_name, "arguments": arguments}

        # This should work without raising an exception
        connection = ConcreteConnection()
        assert isinstance(connection, MCPConnection)
        assert connection.is_connected is False

    def test_inheritance_hierarchy(self):
        """Test that MCPConnection properly inherits from ABC"""
        assert issubclass(MCPConnection, ABC)
        assert hasattr(MCPConnection, '__abstractmethods__')

    def test_connection_has_is_connected_property(self):
        """Test that MCPConnection implementations should have is_connected property"""
        
        class TestConnection(MCPConnection):
            def __init__(self):
                self.is_connected = False
            
            async def connect(self) -> Dict[str, Any]:
                return {}
            
            async def disconnect(self) -> None:
                pass
            
            async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
                return {}

        connection = TestConnection()
        # While not enforced by the interface, implementations should have this property
        assert hasattr(connection, 'is_connected')
        assert isinstance(connection.is_connected, bool)

    @pytest.mark.asyncio
    async def test_concrete_implementation_async_methods(self):
        """Test that concrete implementation async methods work correctly"""
        
        class AsyncConnection(MCPConnection):
            def __init__(self):
                self.is_connected = False
                self.tools_called = []
            
            async def connect(self) -> Dict[str, Any]:
                self.is_connected = True
                return {}
            
            async def disconnect(self) -> None:
                self.is_connected = False
            
            async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
                if not self.is_connected:
                    raise RuntimeError("Not connected")
                self.tools_called.append({"tool": tool_name, "arguments": arguments})
                return {"executed": True, "tool": tool_name}

        connection = AsyncConnection()
        
        # Test connection lifecycle
        result = await connection.connect()
        assert connection.is_connected is True
        assert result == {}
        
        # Test tool calling
        result = await connection.call_tool("test_tool", {"param": "value"})
        assert result == {"executed": True, "tool": "test_tool"}
        assert connection.tools_called == [{"tool": "test_tool", "arguments": {"param": "value"}}]
        
        # Test disconnection
        await connection.disconnect()
        assert connection.is_connected is False
