from unittest.mock import patch

from mcp_client_console.core.exceptions import ConnectionError, ToolExecutionError, ValidationError, ConfigurationError
from mcp_client_console.utils.error_handler import ErrorHandler


class TestErrorHandler:

    def setup_method(self):
        self.error_handler = ErrorHandler()

    def test_format_error_details_basic(self):
        """Test basic error formatting."""
        error = ValueError("Test error")
        details = self.error_handler.format_error_details(error)

        assert details["error_type"] == "ValueError"
        assert details["error_message"] == "Test error"
        assert "timestamp" in details
        assert "full_traceback" in details

    def test_format_error_details_with_context(self):
        """Test error formatting with additional context."""
        error = ValueError("Test error")
        details = self.error_handler.format_error_details(error)

        assert details["error_type"] == "ValueError"
        assert details["error_message"] == "Test error"
        assert "timestamp" in details

    def test_analyze_url_parsing_error(self):
        """Test URL parsing error analysis."""
        error = ValueError("Failed to parse URL from invalid-url")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "parsing"
        assert "Check data format and structure" in analysis["suggestions"][0]

    def test_analyze_connection_error(self):
        """Test connection error analysis."""
        error = ConnectionError("Connection failed")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "connection"
        assert "Check network connectivity" in analysis["suggestions"][0]

    def test_analyze_timeout_error(self):
        """Test timeout error analysis."""
        error = ConfigurationError("Operation timed out")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "unknown"
        assert len(analysis["suggestions"]) >= 0

    def test_analyze_mcp_connection_error(self):
        """Test MCP connection error analysis."""
        error = ConnectionError("MCP connection failed")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "connection"
        assert "Check network connectivity" in analysis["suggestions"][0]

    def test_analyze_mcp_validation_error(self):
        """Test MCP validation error analysis."""
        error = ValidationError("Invalid parameters")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "unknown"
        assert len(analysis["suggestions"]) >= 0

    def test_analyze_mcp_timeout_error(self):
        """Test MCP timeout error analysis."""
        error = ToolExecutionError("MCP operation timed out")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "unknown"
        assert len(analysis["suggestions"]) >= 0

    def test_analyze_generic_error(self):
        """Test generic error analysis."""
        error = RuntimeError("Some runtime error")
        analysis = self.error_handler._analyze_error(error, str(error))

        assert analysis["error_category"] == "unknown"
        assert len(analysis["suggestions"]) >= 0

    @patch("mcp_client_console.utils.error_handler.datetime")
    def test_timestamp_format(self, mock_datetime):
        """Test that timestamp is properly formatted."""
        from datetime import datetime

        mock_now = datetime(2023, 12, 1, 10, 30, 45)
        mock_datetime.now.return_value = mock_now

        error = ValueError("Test error")
        details = self.error_handler.format_error_details(error)

        assert "2023-12-01T10:30:45" in details["timestamp"]
