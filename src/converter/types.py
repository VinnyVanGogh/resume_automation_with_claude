"""
Core data structures and types for the resume converter module.

This module defines the fundamental data structures, protocols, and exceptions
used throughout the converter pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


@dataclass
class ConversionResult:
    """
    Result of a single resume conversion operation.

    Attributes:
        success: Whether the conversion completed successfully
        input_path: Path to the input resume file
        output_files: List of generated output file paths
        processing_time: Time taken for conversion in seconds
        warnings: List of warning messages
        errors: List of error messages
        metadata: Additional metadata about the conversion
    """

    success: bool
    input_path: Path
    output_files: list[Path] = field(default_factory=list)
    processing_time: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def output_count(self) -> int:
        """Number of output files generated."""
        return len(self.output_files)

    def add_error(self, error_message: str) -> None:
        """Add an error message to the result."""
        self.errors.append(error_message)

    def add_warning(self, warning_message: str) -> None:
        """Add a warning message to the result."""
        self.warnings.append(warning_message)


@dataclass
class BatchConversionResult:
    """
    Result of a batch resume conversion operation.

    Attributes:
        total_files: Total number of files processed
        successful_files: Number of successfully converted files
        failed_files: Number of files that failed conversion
        results: List of individual conversion results
        total_processing_time: Total time for batch processing
        summary: Summary statistics and metadata
    """

    total_files: int
    successful_files: int = 0
    failed_files: int = 0
    results: list[ConversionResult] = field(default_factory=list)
    total_processing_time: float = 0.0
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_files / self.total_files) * 100


class ProgressCallback(Protocol):
    """
    Protocol for progress tracking callbacks.

    Implementations of this protocol receive progress updates during
    conversion operations.
    """

    def __call__(
        self,
        stage: str,
        progress: float,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Called to report progress during conversion.

        Args:
            stage: Current processing stage (e.g., "parsing", "formatting")
            progress: Progress as percentage (0.0 to 100.0)
            message: Human-readable progress message
            metadata: Optional additional metadata
        """
        ...


@dataclass
class ConversionOptions:
    """
    Options for customizing conversion behavior.

    Attributes:
        formats: List of output formats to generate
        output_dir: Output directory for generated files
        filename_prefix: Custom prefix for output files
        overwrite_existing: Whether to overwrite existing files
        validate_output: Whether to validate generated outputs
        parallel_processing: Whether to use parallel processing for batch
    """

    formats: list[str] = field(default_factory=lambda: ["html", "pdf", "docx"])
    output_dir: Path | None = None
    filename_prefix: str | None = None
    overwrite_existing: bool = True
    validate_output: bool = True
    parallel_processing: bool = True


class ProcessingStage(Enum):
    """
    Enumeration of processing stages for resume conversion.

    Each stage represents a distinct phase in the conversion pipeline.
    """

    VALIDATION = "validation"
    PARSING = "parsing"
    FORMATTING = "formatting"
    GENERATION = "generation"
    VALIDATION_OUTPUT = "validation_output"
    COMPLETE = "complete"


@dataclass
class ProcessingStageInfo:
    """
    Represents a processing stage with metadata.

    Attributes:
        name: Stage name identifier
        description: Human-readable description
        weight: Relative weight for progress calculation (0.0-1.0)
    """

    name: str
    description: str
    weight: float = 0.0


@dataclass
class FileValidationMetrics:
    """
    Validation metrics for a single file.

    Attributes:
        file_path: Path to the validated file
        format_type: Detected file format (html, pdf, docx)
        file_size: File size in bytes
        is_valid: Whether the file passes validation
        content_score: Content quality score (0-100)
        ats_score: ATS compliance score (0-100)
        formatting_score: Formatting quality score (0-100)
        overall_score: Overall quality score (0-100)
        issues: List of validation issues found
        validation_details: Additional validation metadata
    """

    file_path: Path
    format_type: str
    file_size: int
    is_valid: bool
    content_score: float = 0.0
    ats_score: float = 0.0
    formatting_score: float = 0.0
    overall_score: float = 0.0
    issues: list[str] = field(default_factory=list)
    validation_details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """
    Comprehensive validation report for multiple files.

    Attributes:
        file_metrics: List of individual file validation metrics
        total_files: Total number of files validated
        valid_files: Number of files that passed validation
        invalid_files: Number of files that failed validation
        is_valid: Whether the overall validation passed
        summary: Summary statistics and analysis
        recommendations: List of improvement recommendations
    """

    file_metrics: list[FileValidationMetrics]
    total_files: int
    valid_files: int
    invalid_files: int
    is_valid: bool
    summary: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def export_to_file(self, file_path: str) -> None:
        """Export validation report to JSON file."""
        import json

        # Convert dataclasses to dict for JSON serialization
        report_data = {
            "summary": {
                "total_files": self.total_files,
                "valid_files": self.valid_files,
                "invalid_files": self.invalid_files,
                "is_valid": self.is_valid,
                **self.summary,
            },
            "file_metrics": [
                {
                    "file_path": str(metrics.file_path),
                    "format_type": metrics.format_type,
                    "file_size": metrics.file_size,
                    "is_valid": metrics.is_valid,
                    "content_score": metrics.content_score,
                    "ats_score": metrics.ats_score,
                    "formatting_score": metrics.formatting_score,
                    "overall_score": metrics.overall_score,
                    "issues": metrics.issues,
                    "validation_details": metrics.validation_details,
                }
                for metrics in self.file_metrics
            ],
            "recommendations": self.recommendations,
            "generated_at": datetime.now().isoformat(),
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
