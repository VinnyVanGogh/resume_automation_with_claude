"""
Shared type definitions for resume automation.
This module contains common data types, exceptions, and type aliases
used throughout the resume automation package.
"""
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Result of validating resume content or structure.

    Args:
        valid: Whether the validation passed.
        errors: List of error messages if validation failed.
        warnings: List of warning messages for non-critical issues.

    Returns:
        ValidationResult: Validation result with status and messages.
    """
    valid: bool
    errors: list[str]
    warnings: list[str] | None = None


class ResumeConversionError(Exception):
    """
    Base exception for resume conversion errors.

    This is the base class for all resume automation related exceptions.
    All specific exceptions should inherit from this class.
    """
    pass


class InvalidMarkdownError(ResumeConversionError):
    """
    Raised when markdown structure is invalid.

    This exception is raised when the input markdown does not conform
    to the expected resume format or contains structural issues.
    """
    pass


class ATSComplianceError(ResumeConversionError):
    """
    Raised when output fails ATS compliance checks.

    This exception is raised when the generated output does not meet
    ATS (Applicant Tracking System) requirements or formatting standards.
    """
    pass
