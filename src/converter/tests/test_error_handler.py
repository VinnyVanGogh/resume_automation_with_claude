"""
Unit tests for the ErrorHandler class.

Tests error classification, handling, recovery mechanisms,
user-friendly messaging, and logging integration.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ..error_handler import ErrorHandler
from ..exceptions import (
    ConfigurationError,
    ConversionError,
    FileError,
    ProcessingError,
    ValidationError,
)
from ..types import ConversionResult


class TestErrorHandlerInitialization:
    """Test ErrorHandler initialization and configuration."""

    def test_default_initialization(self):
        """Test error handler with default settings."""
        handler = ErrorHandler()

        assert handler is not None
        assert hasattr(handler, "logger")
        assert handler.error_count == 0
        assert handler.warning_count == 0
        assert len(handler.error_history) == 0

    def test_initialization_with_custom_logger(self):
        """Test error handler with custom logger."""
        custom_logger = logging.getLogger("test_logger")
        handler = ErrorHandler(logger=custom_logger)

        assert handler.logger == custom_logger

    def test_initialization_with_recovery_enabled(self):
        """Test error handler with recovery enabled."""
        handler = ErrorHandler(enable_recovery=True)

        assert hasattr(handler, "enable_recovery")
        # Note: implementation details may vary


class TestErrorHandlerClassification:
    """Test error classification functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()

    def test_classify_validation_error(self):
        """Test classification of validation errors."""
        error = ValidationError("Invalid input format")

        classification = self.handler.classify_error(error)

        assert classification["type"] == "validation"
        assert classification["severity"] == "medium"
        assert classification["recoverable"] is True
        assert "input validation" in classification["category"].lower()

    def test_classify_file_error(self):
        """Test classification of file errors."""
        error = FileError("File not found", file_path="/path/to/file.md")

        classification = self.handler.classify_error(error)

        assert classification["type"] == "file"
        assert classification["severity"] == "high"
        assert classification["recoverable"] is False
        assert "/path/to/file.md" in str(classification.get("context", ""))

    def test_classify_processing_error(self):
        """Test classification of processing errors."""
        error = ProcessingError("Template rendering failed", stage="generation")

        classification = self.handler.classify_error(error)

        assert classification["type"] == "processing"
        assert classification["severity"] == "high"
        assert "generation" in str(classification.get("context", ""))

    def test_classify_configuration_error(self):
        """Test classification of configuration errors."""
        error = ConfigurationError(
            "Invalid configuration", config_path="/path/config.yaml"
        )

        classification = self.handler.classify_error(error)

        assert classification["type"] == "configuration"
        assert classification["severity"] == "high"
        assert classification["recoverable"] is True

    def test_classify_generic_error(self):
        """Test classification of generic errors."""
        error = Exception("Generic error message")

        classification = self.handler.classify_error(error)

        assert classification["type"] == "unknown"
        assert classification["severity"] == "medium"
        assert classification["recoverable"] is False

    def test_classify_conversion_error_with_stage(self):
        """Test classification of conversion error with stage information."""
        error = ConversionError("Parsing failed", stage="parsing")

        classification = self.handler.classify_error(error)

        assert classification["type"] == "conversion"
        assert "parsing" in str(classification.get("context", ""))


