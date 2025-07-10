"""
Error handling utilities for the resume converter module.

This module provides comprehensive error handling, logging, and recovery
mechanisms for the conversion pipeline.
"""

import logging
import traceback
from datetime import datetime
from typing import Any

from .exceptions import (
    ConfigurationError,
    FileError,
    ProcessingError,
    ValidationError,
)
from .types import ConversionResult

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Comprehensive error handler for the conversion pipeline.

    Provides error classification, user-friendly messaging, logging,
    and recovery mechanisms.
    """

    def __init__(
        self,
        debug_mode: bool = False,
        logger: logging.Logger | None = None,
        enable_recovery: bool = False,
    ) -> None:
        """
        Initialize the error handler.

        Args:
            debug_mode: Whether to include debug information in errors
            logger: Optional custom logger instance
            enable_recovery: Whether to enable error recovery mechanisms
        """
        self.debug_mode = debug_mode
        self.logger = logger or logging.getLogger(__name__)
        self.enable_recovery = enable_recovery
        self.error_history: list[dict[str, Any]] = []
        self.error_count = 0
        self.warning_count = 0

    def handle_error(
        self,
        error: Exception,
        context: str,
        result: ConversionResult | None = None,
        recover: bool = True,
    ) -> ConversionResult | None:
        """
        Handle an error with comprehensive logging and recovery.

        Args:
            error: The exception that occurred
            context: Context where the error occurred
            result: Optional ConversionResult to update
            recover: Whether to attempt error recovery

        Returns:
            ConversionResult or None if recovery impossible
        """
        error_info = self._classify_error(error, context)

        # Log the error
        self._log_error(error_info, error)

        # Update result if provided
        if result:
            result.add_error(error_info["user_message"])
            result.success = False

        # Record in error history
        self._record_error(error_info, error)

        # Update counters
        if error_info["severity"] == "error" or error_info["severity"] == "critical":
            self.error_count += 1
        else:
            self.warning_count += 1

        # Attempt recovery if requested and enabled
        if recover and self.enable_recovery:
            return self._attempt_recovery(error, error_info, result)

        return result

    def _classify_error(self, error: Exception, context: str) -> dict[str, Any]:
        """
        Classify error and generate appropriate messages.

        Args:
            error: The exception to classify
            context: Context where error occurred

        Returns:
            Dictionary with error classification and messages
        """
        error_type = type(error).__name__
        timestamp = datetime.now().isoformat()

        if isinstance(error, ValidationError):
            return {
                "category": "validation",
                "severity": "error",
                "user_message": self._get_validation_message(error),
                "technical_message": str(error),
                "suggestions": self._get_validation_suggestions(error),
                "recoverable": False,
                "timestamp": timestamp,
                "context": context,
                "error_type": error_type,
            }

        elif isinstance(error, ProcessingError):
            return {
                "category": "processing",
                "severity": "error",
                "user_message": self._get_processing_message(error),
                "technical_message": str(error),
                "suggestions": self._get_processing_suggestions(error),
                "recoverable": True,
                "timestamp": timestamp,
                "context": context,
                "error_type": error_type,
            }

        elif isinstance(error, FileError):
            return {
                "category": "file",
                "severity": "error",
                "user_message": self._get_file_message(error),
                "technical_message": str(error),
                "suggestions": self._get_file_suggestions(error),
                "recoverable": False,
                "timestamp": timestamp,
                "context": context,
                "error_type": error_type,
            }

        elif isinstance(error, ConfigurationError):
            return {
                "category": "configuration",
                "severity": "error",
                "user_message": self._get_config_message(error),
                "technical_message": str(error),
                "suggestions": self._get_config_suggestions(error),
                "recoverable": True,
                "timestamp": timestamp,
                "context": context,
                "error_type": error_type,
            }

        else:
            return {
                "category": "unexpected",
                "severity": "critical",
                "user_message": f"An unexpected error occurred: {str(error)}",
                "technical_message": str(error),
                "suggestions": ["Please report this issue with the error details"],
                "recoverable": False,
                "timestamp": timestamp,
                "context": context,
                "error_type": error_type,
            }

    def _get_validation_message(self, error: ValidationError) -> str:
        """Generate user-friendly validation error message."""
        if hasattr(error, "field") and error.field:
            return f"Invalid {error.field}: {str(error)}"
        return f"Input validation failed: {str(error)}"

    def _get_processing_message(self, error: ProcessingError) -> str:
        """Generate user-friendly processing error message."""
        stage = getattr(error, "stage", "processing")
        component = getattr(error, "component", "")

        stage_messages = {
            "parsing": "Failed to parse the resume markdown",
            "formatting": "Failed to apply ATS formatting",
            "generation": "Failed to generate output files",
        }

        base_message = stage_messages.get(stage, f"Processing failed during {stage}")

        if component:
            return f"{base_message} ({component}): {str(error)}"
        return f"{base_message}: {str(error)}"

    def _get_file_message(self, error: FileError) -> str:
        """Generate user-friendly file error message."""
        file_path = getattr(error, "file_path", "unknown file")
        operation = getattr(error, "operation", "file operation")

        return f"File {operation} failed for {file_path}: {str(error)}"

    def _get_config_message(self, error: ConfigurationError) -> str:
        """Generate user-friendly configuration error message."""
        config_path = getattr(error, "config_path", None)
        config_section = getattr(error, "config_section", None)

        if config_path:
            return f"Configuration error in {config_path}: {str(error)}"
        elif config_section:
            return f"Configuration error in section '{config_section}': {str(error)}"
        return f"Configuration error: {str(error)}"

    def _get_validation_suggestions(self, error: ValidationError) -> list[str]:
        """Get suggestions for validation errors."""
        suggestions = []

        if "contact" in str(error).lower():
            suggestions.append("Ensure contact information includes name and email")
            suggestions.append("Check email format and phone number format")

        if "experience" in str(error).lower():
            suggestions.append("Check date formats in experience section")
            suggestions.append("Ensure job titles and companies are specified")

        if "education" in str(error).lower():
            suggestions.append("Check degree and institution information")
            suggestions.append("Verify education date formats")

        if not suggestions:
            suggestions.append("Review the resume content for completeness")
            suggestions.append("Check that all required sections are present")

        return suggestions

    def _get_processing_suggestions(self, error: ProcessingError) -> list[str]:
        """Get suggestions for processing errors."""
        stage = getattr(error, "stage", "")
        suggestions = []

        if stage == "parsing":
            suggestions.extend(
                [
                    "Check that the file is valid markdown format",
                    "Ensure the file encoding is UTF-8",
                    "Verify the resume structure follows expected format",
                ]
            )

        elif stage == "formatting":
            suggestions.extend(
                [
                    "Check ATS configuration settings",
                    "Verify resume content meets ATS requirements",
                    "Try with default ATS settings",
                ]
            )

        elif stage == "generation":
            suggestions.extend(
                [
                    "Check output directory permissions",
                    "Ensure sufficient disk space",
                    "Verify template files are accessible",
                ]
            )

        else:
            suggestions.append("Try running with debug mode for more details")

        return suggestions

    def _get_file_suggestions(self, error: FileError) -> list[str]:
        """Get suggestions for file errors."""
        return [
            "Check that the file path is correct",
            "Verify file permissions",
            "Ensure the file exists and is readable",
            "Check available disk space for output files",
        ]

    def _get_config_suggestions(self, error: ConfigurationError) -> list[str]:
        """Get suggestions for configuration errors."""
        return [
            "Check the configuration file syntax",
            "Verify all required configuration sections are present",
            "Try using the default configuration",
            "Validate the configuration file against the schema",
        ]

    def _log_error(self, error_info: dict[str, Any], error: Exception) -> None:
        """Log error with appropriate level and detail."""
        severity = error_info["severity"]
        context = error_info["context"]
        user_message = error_info["user_message"]

        log_message = f"[{context}] {user_message}"

        if severity == "critical":
            self.logger.critical(log_message)
        elif severity == "error":
            self.logger.error(log_message)
        else:
            self.logger.warning(log_message)

        # Log technical details at debug level
        if self.debug_mode:
            self.logger.debug(f"Technical details: {error_info['technical_message']}")
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")

    def _record_error(self, error_info: dict[str, Any], error: Exception) -> None:
        """Record error in history for analysis."""
        error_record = {
            **error_info,
            "exception_type": type(error).__name__,
            "stack_trace": traceback.format_exc() if self.debug_mode else None,
        }

        self.error_history.append(error_record)

        # Keep only last 100 errors to prevent memory issues
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

    def _attempt_recovery(
        self,
        error: Exception,
        error_info: dict[str, Any],
        result: ConversionResult | None,
    ) -> ConversionResult | None:
        """
        Attempt to recover from error if possible.

        Args:
            error: The original exception
            error_info: Error classification information
            result: ConversionResult to update

        Returns:
            Updated result if recovery attempted, None if not recoverable
        """
        if not error_info["recoverable"]:
            return result

        category = error_info["category"]

        if category == "processing":
            return self._recover_processing_error(error, result)
        elif category == "configuration":
            return self._recover_configuration_error(error, result)

        return result

    def _recover_processing_error(
        self, error: ProcessingError, result: ConversionResult | None
    ) -> ConversionResult | None:
        """Attempt recovery from processing errors."""
        if result:
            result.add_warning(
                "Processing error occurred, attempting with fallback settings"
            )

        # Add recovery logic here based on specific error types
        # For now, just log the recovery attempt
        self.logger.info("Attempting recovery from processing error")

        return result

    def _recover_configuration_error(
        self, error: ConfigurationError, result: ConversionResult | None
    ) -> ConversionResult | None:
        """Attempt recovery from configuration errors."""
        if result:
            result.add_warning("Configuration error occurred, falling back to defaults")

        self.logger.info("Attempting recovery with default configuration")

        return result

    def get_error_summary(self) -> dict[str, Any]:
        """
        Get summary of recent errors for reporting.

        Returns:
            Dictionary with error statistics and recent errors
        """
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": []}

        # Count errors by category and context
        error_types = {}
        severities = {}
        contexts = {}

        for error in self.error_history:
            category = error["category"]
            severity = error["severity"]
            context = error.get("context", "unknown")

            error_types[category] = error_types.get(category, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
            contexts[context] = contexts.get(context, 0) + 1

        # Find most common context
        most_common_context = max(contexts, key=contexts.get) if contexts else None

        # Get recent errors (last 10)
        recent_errors = self.error_history[-10:]

        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "severities": severities,
            "recent_errors": recent_errors,
            "most_common_context": most_common_context,
            "last_error_time": (
                self.error_history[-1]["timestamp"] if self.error_history else None
            ),
        }

    def clear_error_history(self) -> None:
        """Clear the error history."""
        self.error_history.clear()
        self.error_count = 0
        self.warning_count = 0
        self.logger.debug("Error history cleared")

    def get_recent_errors(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent errors from history.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of recent error records
        """
        return self.error_history[-limit:]

    def export_error_report(self, file_path: str) -> None:
        """
        Export error report to file.

        Args:
            file_path: Path to save the error report
        """
        import json
        from datetime import datetime

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "error_history": self.error_history,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Error report exported to {file_path}")
