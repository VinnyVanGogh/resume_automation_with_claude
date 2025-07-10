"""
Configuration validator for comprehensive validation of configuration settings.

This module provides detailed validation of configuration sections with
specific error messages and validation results for debugging.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from pydantic import ValidationError

from .config_model import (
    Config,
    ATSRulesConfig,
    OutputFormatsConfig,
    StylingConfig,
    ProcessingConfig,
    LoggingConfig
)


logger = logging.getLogger(__name__)


class ValidationResult:
    """
    Container for validation results with detailed error information.
    """
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None, 
                 warnings: Optional[List[str]] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            errors: List of error messages
            warnings: List of warning messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
    
    def __str__(self) -> str:
        """String representation of validation result."""
        if self.is_valid and not self.warnings:
            return "Validation passed successfully"
        
        result = []
        if not self.is_valid:
            result.append(f"Validation failed with {len(self.errors)} error(s)")
            for error in self.errors:
                result.append(f"  ERROR: {error}")
        
        if self.warnings:
            result.append(f"Validation completed with {len(self.warnings)} warning(s)")
            for warning in self.warnings:
                result.append(f"  WARNING: {warning}")
        
        return "\n".join(result)


class ConfigValidator:
    """
    Comprehensive configuration validator with detailed error reporting.
    
    Provides section-specific validation methods and overall configuration
    validation with helpful error messages and warnings.
    """
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.logger = logging.getLogger(__name__)
    
    def validate_full_config(self, config: Union[Config, Dict[str, Any]]) -> ValidationResult:
        """
        Validate complete configuration.
        
        Args:
            config: Configuration instance or dictionary
            
        Returns:
            ValidationResult: Comprehensive validation result
        """
        result = ValidationResult()
        
        # Convert dict to Config if needed
        if isinstance(config, dict):
            try:
                config_obj = Config.from_dict(config)
            except ValidationError as e:
                result.add_error(f"Configuration model validation failed: {e}")
                return result
        else:
            config_obj = config
        
        # Validate each section
        ats_result = self.validate_ats_rules(config_obj.ats_rules)
        result.merge(ats_result)
        
        output_result = self.validate_output_formats(config_obj.output_formats)
        result.merge(output_result)
        
        styling_result = self.validate_styling(config_obj.styling)
        result.merge(styling_result)
        
        processing_result = self.validate_processing(config_obj.processing)
        result.merge(processing_result)
        
        logging_result = self.validate_logging(config_obj.logging)
        result.merge(logging_result)
        
        # Cross-section validation
        cross_result = self._validate_cross_sections(config_obj)
        result.merge(cross_result)
        
        self.logger.info(f"Configuration validation completed: {result.is_valid}")
        return result
    
    def validate_ats_rules(self, ats_config: ATSRulesConfig) -> ValidationResult:
        """
        Validate ATS rules configuration.
        
        Args:
            ats_config: ATS rules configuration
            
        Returns:
            ValidationResult: ATS validation result
        """
        result = ValidationResult()
        
        # Validate line length
        if ats_config.max_line_length < 40:
            result.add_warning("Very short line length may cause formatting issues")
        elif ats_config.max_line_length > 120:
            result.add_warning("Very long line length may not be ATS-friendly")
        
        # Validate bullet style
        ats_friendly_bullets = ["•", "-", "*", "▪", "◦"]
        if ats_config.bullet_style not in ats_friendly_bullets:
            result.add_error(f"Bullet style '{ats_config.bullet_style}' is not ATS-friendly. "
                           f"Use one of: {', '.join(ats_friendly_bullets)}")
        
        # Validate section order
        required_sections = ["contact", "summary", "experience", "education", "skills"]
        missing_sections = [s for s in required_sections if s not in ats_config.section_order]
        if missing_sections:
            result.add_warning(f"Missing recommended sections: {', '.join(missing_sections)}")
        
        # Validate contact section is first
        if ats_config.section_order and ats_config.section_order[0] != "contact":
            result.add_warning("Contact section should typically be first for ATS compatibility")
        
        # Validate keyword emphasis settings
        if hasattr(ats_config, 'keyword_emphasis'):
            for category, weight in ats_config.keyword_emphasis.items():
                if weight < 0.5 or weight > 3.0:
                    result.add_warning(f"Keyword emphasis weight {weight} for '{category}' "
                                     f"is outside recommended range (0.5-3.0)")
        
        return result
    
    def validate_output_formats(self, output_config: OutputFormatsConfig) -> ValidationResult:
        """
        Validate output formats configuration.
        
        Args:
            output_config: Output formats configuration
            
        Returns:
            ValidationResult: Output formats validation result
        """
        result = ValidationResult()
        
        # Validate enabled formats
        if not output_config.enabled_formats:
            result.add_error("At least one output format must be enabled")
        
        supported_formats = ["html", "pdf", "docx"]
        for fmt in output_config.enabled_formats:
            if fmt not in supported_formats:
                result.add_error(f"Unsupported output format: {fmt}")
        
        # Validate themes
        supported_themes = ["professional", "modern", "minimal", "tech"]
        if output_config.html_theme not in supported_themes:
            result.add_error(f"Unsupported HTML theme: {output_config.html_theme}")
        
        # Validate PDF settings
        if "pdf" in output_config.enabled_formats:
            if output_config.pdf_page_size not in ["Letter", "A4", "Legal"]:
                result.add_error(f"Unsupported PDF page size: {output_config.pdf_page_size}")
            
            # Check margins
            for margin_name, margin_value in output_config.pdf_margins.items():
                if margin_value < 0.25 or margin_value > 2.0:
                    result.add_warning(f"PDF {margin_name} margin {margin_value} is outside "
                                     f"recommended range (0.25-2.0 inches)")
        
        # Validate DOCX settings
        if "docx" in output_config.enabled_formats:
            if output_config.docx_template not in supported_themes:
                result.add_error(f"Unsupported DOCX template: {output_config.docx_template}")
            
            if output_config.docx_line_spacing < 0.8 or output_config.docx_line_spacing > 2.5:
                result.add_warning(f"DOCX line spacing {output_config.docx_line_spacing} "
                                 f"is outside recommended range (0.8-2.5)")
        
        # Validate output directory
        try:
            output_path = Path(output_config.output_directory)
            if output_path.exists() and not output_path.is_dir():
                result.add_error(f"Output path exists but is not a directory: {output_config.output_directory}")
        except Exception as e:
            result.add_error(f"Invalid output directory path: {e}")
        
        return result
    
    def validate_styling(self, styling_config: StylingConfig) -> ValidationResult:
        """
        Validate styling configuration.
        
        Args:
            styling_config: Styling configuration
            
        Returns:
            ValidationResult: Styling validation result
        """
        result = ValidationResult()
        
        # Validate theme
        supported_themes = ["professional", "modern", "minimal", "tech"]
        if styling_config.theme not in supported_themes:
            result.add_error(f"Unsupported theme: {styling_config.theme}")
        
        # Validate font sizes
        if styling_config.font_size < 8 or styling_config.font_size > 16:
            result.add_warning(f"Base font size {styling_config.font_size} is outside "
                             f"recommended range (8-16 points)")
        
        # Validate font family
        ats_friendly_fonts = [
            "Arial", "Helvetica", "Times New Roman", "Calibri", 
            "Georgia", "Verdana", "Trebuchet MS"
        ]
        if styling_config.font_family not in ats_friendly_fonts:
            result.add_warning(f"Font '{styling_config.font_family}' may not be ATS-friendly. "
                             f"Consider using: {', '.join(ats_friendly_fonts[:3])}")
        
        # Validate font weight
        if styling_config.font_weight not in ["normal", "bold", "light"]:
            result.add_error(f"Invalid font weight: {styling_config.font_weight}")
        
        # Validate color scheme
        for color_name, color_value in styling_config.color_scheme.items():
            if not self._is_valid_hex_color(color_value):
                result.add_error(f"Invalid hex color for {color_name}: {color_value}")
        
        # Validate spacing values
        if styling_config.section_spacing < 0 or styling_config.section_spacing > 50:
            result.add_warning(f"Section spacing {styling_config.section_spacing} is outside "
                             f"recommended range (0-50 points)")
        
        if styling_config.line_height < 0.8 or styling_config.line_height > 3.0:
            result.add_warning(f"Line height {styling_config.line_height} is outside "
                             f"recommended range (0.8-3.0)")
        
        return result
    
    def validate_processing(self, processing_config: ProcessingConfig) -> ValidationResult:
        """
        Validate processing configuration.
        
        Args:
            processing_config: Processing configuration
            
        Returns:
            ValidationResult: Processing validation result
        """
        result = ValidationResult()
        
        # Validate batch size
        if processing_config.batch_size < 1:
            result.add_error("Batch size must be at least 1")
        elif processing_config.batch_size > 100:
            result.add_warning("Large batch size may consume significant memory")
        
        # Validate max workers
        if processing_config.max_workers < 1:
            result.add_error("Max workers must be at least 1")
        elif processing_config.max_workers > 16:
            result.add_warning("High worker count may not improve performance")
        
        # Validate timeout
        if processing_config.timeout_seconds < 30:
            result.add_warning("Short timeout may cause failures for complex resumes")
        elif processing_config.timeout_seconds > 1800:  # 30 minutes
            result.add_warning("Very long timeout may mask performance issues")
        
        return result
    
    def validate_logging(self, logging_config: LoggingConfig) -> ValidationResult:
        """
        Validate logging configuration.
        
        Args:
            logging_config: Logging configuration
            
        Returns:
            ValidationResult: Logging validation result
        """
        result = ValidationResult()
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if logging_config.level.upper() not in valid_levels:
            result.add_error(f"Invalid log level: {logging_config.level}")
        
        # Validate log file path
        if logging_config.file_path:
            try:
                log_path = Path(logging_config.file_path)
                if log_path.exists() and not log_path.is_file():
                    result.add_error(f"Log path exists but is not a file: {logging_config.file_path}")
                
                # Check if parent directory exists or can be created
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                result.add_error(f"Invalid log file path: {e}")
        
        # Validate file size limits
        if logging_config.max_file_size < 1024:  # 1KB minimum
            result.add_warning("Very small max file size may cause frequent log rotation")
        elif logging_config.max_file_size > 1073741824:  # 1GB maximum
            result.add_warning("Very large max file size may consume significant disk space")
        
        return result
    
    def _validate_cross_sections(self, config: Config) -> ValidationResult:
        """
        Validate cross-section dependencies and consistency.
        
        Args:
            config: Complete configuration
            
        Returns:
            ValidationResult: Cross-section validation result
        """
        result = ValidationResult()
        
        # Check theme consistency
        if (config.styling.theme != config.output_formats.html_theme or
            config.styling.theme != config.output_formats.docx_template):
            result.add_warning("Theme settings are inconsistent across sections")
        
        # Check font consistency
        if hasattr(config.output_formats, 'pdf') and hasattr(config.output_formats.pdf, 'font_family'):
            if config.styling.font_family != config.output_formats.pdf.font_family:
                result.add_warning("Font family settings are inconsistent between styling and PDF output")
        
        # Check margin consistency
        styling_margins = config.styling.page_margins if hasattr(config.styling, 'page_margins') else None
        if styling_margins and hasattr(config.output_formats, 'pdf_margins'):
            pdf_margins = config.output_formats.pdf_margins
            for margin_name in ['top', 'bottom', 'left', 'right']:
                if (margin_name in styling_margins and 
                    margin_name in pdf_margins and
                    abs(styling_margins[margin_name] - pdf_margins[margin_name]) > 0.01):
                    result.add_warning("Margin settings are inconsistent between styling and PDF output")
                    break
        
        return result
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """
        Validate hex color format.
        
        Args:
            color: Color string to validate
            
        Returns:
            bool: True if valid hex color
        """
        if not isinstance(color, str) or not color.startswith('#'):
            return False
        
        if len(color) != 7:
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def validate_config_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a configuration file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            ValidationResult: File validation result
        """
        result = ValidationResult()
        file_path = Path(file_path)
        
        if not file_path.exists():
            result.add_error(f"Configuration file does not exist: {file_path}")
            return result
        
        try:
            from .config_loader import ConfigLoader
            loader = ConfigLoader()
            config = loader.load_config(file_path)
            return self.validate_full_config(config)
        except Exception as e:
            result.add_error(f"Failed to load configuration file: {e}")
            return result