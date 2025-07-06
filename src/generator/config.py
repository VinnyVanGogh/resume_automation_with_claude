"""
Output generation configuration for resume generators.

This module defines configuration classes for controlling the output
generation process across different formats.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class HTMLConfig(BaseModel):
    """
    Configuration for HTML output generation.
    
    Attributes:
        template_name: Name of the Jinja2 template file
        theme: CSS theme to apply (default, professional, modern)
        include_styles: Whether to include CSS inline or as external link
        meta_description: Description for HTML meta tag
        custom_css: Optional custom CSS to include
    """
    
    template_name: str = Field(default="resume.html", description="Template file name")
    theme: str = Field(default="professional", description="CSS theme to apply")
    include_styles: bool = Field(default=True, description="Include CSS inline")
    meta_description: str = Field(default="Professional resume", description="Meta description")
    custom_css: Optional[str] = Field(default=None, description="Custom CSS styles")


class PDFConfig(BaseModel):
    """
    Configuration for PDF output generation.
    
    Attributes:
        page_size: Page size for PDF (Letter, A4, Legal)
        margin_top: Top margin in inches
        margin_bottom: Bottom margin in inches
        margin_left: Left margin in inches
        margin_right: Right margin in inches
        font_family: Primary font family
        font_size: Base font size in points
        optimize_size: Whether to optimize for smaller file size
    """
    
    page_size: str = Field(default="Letter", description="Page size (Letter, A4, Legal)")
    margin_top: float = Field(default=0.75, description="Top margin in inches")
    margin_bottom: float = Field(default=0.75, description="Bottom margin in inches")
    margin_left: float = Field(default=0.75, description="Left margin in inches")
    margin_right: float = Field(default=0.75, description="Right margin in inches")
    font_family: str = Field(default="Arial", description="Primary font family")
    font_size: int = Field(default=11, description="Base font size in points")
    optimize_size: bool = Field(default=True, description="Optimize for file size")


class DOCXConfig(BaseModel):
    """
    Configuration for DOCX output generation.
    
    Attributes:
        style_template: Style template to use (professional, modern, classic)
        font_name: Primary font name
        font_size: Base font size in points
        line_spacing: Line spacing multiplier
        margin_top: Top margin in inches
        margin_bottom: Bottom margin in inches
        margin_left: Left margin in inches
        margin_right: Right margin in inches
        section_spacing: Spacing between sections in points
    """
    
    style_template: str = Field(default="professional", description="Style template")
    font_name: str = Field(default="Arial", description="Primary font name")
    font_size: int = Field(default=11, description="Base font size in points")
    line_spacing: float = Field(default=1.15, description="Line spacing multiplier")
    margin_top: float = Field(default=0.75, description="Top margin in inches")
    margin_bottom: float = Field(default=0.75, description="Bottom margin in inches")
    margin_left: float = Field(default=0.75, description="Left margin in inches")
    margin_right: float = Field(default=0.75, description="Right margin in inches")
    section_spacing: int = Field(default=12, description="Section spacing in points")


class OutputConfig(BaseModel):
    """
    Main configuration class for all output generators.
    
    Attributes:
        html: HTML generation configuration
        pdf: PDF generation configuration
        docx: DOCX generation configuration
        output_dir: Base directory for output files
        filename_prefix: Prefix for generated files
        overwrite_existing: Whether to overwrite existing files
        validate_output: Whether to validate generated output
    """
    
    html: HTMLConfig = Field(default_factory=HTMLConfig, description="HTML config")
    pdf: PDFConfig = Field(default_factory=PDFConfig, description="PDF config")
    docx: DOCXConfig = Field(default_factory=DOCXConfig, description="DOCX config")
    output_dir: Path = Field(default=Path("output"), description="Output directory")
    filename_prefix: str = Field(default="resume", description="File name prefix")
    overwrite_existing: bool = Field(default=True, description="Overwrite existing files")
    validate_output: bool = Field(default=True, description="Validate generated output")

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization validation and setup.
        
        Args:
            __context: Pydantic context (unused)
        """
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_output_path(self, format_type: str, custom_name: Optional[str] = None) -> Path:
        """
        Get the full output path for a specific format.
        
        Args:
            format_type: Output format (html, pdf, docx)
            custom_name: Custom filename (without extension)
            
        Returns:
            Path: Full path to output file
            
        Raises:
            ValueError: If format_type is not supported
        """
        if format_type not in ["html", "pdf", "docx"]:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        filename = custom_name or self.filename_prefix
        return self.output_dir / f"{filename}.{format_type}"

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "OutputConfig":
        """
        Create OutputConfig from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            OutputConfig: Configured instance
        """
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return self.model_dump()