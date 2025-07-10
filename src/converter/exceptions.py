"""
Custom exceptions for the resume converter module.

This module defines the exception hierarchy used throughout the converter
pipeline for comprehensive error handling.
"""

from typing import Any


class ConversionError(Exception):
    """
    Base exception for conversion-related errors.

    This is the base class for all errors that occur during the
    resume conversion pipeline.
    """

    def __init__(
        self,
        message: str,
        stage: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize conversion error.

        Args:
            message: Error message
            stage: Optional stage where error occurred
            details: Optional additional error details
        """
        self.stage = stage
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.stage:
            return f"[{self.stage}] {super().__str__()}"
        return super().__str__()


class ValidationError(ConversionError):
    """
    Exception for input validation errors.

    Raised when input files or configuration fail validation
    before processing begins.
    """

    def __init__(
        self, message: str, field: str | None = None, value: Any | None = None
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
        """
        self.field = field
        self.value = value
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, stage="validation", details=details)


class ProcessingError(ConversionError):
    """
    Exception for processing pipeline errors.

    Raised when errors occur during parsing, formatting, or
    output generation stages.
    """

    def __init__(
        self,
        message: str,
        stage: str | None = None,
        component: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """
        Initialize processing error.

        Args:
            message: Error message
            stage: Processing stage where error occurred
            component: Component that caused the error
            original_error: Original exception that was wrapped
        """
        self.component = component
        self.original_error = original_error
        details = {}
        if component:
            details["component"] = component
        if original_error:
            details["original_error"] = str(original_error)
            details["original_type"] = type(original_error).__name__
        super().__init__(message, stage=stage or "processing", details=details)


class ConfigurationError(ConversionError):
    """
    Exception for configuration-related errors.

    Raised when configuration loading or validation fails.
    """

    def __init__(
        self,
        message: str,
        config_path: str | None = None,
        config_section: str | None = None,
    ) -> None:
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_path: Path to configuration file
            config_section: Configuration section with error
        """
        self.config_path = config_path
        self.config_section = config_section
        details = {}
        if config_path:
            details["config_path"] = config_path
        if config_section:
            details["config_section"] = config_section
        super().__init__(message, stage="configuration", details=details)


class FileError(ConversionError):
    """
    Exception for file-related errors.

    Raised when file operations fail during processing.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        operation: str | None = None,
    ) -> None:
        """
        Initialize file error.

        Args:
            message: Error message
            file_path: Path to file that caused error
            operation: File operation that failed
        """
        self.file_path = file_path
        self.operation = operation
        details = {}
        if file_path:
            details["file_path"] = file_path
        if operation:
            details["operation"] = operation
        super().__init__(message, stage="file_operation", details=details)
