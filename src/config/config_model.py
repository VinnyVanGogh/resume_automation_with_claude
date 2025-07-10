"""
Configuration data models for the resume automation system.

This module defines Pydantic models for all configuration sections,
integrating with existing component configurations while providing
a unified YAML-based configuration system.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..formatter.config import ATSConfig
from ..generator.config import OutputConfig


class ATSRulesConfig(BaseModel):
    """
    Configuration for ATS optimization rules and keyword emphasis.
    
    Extends the existing ATSConfig with additional YAML-configurable options.
    """
    
    max_line_length: int = Field(default=80, ge=1, le=200, description="Maximum line length for ATS compatibility")
    bullet_style: str = Field(default="•", description="Bullet point style ('•', '-', '*')")
    section_order: List[str] = Field(
        default_factory=lambda: ["contact", "summary", "experience", "education", "skills", "projects", "certifications"],
        description="Preferred order of resume sections"
    )
    optimize_keywords: bool = Field(default=True, description="Whether to optimize keyword density")
    remove_special_chars: bool = Field(default=True, description="Whether to remove ATS-unfriendly characters")
    keyword_emphasis: Dict[str, float] = Field(
        default_factory=lambda: {
            "technical_skills": 1.5,
            "soft_skills": 1.2,
            "industry_terms": 1.3,
            "certifications": 1.4
        },
        description="Keyword emphasis weights by category"
    )
    formatting_rules: Dict[str, Any] = Field(
        default_factory=lambda: {
            "use_standard_fonts": True,
            "avoid_tables": True,
            "use_simple_bullets": True,
            "standard_date_format": True
        },
        description="ATS formatting rules"
    )
    
    @field_validator('bullet_style')
    @classmethod
    def validate_bullet_style(cls, v: str) -> str:
        """Validate bullet style is ATS-friendly."""
        allowed_styles = ["•", "-", "*"]
        if v not in allowed_styles:
            raise ValueError(f"Bullet style must be one of: {allowed_styles}")
        return v
    
    def to_ats_config(self) -> ATSConfig:
        """Convert to existing ATSConfig format for backward compatibility."""
        return ATSConfig(
            max_line_length=self.max_line_length,
            bullet_style=self.bullet_style,
            section_order=self.section_order,
            optimize_keywords=self.optimize_keywords,
            remove_special_chars=self.remove_special_chars
        )


class OutputFormatsConfig(BaseModel):
    """
    Configuration for output format preferences (PDF, HTML, DOCX).
    
    Extends the existing OutputConfig with additional YAML-configurable options.
    """
    
    enabled_formats: List[str] = Field(
        default_factory=lambda: ["html", "pdf", "docx"],
        description="List of output formats to generate"
    )
    
    # HTML Configuration
    html_theme: str = Field(default="professional", description="HTML theme (professional, modern, minimal, tech)")
    html_include_styles: bool = Field(default=True, description="Include CSS inline in HTML")
    html_meta_description: str = Field(default="Professional resume", description="HTML meta description")
    
    # PDF Configuration  
    pdf_page_size: str = Field(default="Letter", description="PDF page size (Letter, A4, Legal)")
    pdf_margins: Dict[str, float] = Field(
        default_factory=lambda: {"top": 0.75, "bottom": 0.75, "left": 0.75, "right": 0.75},
        description="PDF margins in inches"
    )
    pdf_optimize_size: bool = Field(default=True, description="Optimize PDF for smaller file size")
    
    # DOCX Configuration
    docx_template: str = Field(default="professional", description="DOCX template (professional, modern, minimal, tech)")
    docx_margins: Dict[str, float] = Field(
        default_factory=lambda: {"top": 0.75, "bottom": 0.75, "left": 0.75, "right": 0.75},
        description="DOCX margins in inches"
    )
    docx_line_spacing: float = Field(default=1.15, description="DOCX line spacing multiplier")
    
    # General Output Settings
    output_directory: str = Field(default="output", description="Output directory for generated files")
    filename_prefix: str = Field(default="resume", description="Prefix for generated filenames")
    overwrite_existing: bool = Field(default=True, description="Whether to overwrite existing files")
    
    @field_validator('enabled_formats')
    @classmethod
    def validate_enabled_formats(cls, v: List[str]) -> List[str]:
        """Validate enabled formats are supported."""
        supported_formats = ["html", "pdf", "docx"]
        for fmt in v:
            if fmt not in supported_formats:
                raise ValueError(f"Unsupported format: {fmt}. Supported formats: {supported_formats}")
        return v
    
    @field_validator('pdf_page_size')
    @classmethod
    def validate_pdf_page_size(cls, v: str) -> str:
        """Validate PDF page size."""
        allowed_sizes = ["Letter", "A4", "Legal"]
        if v not in allowed_sizes:
            raise ValueError(f"PDF page size must be one of: {allowed_sizes}")
        return v
    
    def to_output_config(self) -> OutputConfig:
        """Convert to existing OutputConfig format for backward compatibility."""
        from ..generator.config import HTMLConfig, PDFConfig, DOCXConfig
        
        return OutputConfig(
            html=HTMLConfig(
                theme=self.html_theme,
                include_styles=self.html_include_styles,
                meta_description=self.html_meta_description
            ),
            pdf=PDFConfig(
                page_size=self.pdf_page_size,
                margin_top=self.pdf_margins["top"],
                margin_bottom=self.pdf_margins["bottom"],
                margin_left=self.pdf_margins["left"],
                margin_right=self.pdf_margins["right"],
                optimize_size=self.pdf_optimize_size
            ),
            docx=DOCXConfig(
                template_name=self.docx_template,
                line_spacing=self.docx_line_spacing,
                margin_top=self.docx_margins["top"],
                margin_bottom=self.docx_margins["bottom"],
                margin_left=self.docx_margins["left"],
                margin_right=self.docx_margins["right"]
            ),
            output_dir=Path(self.output_directory),
            filename_prefix=self.filename_prefix,
            overwrite_existing=self.overwrite_existing
        )


class StylingConfig(BaseModel):
    """
    Configuration for font settings, themes, and styling options.
    """
    
    font_family: str = Field(default="Arial", description="Primary font family")
    font_size: int = Field(default=11, ge=6, le=24, description="Base font size in points")
    font_weight: str = Field(default="normal", description="Font weight (normal, bold)")
    
    # Theme Configuration
    theme: str = Field(default="professional", description="Overall theme (professional, modern, minimal, tech)")
    color_scheme: Dict[str, str] = Field(
        default_factory=lambda: {
            "primary": "#000000",
            "secondary": "#333333", 
            "accent": "#0066cc",
            "background": "#ffffff"
        },
        description="Color scheme for the resume"
    )
    
    # Spacing Configuration
    section_spacing: int = Field(default=12, description="Spacing between sections in points")
    line_height: float = Field(default=1.15, description="Line height multiplier")
    paragraph_spacing: int = Field(default=6, description="Spacing between paragraphs in points")
    
    # Layout Configuration
    layout_style: str = Field(default="single_column", description="Layout style (single_column, two_column)")
    header_style: str = Field(default="centered", description="Header style (centered, left_aligned, right_aligned)")
    
    @field_validator('font_weight')
    @classmethod
    def validate_font_weight(cls, v: str) -> str:
        """Validate font weight."""
        allowed_weights = ["normal", "bold", "light"]
        if v not in allowed_weights:
            raise ValueError(f"Font weight must be one of: {allowed_weights}")
        return v
    
    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """Validate theme selection."""
        allowed_themes = ["professional", "modern", "minimal", "tech"]
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {allowed_themes}")
        return v


class ProcessingConfig(BaseModel):
    """
    Configuration for batch processing and performance settings.
    """
    
    batch_size: int = Field(default=1, ge=1, le=1000, description="Number of resumes to process in parallel")
    max_workers: int = Field(default=1, ge=1, le=32, description="Maximum number of worker threads")
    timeout_seconds: int = Field(default=300, description="Timeout for processing individual resumes")
    
    # Validation Settings
    validate_input: bool = Field(default=True, description="Whether to validate input markdown")
    validate_output: bool = Field(default=True, description="Whether to validate generated output")
    strict_validation: bool = Field(default=False, description="Whether to use strict validation mode")
    
    # Performance Settings
    cache_templates: bool = Field(default=True, description="Whether to cache compiled templates")
    optimize_images: bool = Field(default=True, description="Whether to optimize images in output")
    
    @field_validator('batch_size')
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """Validate batch size is positive."""
        if v < 1:
            raise ValueError("Batch size must be at least 1")
        return v
    
    @field_validator('max_workers')
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        """Validate max workers is positive."""
        if v < 1:
            raise ValueError("Max workers must be at least 1")
        return v


class LoggingConfig(BaseModel):
    """
    Configuration for logging settings.
    """
    
    level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file_path: Optional[str] = Field(default=None, description="Path to log file (None for console only)")
    max_file_size: int = Field(default=10485760, description="Maximum log file size in bytes (10MB)")
    backup_count: int = Field(default=3, description="Number of backup log files to keep")
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate logging level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Logging level must be one of: {allowed_levels}")
        return v.upper()


class Config(BaseModel):
    """
    Root configuration model combining all configuration sections.
    
    This is the main configuration class that integrates all component
    configurations and provides a unified interface for YAML-based configuration.
    """
    
    ats_rules: ATSRulesConfig = Field(default_factory=ATSRulesConfig, description="ATS optimization rules")
    output_formats: OutputFormatsConfig = Field(default_factory=OutputFormatsConfig, description="Output format preferences")
    styling: StylingConfig = Field(default_factory=StylingConfig, description="Font and styling settings")
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig, description="Processing and performance settings")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    
    # Metadata
    version: str = Field(default="1.0", description="Configuration version")
    created_by: str = Field(default="resume-automation", description="Configuration creator")
    
    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True  # Validate on assignment
    )
        
    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization validation and setup.
        
        Args:
            __context: Pydantic context (unused)
        """
        # Ensure output directory exists
        output_dir = Path(self.output_formats.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_ats_config(self) -> ATSConfig:
        """Get backward-compatible ATSConfig instance."""
        return self.ats_rules.to_ats_config()
    
    def get_output_config(self) -> OutputConfig:
        """Get backward-compatible OutputConfig instance."""
        return self.output_formats.to_output_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """
        Create Config instance from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Config: Configured instance
        """
        return cls(**config_dict)