class TestErrorHandlerMessaging:
    """Test user-friendly error messaging."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()

    def test_generate_user_friendly_message_validation(self):
        """Test user-friendly message for validation errors."""
        error = ValidationError("Input file format is not supported")

        message = self.handler.generate_user_friendly_message(error)

        assert "input" in message.lower()
        assert "format" in message.lower()
        assert len(message) > len(str(error))  # Should be more descriptive
        assert not message.startswith("Traceback")  # Should not include traceback

    def test_generate_user_friendly_message_file(self):
        """Test user-friendly message for file errors."""
        error = FileError(
            "Permission denied", file_path="/protected/file.md", operation="read"
        )

        message = self.handler.generate_user_friendly_message(error)

        assert "permission" in message.lower()
        assert "/protected/file.md" in message
        assert "read" in message.lower()

    def test_generate_user_friendly_message_with_suggestions(self):
        """Test user-friendly message includes suggestions."""
        error = ConfigurationError("Configuration file not found")

        message = self.handler.generate_user_friendly_message(error)

        # Should include helpful suggestions
        assert any(
            word in message.lower() for word in ["check", "verify", "ensure", "try"]
        )

    def test_generate_user_friendly_message_processing(self):
        """Test user-friendly message for processing errors."""
        error = ProcessingError("Template not found", stage="generation")

        message = self.handler.generate_user_friendly_message(error)

        assert "template" in message.lower()
        assert "generation" in message.lower()

    def test_generate_recovery_suggestions(self):
        """Test generation of recovery suggestions."""
        # Test validation error suggestions
        error = ValidationError("Invalid markdown format")
        suggestions = self.handler.generate_recovery_suggestions(error)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any("format" in suggestion.lower() for suggestion in suggestions)

        # Test file error suggestions
        error = FileError("File not found", file_path="/missing/file.md")
        suggestions = self.handler.generate_recovery_suggestions(error)

        assert any("path" in suggestion.lower() for suggestion in suggestions)
        assert any("exist" in suggestion.lower() for suggestion in suggestions)


class TestErrorHandlerHandling:
    """Test error handling and recovery functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()

    def test_handle_error_basic(self):
        """Test basic error handling."""
        error = ValidationError("Test validation error")
        context = "test_context"

        result = self.handler.handle_error(error, context)

        assert result is None  # No result returned for basic handling
        assert self.handler.error_count == 1
        assert len(self.handler.error_history) == 1

        # Check error history
        error_record = self.handler.error_history[0]
        assert error_record["error"] == error
        assert error_record["context"] == context
        assert "timestamp" in error_record

    def test_handle_error_with_result(self):
        """Test error handling with conversion result."""
        error = ProcessingError("Test processing error")
        context = "test_context"
        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[],
            processing_time=1.0,
        )

        updated_result = self.handler.handle_error(error, context, result=result)

        assert updated_result is not None
        assert updated_result.success is False
        assert len(updated_result.errors) == 1
        assert "test processing error" in updated_result.errors[0].lower()

    def test_handle_error_with_recovery(self):
        """Test error handling with recovery enabled."""
        error = ConfigurationError("Invalid config")
        context = "config_loading"

        with patch.object(self.handler, "_attempt_error_recovery") as mock_recovery:
            mock_recovery.return_value = True

            result = self.handler.handle_error(error, context, recover=True)

            mock_recovery.assert_called_once_with(error, context)

    def test_handle_multiple_errors(self):
        """Test handling multiple errors."""
        errors = [
            ValidationError("Error 1"),
            ProcessingError("Error 2"),
            FileError("Error 3"),
        ]

        for error in errors:
            self.handler.handle_error(error, "test_context")

        assert self.handler.error_count == 3
        assert len(self.handler.error_history) == 3

    def test_handle_error_logging(self):
        """Test that errors are properly logged."""
        with patch.object(self.handler.logger, "error") as mock_log_error:
            error = ConversionError("Test error")
            self.handler.handle_error(error, "test_context")

            mock_log_error.assert_called_once()
            call_args = mock_log_error.call_args[0][0]
            assert "test error" in call_args.lower()


