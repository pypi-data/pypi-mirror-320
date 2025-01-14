# src/nyc_records_common/utils/error_handler.py
"""Error handling utilities for NYC Records."""
import logging
from enum import Enum
from typing import Optional


class ErrorLevel(Enum):
    """Error severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorHandler:
    """Centralized error handling and logging."""

    def __init__(self, logger_name: str = "nyc_records"):
        """Initialize error handler with logger.

        Args:
            logger_name: Name for the logger instance
        """
        self.logger = logging.getLogger(logger_name)

    def handle_error(
        self, error_type: str, details: str, level: ErrorLevel = ErrorLevel.ERROR, exc: Optional[Exception] = None
    ) -> None:
        """Log standardized error message.

        Args:
            error_type: Type of error that occurred
            details: Detailed error message
            level: Error severity level
            exc: Optional exception object
        """
        message = f"{error_type}: {details}"

        if exc:
            message += f" | Exception: {str(exc)}"

        if level == ErrorLevel.INFO:
            self.logger.info(message)
        elif level == ErrorLevel.WARNING:
            self.logger.warning(message)
        elif level == ErrorLevel.ERROR:
            self.logger.error(message)
        elif level == ErrorLevel.CRITICAL:
            self.logger.critical(message)
