"""
Logging utilities for MCP Client Console.
"""

import logging
import sys
from typing import Optional

# Global logger configuration
_configured = False

def configure_logging(level: str = "INFO", format_string: Optional[str] = None):
    """
    Configure global logging settings.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    global _configured
    
    if _configured:
        return
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    _configured = True

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    # Ensure logging is configured
    if not _configured:
        configure_logging()
    
    return logging.getLogger(name)

def set_log_level(level: str):
    """
    Set the global log level.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger().setLevel(getattr(logging, level.upper()))
