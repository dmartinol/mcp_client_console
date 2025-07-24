import pytest
import json
import re
from unittest.mock import patch, Mock
from datetime import datetime

from mcp_client_console.core.exceptions import (
    ConnectionError, 
    ToolExecutionError, 
    MCPClientError
)
from mcp_client_console.utils.error_handler import ErrorHandler, handle_errors


class TestErrorHandler:
    """Test cases for ErrorHandler class."""

    def test_format_error_details_basic(self):
        """Test basic error formatting."""
        error = ValueError("Test error")
        details = ErrorHandler.format_error_details(error)

        assert details["error_type"] == "ValueError"
        assert details["error_message"] == "Test error"
        assert "timestamp" in details
        assert "full_traceback" in details
        assert "error_category" in details
        assert "suggestions" in details
        assert "additional_context" in details

    def test_format_error_details_with_context(self):
        """Test error formatting with additional context."""
        error = ValueError("Test error")
        details = ErrorHandler.format_error_details(error)

        assert details["error_type"] == "ValueError"
        assert details["error_message"] == "Test error"
        assert "timestamp" in details
        assert isinstance(details["suggestions"], list)
        assert isinstance(details["additional_context"], dict)

    def test_format_error_details_with_mcp_client_error(self):
        """Test error formatting with MCPClientError."""
        error = MCPClientError("MCP Error", details={"key": "value"})
        details = ErrorHandler.format_error_details(error)

        assert details["error_type"] == "MCPClientError"
        assert details["error_message"] == "MCP Error"
        assert details["key"] == "value"
        assert "traceback" in details

    def test_format_error_details_with_connection_error(self):
        """Test error formatting with ConnectionError."""
        error = ConnectionError(
            "Connection failed", 
            connection_type="stdio",
            connection_params={"command": "python"}
        )
        details = ErrorHandler.format_error_details(error)

        assert details["error_type"] == "ConnectionError"
        assert details["error_message"] == "Connection failed"
        assert details["connection_type"] == "stdio"
        assert details["connection_params"] == {"command": "python"}

    def test_format_error_details_with_tool_execution_error(self):
        """Test error formatting with ToolExecutionError."""
        error = ToolExecutionError(
            "Tool failed",
            tool_name="test_tool",
            arguments={"arg1": "value1"},
            execution_context={"time": 1.5}
        )
        details = ErrorHandler.format_error_details(error)

        assert details["error_type"] == "ToolExecutionError"
        assert details["error_message"] == "Tool failed"
        assert details["tool_name"] == "test_tool"
        assert details["arguments"] == {"arg1": "value1"}
        assert details["execution_context"] == {"time": 1.5}

    def test_analyze_url_parsing_error(self):
        """Test URL parsing error analysis."""
        error = ValueError("Invalid URL: http://invalid-url")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "url_parsing"
        assert len(analysis["suggestions"]) >= 2
        assert "Check that the URL is properly formatted" in analysis["suggestions"][0]
        assert "Ensure the URL doesn't contain invalid characters" in analysis["suggestions"][1]

    def test_analyze_url_parsing_error_with_url_extraction(self):
        """Test URL parsing error analysis with URL extraction."""
        error = ValueError("Invalid URL: http://example.com/path")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "url_parsing"
        assert "problematic_urls" in analysis["additional_context"]
        assert "http://example.com/path" in analysis["additional_context"]["problematic_urls"]

    def test_analyze_connection_error(self):
        """Test connection error analysis."""
        error = ConnectionError("Connection refused")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "connection"
        assert "Check network connectivity" in analysis["suggestions"][0]
        assert "Verify server is running and accessible" in analysis["suggestions"][1]
        assert "Check firewall settings" in analysis["suggestions"][2]

    def test_analyze_timeout_error(self):
        """Test timeout error analysis."""
        error = TimeoutError("Connection timeout occurred")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "connection"
        assert "Check network connectivity" in analysis["suggestions"][0]

    def test_analyze_json_parsing_error(self):
        """Test JSON parsing error analysis."""
        error = json.JSONDecodeError("Invalid JSON", "invalid json", 0)
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "parsing"
        assert "Check data format and structure" in analysis["suggestions"][0]
        assert "Verify input contains valid JSON/data" in analysis["suggestions"][1]

    def test_analyze_permission_error(self):
        """Test permission error analysis."""
        error = PermissionError("Access denied")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "permission"
        assert "Check file/directory permissions" in analysis["suggestions"][0]
        assert "Verify authentication credentials" in analysis["suggestions"][1]
        assert "Ensure proper access rights" in analysis["suggestions"][2]

    def test_analyze_filesystem_error(self):
        """Test filesystem error analysis."""
        error = FileNotFoundError("No such file or directory")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "filesystem"
        assert "Verify file/directory path exists" in analysis["suggestions"][0]
        assert "Check spelling and case sensitivity" in analysis["suggestions"][1]
        assert "Ensure proper file permissions" in analysis["suggestions"][2]

    def test_analyze_tool_execution_error(self):
        """Test tool execution error analysis."""
        error = ToolExecutionError("Tool execution failed")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "tool_execution"
        assert "Check tool parameters and arguments" in analysis["suggestions"][0]
        assert "Verify tool is available and properly configured" in analysis["suggestions"][1]
        assert "Review tool documentation for proper usage" in analysis["suggestions"][2]

    def test_analyze_generic_error(self):
        """Test generic error analysis."""
        error = RuntimeError("Some runtime error")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "unknown"
        assert len(analysis["suggestions"]) == 0

    def test_analyze_error_with_multiple_keywords(self):
        """Test error analysis with multiple matching keywords."""
        error = ConnectionError("Connection timeout and refused")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "connection"
        assert len(analysis["suggestions"]) >= 3

    def test_get_user_friendly_message_connection_error(self):
        """Test user-friendly message for ConnectionError."""
        error = ConnectionError("Connection failed")
        message = ErrorHandler.get_user_friendly_message(error)

        assert message == "Failed to connect to MCP server: Connection failed"

    def test_get_user_friendly_message_tool_execution_error(self):
        """Test user-friendly message for ToolExecutionError."""
        error = ToolExecutionError("Tool failed")
        message = ErrorHandler.get_user_friendly_message(error)

        assert message == "Tool execution failed: Tool failed"

    def test_get_user_friendly_message_mcp_client_error(self):
        """Test user-friendly message for MCPClientError."""
        error = MCPClientError("MCP Error")
        message = ErrorHandler.get_user_friendly_message(error)

        assert message == "MCP Error"

    def test_get_user_friendly_message_generic_error(self):
        """Test user-friendly message for generic error."""
        error = ValueError("Some value error")
        message = ErrorHandler.get_user_friendly_message(error)

        assert message == "An unexpected error occurred: Some value error"

    @patch("mcp_client_console.utils.error_handler.logger")
    def test_log_error_connection_error(self, mock_logger):
        """Test logging ConnectionError."""
        error = ConnectionError("Connection failed")
        ErrorHandler.log_error(error, "test_context")

        mock_logger.error.assert_called_once_with("ConnectionError in test_context: Connection failed")
        mock_logger.debug.assert_called_once()

    @patch("mcp_client_console.utils.error_handler.logger")
    def test_log_error_tool_execution_error(self, mock_logger):
        """Test logging ToolExecutionError."""
        error = ToolExecutionError("Tool failed")
        ErrorHandler.log_error(error, "test_context")

        mock_logger.error.assert_called_once_with("ToolExecutionError in test_context: Tool failed")
        mock_logger.debug.assert_called_once()

    @patch("mcp_client_console.utils.error_handler.logger")
    def test_log_error_generic_error(self, mock_logger):
        """Test logging generic error."""
        error = ValueError("Some error")
        ErrorHandler.log_error(error, "test_context")

        mock_logger.error.assert_called_once_with("Unexpected error in test_context: Some error")
        mock_logger.debug.assert_called_once()

    @patch("mcp_client_console.utils.error_handler.logger")
    def test_log_error_no_context(self, mock_logger):
        """Test logging error without context."""
        error = ValueError("Some error")
        ErrorHandler.log_error(error)

        mock_logger.error.assert_called_once_with("Unexpected error: Some error")
        mock_logger.debug.assert_called_once()

    @patch("mcp_client_console.utils.error_handler.datetime")
    def test_timestamp_format(self, mock_datetime):
        """Test that timestamp is properly formatted."""
        mock_now = datetime(2023, 12, 1, 10, 30, 45)
        mock_datetime.now.return_value = mock_now

        error = ValueError("Test error")
        details = ErrorHandler.format_error_details(error)

        assert details["timestamp"] == "2023-12-01T10:30:45"

    def test_analyze_error_with_url_pattern_matching(self):
        """Test URL pattern matching in error analysis."""
        error = ValueError("Invalid URL: https://example.com/path?param=value")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "url_parsing"
        assert "problematic_urls" in analysis["additional_context"]
        urls = analysis["additional_context"]["problematic_urls"]
        assert any("https://example.com/path" in url for url in urls)

    def test_analyze_error_with_www_url(self):
        """Test URL pattern matching with www URLs."""
        error = ValueError("Invalid URL: www.example.com")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "url_parsing"
        assert "problematic_urls" in analysis["additional_context"]
        urls = analysis["additional_context"]["problematic_urls"]
        assert any("www.example.com" in url for url in urls)

    def test_analyze_error_with_domain_only(self):
        """Test URL pattern matching with domain-only URLs."""
        error = ValueError("Invalid URL: example.com")
        analysis = ErrorHandler._analyze_error(error, str(error))

        assert analysis["error_category"] == "url_parsing"
        assert "problematic_urls" in analysis["additional_context"]
        urls = analysis["additional_context"]["problematic_urls"]
        assert any("example.com" in url for url in urls)


