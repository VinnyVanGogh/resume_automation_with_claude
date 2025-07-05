"""
Resume Automation Package.

A Python-based resume conversion pipeline that transforms Markdown-formatted
resumes into multiple ATS-optimized formats (PDF, DOCX, HTML).
"""

__version__ = "0.1.0"
__author__ = "Resume Automation Team"

from .formatter import ATSFormatter
from .generator import ResumeGenerator
from .parser import MarkdownResumeParser
from .custom_types import (
    ATSComplianceError,
    InvalidMarkdownError,
    ResumeConversionError,
    ValidationResult,
)

__all__ = [
    "MarkdownResumeParser",
    "ATSFormatter",
    "ResumeGenerator",
    "ValidationResult",
    "ResumeConversionError",
    "InvalidMarkdownError",
    "ATSComplianceError",
]
