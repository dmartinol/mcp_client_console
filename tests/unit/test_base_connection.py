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
        expected_methods = {'connect', 'disconnect', 'send_message', 'receive_message'}
        
        assert expected_methods.issubset(abstract_methods)

    def test_concrete_implementation_works(self):
        """Test that a concrete implementation of MCPConnection can be created"""
        
        class ConcreteConnection(MCPConnection):
            def __init__(self):
                self.is_connected = False
            
            async def connect(self) -> None:
                self.is_connected = True
            
            async def disconnect(self) -> None:
                self.is_connected = False
            
            async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "sent", "message": message}
            
            async def receive_message(self) -> Dict[str, Any]:
                return {"status": "received"}

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
            
            async def connect(self) -> None:
                pass
            
            async def disconnect(self) -> None:
                pass
            
            async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
                return {}
            
            async def receive_message(self) -> Dict[str, Any]:
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
                self.messages = []
            
            async def connect(self) -> None:
                self.is_connected = True
            
            async def disconnect(self) -> None:
                self.is_connected = False
            
            async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
                if not self.is_connected:
                    raise RuntimeError("Not connected")
                self.messages.append(message)
                return {"sent": True}
            
            async def receive_message(self) -> Dict[str, Any]:
                if not self.is_connected:
                    raise RuntimeError("Not connected")
                return {"received": True}

        connection = AsyncConnection()
        
        # Test connection lifecycle
        await connection.connect()
        assert connection.is_connected is True
        
        # Test message sending
        result = await connection.send_message({"test": "message"})
        assert result == {"sent": True}
        assert connection.messages == [{"test": "message"}]
        
        # Test message receiving
        result = await connection.receive_message()
        assert result == {"received": True}
        
        # Test disconnection
        await connection.disconnect()
        assert connection.is_connected is False
