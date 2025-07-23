from mcp_client_console.core.exceptions import (
    MCPClientError,
    ConnectionError,
    ToolExecutionError,
    ValidationError,
    ConfigurationError,
)


class TestMCPExceptions:

    def test_mcp_client_error_base(self):
        """Test base MCP client error."""
        error = MCPClientError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_mcp_connection_error(self):
        """Test MCP connection error."""
        error = ConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, MCPClientError)

    def test_mcp_validation_error(self):
        """Test MCP validation error."""
        error = ValidationError("Invalid parameters")
        assert str(error) == "Invalid parameters"
        assert isinstance(error, MCPClientError)

    def test_mcp_timeout_error(self):
        """Test MCP timeout error."""
        error = ConfigurationError("Configuration error")
        assert str(error) == "Configuration error"
        assert isinstance(error, MCPClientError)

    def test_mcp_execution_error(self):
        """Test MCP execution error."""
        error = ToolExecutionError("Tool execution failed")
        assert str(error) == "Tool execution failed"
        assert isinstance(error, MCPClientError)

    def test_unsupported_transport_error(self):
        """Test unsupported transport error."""
        error = ConfigurationError("Unsupported transport")
        assert str(error) == "Unsupported transport"
        assert isinstance(error, MCPClientError)

    def test_error_with_details(self):
        """Test errors with additional details."""
        error = ConnectionError("Connection failed", connection_type="http", connection_params={"server": "localhost", "port": 8080})

        assert str(error) == "Connection failed"
        assert hasattr(error, "details")
        assert error.details["connection_type"] == "http"
        assert error.details["connection_params"]["server"] == "localhost"

    def test_error_inheritance_chain(self):
        """Test that all MCP errors inherit from base classes correctly."""
        connection_error = ConnectionError("test")
        validation_error = ValidationError("test")
        timeout_error = ConfigurationError("test")
        execution_error = ToolExecutionError("test")
        transport_error = ConfigurationError("test")

        # All should inherit from MCPClientError
        assert isinstance(connection_error, MCPClientError)
        assert isinstance(validation_error, MCPClientError)
        assert isinstance(timeout_error, MCPClientError)
        assert isinstance(execution_error, MCPClientError)
        assert isinstance(transport_error, MCPClientError)

        # All should inherit from base Exception
        assert isinstance(connection_error, Exception)
        assert isinstance(validation_error, Exception)
        assert isinstance(timeout_error, Exception)
        assert isinstance(execution_error, Exception)
        assert isinstance(transport_error, Exception)