class TestHandleErrorsDecorator:
    """Test cases for handle_errors decorator."""

    def test_handle_errors_sync_function_success(self):
        """Test handle_errors decorator with successful sync function."""
        @handle_errors("test_context")
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_handle_errors_sync_function_error(self):
        """Test handle_errors decorator with sync function that raises error."""
        @handle_errors("test_context")
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

    def test_handle_errors_sync_function_error_no_reraise(self):
        """Test handle_errors decorator with sync function error and no reraise."""
        @handle_errors("test_context", reraise=False)
        def test_func():
            raise ValueError("Test error")

        result = test_func()
        assert result is None

    def test_handle_errors_sync_function_with_ui_callback(self):
        """Test handle_errors decorator with sync function and UI callback."""
        callback_called = False
        callback_error = None

        def ui_callback(error):
            nonlocal callback_called, callback_error
            callback_called = True
            callback_error = error

        @handle_errors("test_context", ui_callback=ui_callback)
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

        assert callback_called
        assert isinstance(callback_error, ValueError)
        assert str(callback_error) == "Test error"

    @pytest.mark.asyncio
    async def test_handle_errors_async_function_success(self):
        """Test handle_errors decorator with successful async function."""
        @handle_errors("test_context")
        async def test_func():
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_handle_errors_async_function_error(self):
        """Test handle_errors decorator with async function that raises error."""
        @handle_errors("test_context")
        async def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await test_func()

    @pytest.mark.asyncio
    async def test_handle_errors_async_function_error_no_reraise(self):
        """Test handle_errors decorator with async function error and no reraise."""
        @handle_errors("test_context", reraise=False)
        async def test_func():
            raise ValueError("Test error")

        result = await test_func()
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_errors_async_function_with_ui_callback(self):
        """Test handle_errors decorator with async function and UI callback."""
        callback_called = False
        callback_error = None

        def ui_callback(error):
            nonlocal callback_called, callback_error
            callback_called = True
            callback_error = error

        @handle_errors("test_context", ui_callback=ui_callback)
        async def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await test_func()

        assert callback_called
        assert isinstance(callback_error, ValueError)
        assert str(callback_error) == "Test error"

    def test_handle_errors_with_default_context(self):
        """Test handle_errors decorator with default context (function name)."""
        @handle_errors()
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

    def test_handle_errors_with_complex_error(self):
        """Test handle_errors decorator with complex error types."""
        @handle_errors("test_context")
        def test_func():
            raise ConnectionError("Connection failed", connection_type="stdio")

        with pytest.raises(ConnectionError, match="Connection failed"):
            test_func()

    @pytest.mark.asyncio
    async def test_handle_errors_async_with_complex_error(self):
        """Test handle_errors decorator with async function and complex error."""
        @handle_errors("test_context")
        async def test_func():
            raise ToolExecutionError("Tool failed", tool_name="test_tool")

        with pytest.raises(ToolExecutionError, match="Tool failed"):
            await test_func()
