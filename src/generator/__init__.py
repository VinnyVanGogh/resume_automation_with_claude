"""
Resume Generator Module.

This module provides functionality to generate resume outputs in multiple
formats (HTML, PDF, DOCX) from ATS-formatted resume data.
"""

from .html_generator import HTMLGenerator
from .pdf_generator import PDFGenerator
from .docx_generator import DOCXGenerator
from .config import OutputConfig

__version__ = "1.0.0"
__all__ = ["HTMLGenerator", "PDFGenerator", "DOCXGenerator", "OutputConfig"]