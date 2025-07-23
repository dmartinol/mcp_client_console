"""
Centralized error handling utilities.
"""

import json
import re
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

from ..core.exceptions import ConnectionError, MCPClientError, ToolExecutionError
from .logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """
    Centralized error handling and reporting utilities.
    """

    @staticmethod
    def format_error_details(error: Exception) -> Dict[str, Any]:
        """
        Format exception details for display or logging.

        Args:
            error: Exception to format

        Returns:
            Dictionary with formatted error details
        """
        error_message = str(error)

        details = {
            "error_type": type(error).__name__,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
            "full_traceback": traceback.format_exc(),
        }

        # Enhanced error analysis
        details.update(ErrorHandler._analyze_error(error, error_message))

        # Add specific details for MCP errors
        if isinstance(error, MCPClientError):
            details.update(error.details)
            details["traceback"] = error.traceback_info

        if isinstance(error, ConnectionError):
            details["connection_type"] = error.connection_type
            details["connection_params"] = error.connection_params

        if isinstance(error, ToolExecutionError):
            details["tool_name"] = error.tool_name
            details["arguments"] = error.arguments
            details["execution_context"] = error.execution_context

        return details

    @staticmethod
    def _analyze_error(error: Exception, error_message: str) -> Dict[str, Any]:
        """
        Analyze error to detect common patterns and provide additional context.

        Args:
            error: Exception to analyze
            error_message: String representation of the error

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "error_category": "unknown",
            "suggestions": [],
            "additional_context": {},
        }

        # URL parsing errors
        if "Invalid URL" in error_message or "urlparse" in error_message.lower():
            analysis["error_category"] = "url_parsing"
            analysis["suggestions"].append(
                "Check that the URL is properly formatted with protocol (http:// or https://)"
            )
            analysis["suggestions"].append(
                "Ensure the URL doesn't contain invalid characters"
            )

            # Try to extract problematic URL from error message
            url_pattern = r"(?:http[s]?://|www\.|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})\S*"
            urls = re.findall(url_pattern, error_message)
            if urls:
                analysis["additional_context"]["problematic_urls"] = urls

        # Connection errors
        elif any(
            keyword in error_message.lower()
            for keyword in ["connection", "timeout", "refused", "unreachable"]
        ):
            analysis["error_category"] = "connection"
            analysis["suggestions"].append("Check network connectivity")
            analysis["suggestions"].append("Verify server is running and accessible")
            analysis["suggestions"].append("Check firewall settings")

        # JSON/parsing errors
        elif any(
            keyword in error_message.lower() for keyword in ["json", "parse", "decode"]
        ):
            analysis["error_category"] = "parsing"
            analysis["suggestions"].append("Check data format and structure")
            analysis["suggestions"].append("Verify input contains valid JSON/data")

        # Permission errors
        elif any(
            keyword in error_message.lower()
            for keyword in ["permission", "access", "denied", "unauthorized"]
        ):
            analysis["error_category"] = "permission"
            analysis["suggestions"].append("Check file/directory permissions")
            analysis["suggestions"].append("Verify authentication credentials")
            analysis["suggestions"].append("Ensure proper access rights")

        # File system errors
        elif any(
            keyword in error_message.lower()
            for keyword in ["file not found", "no such file", "directory"]
        ):
            analysis["error_category"] = "filesystem"
            analysis["suggestions"].append("Verify file/directory path exists")
            analysis["suggestions"].append("Check spelling and case sensitivity")
            analysis["suggestions"].append("Ensure proper file permissions")

        # Tool execution errors
        elif "tool" in error_message.lower():
            analysis["error_category"] = "tool_execution"
            analysis["suggestions"].append("Check tool parameters and arguments")
            analysis["suggestions"].append(
                "Verify tool is available and properly configured"
            )
            analysis["suggestions"].append("Review tool documentation for proper usage")

        return analysis

    @staticmethod
    def get_user_friendly_message(error: Exception) -> str:
        """
        Get a user-friendly error message.

        Args:
            error: Exception to format

        Returns:
            User-friendly error message
        """
        if isinstance(error, ConnectionError):
            return f"Failed to connect to MCP server: {error.message}"

        if isinstance(error, ToolExecutionError):
            return f"Tool execution failed: {error.message}"

        if isinstance(error, MCPClientError):
            return error.message

        # Generic fallback
        return f"An unexpected error occurred: {str(error)}"

    @staticmethod
    def log_error(error: Exception, context: Optional[str] = None):
        """
        Log error with appropriate level and details.

        Args:
            error: Exception to log
            context: Optional context string
        """
        error_details = ErrorHandler.format_error_details(error)
        context_msg = f" in {context}" if context else ""

        if isinstance(error, (ConnectionError, ToolExecutionError)):
            logger.error(f"{type(error).__name__}{context_msg}: {error.message}")
            logger.debug(f"Error details: {json.dumps(error_details, indent=2)}")
        else:
            logger.error(f"Unexpected error{context_msg}: {str(error)}")
            logger.debug(f"Error details: {json.dumps(error_details, indent=2)}")


def handle_errors(
    context: Optional[str] = None,
    reraise: bool = True,
    ui_callback: Optional[Callable[[Exception], None]] = None,
):
    """
    Decorator for handling errors in functions.

    Args:
        context: Context string for error logging
        reraise: Whether to reraise the exception after handling
        ui_callback: Optional callback for UI error display
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, context or func.__name__)

                if ui_callback:
                    ui_callback(e)

                if reraise:
                    raise
                return None

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, context or func.__name__)

                if ui_callback:
                    ui_callback(e)

                if reraise:
                    raise
                return None

        # Return appropriate wrapper based on function type
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
