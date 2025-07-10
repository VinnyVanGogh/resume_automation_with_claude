"""
Core data structures and types for the resume converter module.

This module defines the fundamental data structures, protocols, and exceptions
used throughout the converter pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Any
from datetime import datetime


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
    output_files: List[Path] = field(default_factory=list)
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def output_count(self) -> int:
        """Number of output files generated."""
        return len(self.output_files)
    
    def add_warning(self, message: str) -> None:
        """Add a warning message to the result."""
        self.warnings.append(message)
    
    def add_error(self, message: str) -> None:
        """Add an error message and mark conversion as failed."""
        self.errors.append(message)
        self.success = False


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
    results: List[ConversionResult] = field(default_factory=list)
    total_processing_time: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_files / self.total_files) * 100
    
    def add_result(self, result: ConversionResult) -> None:
        """Add an individual conversion result to the batch."""
        self.results.append(result)
        if result.success:
            self.successful_files += 1
        else:
            self.failed_files += 1


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
        metadata: Optional[Dict[str, Any]] = None
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


# Import exceptions from separate module
from .exceptions import ConversionError, ValidationError, ProcessingError


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
    formats: List[str] = field(default_factory=lambda: ["html", "pdf", "docx"])
    output_dir: Optional[Path] = None
    filename_prefix: Optional[str] = None
    overwrite_existing: bool = True
    validate_output: bool = True
    parallel_processing: bool = True


@dataclass
class ProcessingStage:
    """
    Information about a processing stage.
    
    Attributes:
        name: Stage name (e.g., "parsing", "formatting")
        description: Human-readable description
        weight: Relative weight for progress calculation
        started_at: Timestamp when stage started
        completed_at: Timestamp when stage completed
    """
    name: str
    description: str
    weight: float = 1.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Duration of stage in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_completed(self) -> bool:
        """Whether the stage has completed."""
        return self.completed_at is not None