class TestErrorHandlerRecovery:
    """Test error recovery mechanisms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler(enable_recovery=True)

    def test_attempt_recovery_validation_error(self):
        """Test recovery attempt for validation errors."""
        error = ValidationError("Invalid input format")

        with patch.object(
            self.handler, "_recover_from_validation_error"
        ) as mock_recovery:
            mock_recovery.return_value = True

            success = self.handler._attempt_error_recovery(error, "test_context")

            assert success is True
            mock_recovery.assert_called_once_with(error, "test_context")

    def test_attempt_recovery_configuration_error(self):
        """Test recovery attempt for configuration errors."""
        error = ConfigurationError("Config file not found")

        with patch.object(
            self.handler, "_recover_from_configuration_error"
        ) as mock_recovery:
            mock_recovery.return_value = True

            success = self.handler._attempt_error_recovery(error, "test_context")

            assert success is True
            mock_recovery.assert_called_once_with(error, "test_context")

    def test_attempt_recovery_file_error(self):
        """Test recovery attempt for file errors."""
        error = FileError("File not found", file_path="/missing/file.md")

        with patch.object(self.handler, "_recover_from_file_error") as mock_recovery:
            mock_recovery.return_value = False  # File errors typically not recoverable

            success = self.handler._attempt_error_recovery(error, "test_context")

            assert success is False
            mock_recovery.assert_called_once_with(error, "test_context")

    def test_attempt_recovery_unsupported_error(self):
        """Test recovery attempt for unsupported error types."""
        error = Exception("Generic error")

        success = self.handler._attempt_error_recovery(error, "test_context")

        assert success is False  # No recovery for generic errors

    def test_configuration_fallback_recovery(self):
        """Test configuration fallback recovery."""
        error = ConfigurationError("Invalid configuration value")

        # Mock the recovery method
        with patch.object(self.handler, "_load_default_configuration") as mock_default:
            mock_default.return_value = True

            success = self.handler._recover_from_configuration_error(
                error, "config_loading"
            )

            assert success is True
            mock_default.assert_called_once()

    def test_validation_retry_recovery(self):
        """Test validation retry recovery."""
        error = ValidationError("Temporary validation failure")

        with patch.object(self.handler, "_retry_with_relaxed_validation") as mock_retry:
            mock_retry.return_value = True

            success = self.handler._recover_from_validation_error(
                error, "input_validation"
            )

            assert success is True
            mock_retry.assert_called_once()


class TestErrorHandlerReporting:
    """Test error reporting and statistics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()

        # Add some test errors
        self.handler.handle_error(ValidationError("Validation error"), "validation")
        self.handler.handle_error(ProcessingError("Processing error"), "processing")
        self.handler.handle_error(FileError("File error"), "file_ops")

    def test_get_error_summary(self):
        """Test getting error summary."""
        summary = self.handler.get_error_summary()

        assert isinstance(summary, dict)
        assert summary["total_errors"] == 3
        assert summary["error_types"]["validation"] == 1
        assert summary["error_types"]["processing"] == 1
        assert summary["error_types"]["file"] == 1
        assert "most_common_context" in summary

    def test_get_recent_errors(self):
        """Test getting recent errors."""
        recent = self.handler.get_recent_errors(limit=2)

        assert len(recent) == 2
        assert all("timestamp" in error for error in recent)
        assert all("error" in error for error in recent)
        assert all("context" in error for error in recent)

    def test_export_error_report(self):
        """Test exporting error report."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report_path = f.name

        try:
            self.handler.export_error_report(report_path)

            # Verify file was created
            assert Path(report_path).exists()

            # Verify content
            import json

            with open(report_path) as f:
                report_data = json.load(f)

            assert "summary" in report_data
            assert "error_history" in report_data
            assert report_data["summary"]["total_errors"] == 3
        finally:
            Path(report_path).unlink()

    def test_clear_error_history(self):
        """Test clearing error history."""
        assert len(self.handler.error_history) == 3
        assert self.handler.error_count == 3

        self.handler.clear_error_history()

        assert len(self.handler.error_history) == 0
        assert self.handler.error_count == 0
        assert self.handler.warning_count == 0


class TestErrorHandlerIntegration:
    """Test integration with other system components."""

    def test_integration_with_conversion_result(self):
        """Test integration with ConversionResult."""
        handler = ErrorHandler()
        error = ProcessingError("Integration test error")

        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("output.html")],
            processing_time=2.5,
            warnings=["Existing warning"],
        )

        updated_result = handler.handle_error(error, "integration_test", result=result)

        assert updated_result.success is False
        assert len(updated_result.errors) == 1
        assert "integration test error" in updated_result.errors[0].lower()
        assert len(updated_result.warnings) == 1  # Existing warning preserved
        assert updated_result.processing_time == 2.5  # Other fields preserved

    def test_logging_integration(self):
        """Test integration with logging system."""
        custom_logger = logging.getLogger("test_error_handler")
        handler = ErrorHandler(logger=custom_logger)

        with patch.object(custom_logger, "error") as mock_error:
            with patch.object(custom_logger, "warning") as mock_warning:
                # Test error logging
                error = ConversionError("Test error")
                handler.handle_error(error, "test")
                mock_error.assert_called_once()

                # Test warning logging
                warning = ValidationError("Test warning")
                handler.handle_warning(warning, "test")
                mock_warning.assert_called_once()

    def test_context_propagation(self):
        """Test that context information is properly propagated."""
        handler = ErrorHandler()
        error = ProcessingError("Context test error", stage="generation")
        context = "template_processing"

        result = handler.handle_error(error, context)

        error_record = handler.error_history[0]
        assert error_record["context"] == context
        assert error_record["error"].stage == "generation"


# Fixtures for pytest


@pytest.fixture
def error_handler():
    """Create an error handler for testing."""
    return ErrorHandler()


@pytest.fixture
def sample_errors():
    """Sample errors for testing."""
    return [
        ValidationError("Invalid input format"),
        ProcessingError("Template not found", stage="generation"),
        FileError("Permission denied", file_path="/test/file.md"),
        ConfigurationError("Invalid config", config_path="/test/config.yaml"),
        ConversionError("Conversion failed", stage="parsing"),
    ]


@pytest.fixture
def error_handler_with_history(sample_errors):
    """Create error handler with sample error history."""
    handler = ErrorHandler()
    for i, error in enumerate(sample_errors):
        handler.handle_error(error, f"context_{i}")
    return handler


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return MagicMock(spec=logging.Logger)
