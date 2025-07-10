"""
Resume Converter Module.

This module provides the main ResumeConverter class that orchestrates the complete
resume conversion pipeline from markdown input to multiple output formats.

Main Classes:
    ResumeConverter: Main converter class for orchestrating the pipeline
    ConversionResult: Result object for single conversions
    BatchConversionResult: Result object for batch conversions

Main Functions:
    convert_resume: Convenience function for simple conversions
"""

from .exceptions import (
    ConversionError,
    ProcessingError,
    ValidationError,
)
from .resume_converter import ResumeConverter
from .types import (
    BatchConversionResult,
    ConversionResult,
    ProgressCallback,
)


# Convenience function for simple usage
def convert_resume(
    input_path: str, output_dir: str = "output", config_path: str = None
) -> ConversionResult:
    """
    Convenience function for simple resume conversion.

    Args:
        input_path: Path to markdown resume file
        output_dir: Output directory for generated files
        config_path: Optional path to configuration file

    Returns:
        ConversionResult: Result of the conversion operation
    """
    converter = ResumeConverter(config_path=config_path)
    return converter.convert(input_path, output_dir=output_dir)


__all__ = [
    "ResumeConverter",
    "ConversionResult",
    "BatchConversionResult",
    "ProgressCallback",
    "ConversionError",
    "ValidationError",
    "ProcessingError",
    "convert_resume",
]
