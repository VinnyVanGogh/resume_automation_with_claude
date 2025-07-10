"""
Tests for configuration validator functionality.

Tests ValidationResult class and ConfigValidator methods for comprehensive
validation of configuration settings with detailed error reporting.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from ..config_validator import ConfigValidator, ValidationResult
from ..config_model import (
    Config,
    ATSRulesConfig,
    OutputFormatsConfig,
    StylingConfig,
    ProcessingConfig,
    LoggingConfig
)


class TestValidationResult:
    """Test ValidationResult class functionality."""
    
    def test_initialization_defaults(self):
        """Test ValidationResult initialization with defaults."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
    
    def test_initialization_with_values(self):
        """Test ValidationResult initialization with custom values."""
        errors = ["Error 1", "Error 2"]
        warnings = ["Warning 1"]
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        assert result.is_valid is False
        assert result.errors == errors
        assert result.warnings == warnings
    
    def test_add_error(self):
        """Test adding errors to validation result."""
        result = ValidationResult()
        assert result.is_valid is True
        
        result.add_error("Test error")
        assert result.is_valid is False
        assert "Test error" in result.errors
        assert len(result.errors) == 1
    
    def test_add_warning(self):
        """Test adding warnings to validation result."""
        result = ValidationResult()
        assert result.is_valid is True
        
        result.add_warning("Test warning")
        assert result.is_valid is True  # Warnings don't affect validity
        assert "Test warning" in result.warnings
        assert len(result.warnings) == 1
    
    def test_merge_valid_results(self):
        """Test merging two valid results."""
        result1 = ValidationResult()
        result1.add_warning("Warning 1")
        
        result2 = ValidationResult()
        result2.add_warning("Warning 2")
        
        result1.merge(result2)
        assert result1.is_valid is True
        assert len(result1.warnings) == 2
        assert "Warning 1" in result1.warnings
        assert "Warning 2" in result1.warnings
    
    def test_merge_with_invalid_result(self):
        """Test merging with an invalid result."""
        result1 = ValidationResult()
        result1.add_warning("Warning 1")
        
        result2 = ValidationResult()
        result2.add_error("Error 1")
        result2.add_warning("Warning 2")
        
        result1.merge(result2)
        assert result1.is_valid is False
        assert len(result1.errors) == 1
        assert len(result1.warnings) == 2
        assert "Error 1" in result1.errors
        assert "Warning 1" in result1.warnings
        assert "Warning 2" in result1.warnings
    
    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")
        
        result_dict = result.to_dict()
        expected = {
            "is_valid": False,
            "errors": ["Error 1"],
            "warnings": ["Warning 1", "Warning 2"],
            "error_count": 1,
            "warning_count": 2
        }
        assert result_dict == expected
    
    def test_str_valid_no_warnings(self):
        """Test string representation for valid result with no warnings."""
        result = ValidationResult()
        assert str(result) == "Validation passed successfully"
    
    def test_str_invalid_with_errors(self):
        """Test string representation for invalid result with errors."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_error("Error 2")
        
        result_str = str(result)
        assert "Validation failed with 2 error(s)" in result_str
        assert "ERROR: Error 1" in result_str
        assert "ERROR: Error 2" in result_str
    
    def test_str_valid_with_warnings(self):
        """Test string representation for valid result with warnings."""
        result = ValidationResult()
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")
        
        result_str = str(result)
        assert "Validation completed with 2 warning(s)" in result_str
        assert "WARNING: Warning 1" in result_str
        assert "WARNING: Warning 2" in result_str
    
    def test_str_invalid_with_errors_and_warnings(self):
        """Test string representation for invalid result with both errors and warnings."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        
        result_str = str(result)
        assert "Validation failed with 1 error(s)" in result_str
        assert "Validation completed with 1 warning(s)" in result_str
        assert "ERROR: Error 1" in result_str
        assert "WARNING: Warning 1" in result_str


class TestConfigValidator:
    """Test ConfigValidator class functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ConfigValidator initialization."""
        validator = ConfigValidator()
        assert validator.logger is not None
    
    def test_validate_full_config_with_config_object(self):
        """Test validating a complete Config object."""
        config = Config()
        result = self.validator.validate_full_config(config)
        
        assert isinstance(result, ValidationResult)
        # Should be valid since we're using defaults
        assert result.is_valid is True
    
    def test_validate_full_config_with_valid_dict(self):
        """Test validating a valid configuration dictionary."""
        config_dict = {
            "ats_rules": {"max_line_length": 80},
            "output_formats": {"enabled_formats": ["html"]},
            "styling": {"theme": "professional"},
            "processing": {"batch_size": 10},
            "logging": {"level": "INFO"}
        }
        
        result = self.validator.validate_full_config(config_dict)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
    
    def test_validate_full_config_with_invalid_dict(self):
        """Test validating an invalid configuration dictionary."""
        config_dict = {
            "ats_rules": {"max_line_length": "invalid"}  # Should be int
        }
        
        result = self.validator.validate_full_config(config_dict)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Configuration model validation failed" in result.errors[0]


class TestATSRulesValidation:
    """Test ATS rules validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_validate_ats_rules_default(self):
        """Test validating default ATS rules."""
        config = ATSRulesConfig()
        result = self.validator.validate_ats_rules(config)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_ats_rules_short_line_length(self):
        """Test validation with very short line length."""
        config = ATSRulesConfig(max_line_length=30)
        result = self.validator.validate_ats_rules(config)
        
        assert result.is_valid is True  # Warning doesn't make invalid
        assert len(result.warnings) > 0
        assert any("Very short line length" in warning for warning in result.warnings)
    
    def test_validate_ats_rules_long_line_length(self):
        """Test validation with very long line length."""
        config = ATSRulesConfig(max_line_length=150)
        result = self.validator.validate_ats_rules(config)
        
        assert result.is_valid is True  # Warning doesn't make invalid
        assert len(result.warnings) > 0
        assert any("Very long line length" in warning for warning in result.warnings)
    
    def test_validate_ats_rules_invalid_bullet_style(self):
        """Test validation with invalid bullet style using model_construct."""
        # Use model_construct to bypass Pydantic validation for testing validator logic
        config = ATSRulesConfig.model_construct(bullet_style="☆")
        result = self.validator.validate_ats_rules(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("not ATS-friendly" in error for error in result.errors)
    
    def test_validate_ats_rules_valid_bullet_styles(self):
        """Test validation with valid bullet styles."""
        valid_styles = ["•", "-", "*", "▪", "◦"]
        
        for style in valid_styles:
            config = ATSRulesConfig.model_construct(bullet_style=style)
            result = self.validator.validate_ats_rules(config)
            assert result.is_valid is True
    
    def test_validate_ats_rules_missing_sections(self):
        """Test validation with missing recommended sections."""
        config = ATSRulesConfig(section_order=["contact", "experience"])
        result = self.validator.validate_ats_rules(config)
        
        assert result.is_valid is True  # Warning doesn't make invalid
        assert len(result.warnings) > 0
        assert any("Missing recommended sections" in warning for warning in result.warnings)
    
    def test_validate_ats_rules_wrong_first_section(self):
        """Test validation with contact not being first section."""
        config = ATSRulesConfig(section_order=["summary", "contact", "experience"])
        result = self.validator.validate_ats_rules(config)
        
        assert result.is_valid is True  # Warning doesn't make invalid
        assert len(result.warnings) > 0
        assert any("Contact section should typically be first" in warning for warning in result.warnings)
    
    def test_validate_ats_rules_empty_section_order(self):
        """Test validation with empty section order."""
        config = ATSRulesConfig(section_order=[])
        result = self.validator.validate_ats_rules(config)
        
        # Should have warnings for missing sections but no error for empty first section
        assert result.is_valid is True
        assert len(result.warnings) > 0


class TestOutputFormatsValidation:
    """Test output formats validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_validate_output_formats_default(self):
        """Test validating default output formats."""
        config = OutputFormatsConfig()
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_output_formats_empty_enabled_formats(self):
        """Test validation with no enabled formats."""
        config = OutputFormatsConfig(enabled_formats=[])
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("At least one output format must be enabled" in error for error in result.errors)
    
    def test_validate_output_formats_unsupported_format(self):
        """Test validation with unsupported format using model_construct."""
        config = OutputFormatsConfig.model_construct(enabled_formats=["xml"])
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Unsupported output format: xml" in error for error in result.errors)
    
    def test_validate_output_formats_invalid_html_theme(self):
        """Test validation with invalid HTML theme."""
        config = OutputFormatsConfig(html_theme="invalid_theme")
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Unsupported HTML theme: invalid_theme" in error for error in result.errors)
    
    def test_validate_output_formats_invalid_pdf_page_size(self):
        """Test validation with invalid PDF page size using model_construct."""
        config = OutputFormatsConfig.model_construct(
            enabled_formats=["pdf"], 
            pdf_page_size="Tabloid"
        )
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Unsupported PDF page size: Tabloid" in error for error in result.errors)
    
    def test_validate_output_formats_pdf_margins_out_of_range(self):
        """Test validation with PDF margins out of range."""
        config = OutputFormatsConfig(
            enabled_formats=["pdf"],
            pdf_margins={"top": 3.0, "bottom": 0.1, "left": 1.0, "right": 1.0}
        )
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("margin" in warning and "outside recommended range" in warning 
                  for warning in result.warnings)
    
    def test_validate_output_formats_invalid_docx_template(self):
        """Test validation with invalid DOCX template using model_construct."""
        config = OutputFormatsConfig.model_construct(
            enabled_formats=["docx"],
            docx_template="invalid_template"
        )
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Unsupported DOCX template: invalid_template" in error for error in result.errors)
    
    def test_validate_output_formats_docx_line_spacing_out_of_range(self):
        """Test validation with DOCX line spacing out of range."""
        config = OutputFormatsConfig(
            enabled_formats=["docx"],
            docx_line_spacing=3.0
        )
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("DOCX line spacing" in warning and "outside recommended range" in warning 
                  for warning in result.warnings)
    
    def test_validate_output_formats_invalid_output_directory(self):
        """Test validation with invalid output directory."""
        # Create a file instead of directory
        test_file = self.temp_dir / "test_file.txt"
        test_file.write_text("test")
        
        config = OutputFormatsConfig.model_construct(output_directory=str(test_file))
        result = self.validator.validate_output_formats(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("not a directory" in error for error in result.errors)
    
    def test_validate_output_formats_bad_path_format(self):
        """Test validation with badly formatted path."""
        # Use an invalid path that would cause an exception on some systems
        # On macOS, \x00 might not trigger the exception, so let's use a different approach
        from unittest.mock import patch
        
        config = OutputFormatsConfig.model_construct(output_directory="/some/invalid/path")
        
        # Mock Path in the config_validator module to raise an exception
        with patch('src.config.config_validator.Path') as mock_path:
            mock_path.side_effect = Exception("Invalid path")
            result = self.validator.validate_output_formats(config)
            
            assert result.is_valid is False
            assert len(result.errors) > 0
            assert any("Invalid output directory path" in error for error in result.errors)


class TestStylingValidation:
    """Test styling validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_validate_styling_default(self):
        """Test validating default styling."""
        config = StylingConfig()
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_styling_invalid_theme(self):
        """Test validation with invalid theme using model_construct."""
        config = StylingConfig.model_construct(theme="invalid_theme")
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Unsupported theme: invalid_theme" in error for error in result.errors)
    
    def test_validate_styling_font_size_out_of_range(self):
        """Test validation with font size out of range."""
        # Test very small font
        config_small = StylingConfig(font_size=6)
        result_small = self.validator.validate_styling(config_small)
        
        assert result_small.is_valid is True  # Warnings don't make invalid
        assert len(result_small.warnings) > 0
        assert any("font size" in warning and "outside recommended range" in warning 
                  for warning in result_small.warnings)
        
        # Test very large font
        config_large = StylingConfig(font_size=20)
        result_large = self.validator.validate_styling(config_large)
        
        assert result_large.is_valid is True
        assert len(result_large.warnings) > 0
        assert any("font size" in warning and "outside recommended range" in warning 
                  for warning in result_large.warnings)
    
    def test_validate_styling_non_ats_friendly_font(self):
        """Test validation with non-ATS-friendly font."""
        config = StylingConfig(font_family="Comic Sans MS")
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("may not be ATS-friendly" in warning for warning in result.warnings)
    
    def test_validate_styling_ats_friendly_fonts(self):
        """Test validation with ATS-friendly fonts."""
        ats_fonts = ["Arial", "Helvetica", "Times New Roman", "Calibri", "Georgia"]
        
        for font in ats_fonts:
            config = StylingConfig(font_family=font)
            result = self.validator.validate_styling(config)
            # Should not have font warnings for ATS-friendly fonts
            font_warnings = [w for w in result.warnings if "ATS-friendly" in w]
            assert len(font_warnings) == 0
    
    def test_validate_styling_invalid_font_weight(self):
        """Test validation with invalid font weight using model_construct."""
        config = StylingConfig.model_construct(font_weight="extra-bold")
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Invalid font weight: extra-bold" in error for error in result.errors)
    
    def test_validate_styling_invalid_hex_colors(self):
        """Test validation with invalid hex colors."""
        config = StylingConfig(
            color_scheme={
                "primary": "not-a-color",
                "secondary": "#12345",  # Too short
                "accent": "#GGGGGG"     # Invalid hex
            }
        )
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is False
        assert len(result.errors) >= 3
        color_errors = [e for e in result.errors if "Invalid hex color" in e]
        assert len(color_errors) == 3
    
    def test_validate_styling_valid_hex_colors(self):
        """Test validation with valid hex colors."""
        config = StylingConfig(
            color_scheme={
                "primary": "#123456",
                "secondary": "#ABCDEF",
                "accent": "#000000"
            }
        )
        result = self.validator.validate_styling(config)
        
        # Should not have color errors for valid hex colors
        color_errors = [e for e in result.errors if "Invalid hex color" in e]
        assert len(color_errors) == 0
    
    def test_validate_styling_section_spacing_out_of_range(self):
        """Test validation with section spacing out of range."""
        config = StylingConfig(section_spacing=100)
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Section spacing" in warning and "outside recommended range" in warning 
                  for warning in result.warnings)
    
    def test_validate_styling_line_height_out_of_range(self):
        """Test validation with line height out of range."""
        config = StylingConfig(line_height=4.0)
        result = self.validator.validate_styling(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Line height" in warning and "outside recommended range" in warning 
                  for warning in result.warnings)


class TestProcessingValidation:
    """Test processing validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_validate_processing_default(self):
        """Test validating default processing config."""
        config = ProcessingConfig()
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_processing_invalid_batch_size(self):
        """Test validation with invalid batch size using model_construct."""
        config = ProcessingConfig.model_construct(batch_size=0)
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Batch size must be at least 1" in error for error in result.errors)
    
    def test_validate_processing_large_batch_size(self):
        """Test validation with large batch size."""
        config = ProcessingConfig(batch_size=150)
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Large batch size" in warning for warning in result.warnings)
    
    def test_validate_processing_invalid_max_workers(self):
        """Test validation with invalid max workers using model_construct."""
        config = ProcessingConfig.model_construct(max_workers=0)
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Max workers must be at least 1" in error for error in result.errors)
    
    def test_validate_processing_high_max_workers(self):
        """Test validation with high max workers count."""
        config = ProcessingConfig(max_workers=32)
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("High worker count" in warning for warning in result.warnings)
    
    def test_validate_processing_short_timeout(self):
        """Test validation with short timeout."""
        config = ProcessingConfig(timeout_seconds=10)
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Short timeout" in warning for warning in result.warnings)
    
    def test_validate_processing_long_timeout(self):
        """Test validation with very long timeout."""
        config = ProcessingConfig(timeout_seconds=3600)  # 1 hour
        result = self.validator.validate_processing(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Very long timeout" in warning for warning in result.warnings)


class TestLoggingValidation:
    """Test logging validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_validate_logging_default(self):
        """Test validating default logging config."""
        config = LoggingConfig()
        result = self.validator.validate_logging(config)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_logging_invalid_level(self):
        """Test validation with invalid log level using model_construct."""
        config = LoggingConfig.model_construct(level="INVALID")
        result = self.validator.validate_logging(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Invalid log level: INVALID" in error for error in result.errors)
    
    def test_validate_logging_valid_levels(self):
        """Test validation with valid log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = LoggingConfig(level=level)
            result = self.validator.validate_logging(config)
            assert result.is_valid is True
            
        # Test case insensitive
        config = LoggingConfig(level="info")
        result = self.validator.validate_logging(config)
        assert result.is_valid is True
    
    def test_validate_logging_existing_non_file(self):
        """Test validation with log path that exists but is not a file."""
        # Create a directory instead of file
        log_dir = self.temp_dir / "log_dir"
        log_dir.mkdir()
        
        config = LoggingConfig(file_path=str(log_dir))
        result = self.validator.validate_logging(config)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("not a file" in error for error in result.errors)
    
    def test_validate_logging_invalid_file_path(self):
        """Test validation with invalid file path."""
        # Mock Path to raise an exception for invalid path
        from unittest.mock import patch
        
        config = LoggingConfig.model_construct(file_path="/some/invalid/path")
        
        # Mock Path in the config_validator module to raise an exception
        with patch('src.config.config_validator.Path') as mock_path:
            mock_path.side_effect = Exception("Invalid path")
            result = self.validator.validate_logging(config)
            
            assert result.is_valid is False
            assert len(result.errors) > 0
            assert any("Invalid log file path" in error for error in result.errors)
    
    def test_validate_logging_valid_file_path(self):
        """Test validation with valid file path."""
        log_file = self.temp_dir / "test.log"
        config = LoggingConfig(file_path=str(log_file))
        result = self.validator.validate_logging(config)
        
        assert result.is_valid is True
        # Parent directory should be created
        assert log_file.parent.exists()
    
    def test_validate_logging_small_max_file_size(self):
        """Test validation with very small max file size."""
        config = LoggingConfig(max_file_size=512)  # 0.5KB
        result = self.validator.validate_logging(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Very small max file size" in warning for warning in result.warnings)
    
    def test_validate_logging_large_max_file_size(self):
        """Test validation with very large max file size."""
        config = LoggingConfig(max_file_size=2147483648)  # 2GB
        result = self.validator.validate_logging(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Very large max file size" in warning for warning in result.warnings)


class TestCrossSectionValidation:
    """Test cross-section validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_validate_cross_sections_consistent_themes(self):
        """Test validation with consistent themes across sections."""
        config = Config(
            styling=StylingConfig(theme="modern"),
            output_formats=OutputFormatsConfig(
                html_theme="modern",
                docx_template="modern"
            )
        )
        result = self.validator._validate_cross_sections(config)
        
        assert result.is_valid is True
        # Should not have theme consistency warnings
        theme_warnings = [w for w in result.warnings if "inconsistent" in w and "theme" in w]
        assert len(theme_warnings) == 0
    
    def test_validate_cross_sections_inconsistent_themes(self):
        """Test validation with inconsistent themes across sections."""
        config = Config(
            styling=StylingConfig(theme="modern"),
            output_formats=OutputFormatsConfig(
                html_theme="professional",
                docx_template="minimal"
            )
        )
        result = self.validator._validate_cross_sections(config)
        
        assert result.is_valid is True  # Warnings don't make invalid
        assert len(result.warnings) > 0
        assert any("Theme settings are inconsistent" in warning for warning in result.warnings)


class TestHexColorValidation:
    """Test hex color validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_is_valid_hex_color_valid_colors(self):
        """Test validation with valid hex colors."""
        valid_colors = [
            "#000000", "#FFFFFF", "#123456", "#ABCDEF",
            "#abcdef", "#789ABC", "#FF0000", "#00FF00"
        ]
        
        for color in valid_colors:
            assert self.validator._is_valid_hex_color(color) is True
    
    def test_is_valid_hex_color_invalid_colors(self):
        """Test validation with invalid hex colors."""
        invalid_colors = [
            "000000",        # Missing #
            "#12345",        # Too short
            "#1234567",      # Too long
            "#GGGGGG",       # Invalid hex characters
            "#12345G",       # Mixed valid/invalid
            "",              # Empty string
            None,            # Not a string
            123456,          # Not a string
            "#12 345",       # Contains space
        ]
        
        for color in invalid_colors:
            assert self.validator._is_valid_hex_color(color) is False


class TestConfigFileValidation:
    """Test config file validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_validate_config_file_not_exists(self):
        """Test validation with non-existent file."""
        non_existent_file = self.temp_dir / "non_existent.yaml"
        result = self.validator.validate_config_file(non_existent_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("does not exist" in error for error in result.errors)
    
    def test_validate_config_file_valid_file(self):
        """Test validation with valid config file."""
        config_file = self.temp_dir / "valid_config.yaml"
        config_file.write_text("""
version: "1.0"
ats_rules:
  max_line_length: 80
  bullet_style: "•"
output_formats:
  enabled_formats: ["html"]
""")
        
        result = self.validator.validate_config_file(config_file)
        assert result.is_valid is True
    
    def test_validate_config_file_invalid_yaml(self):
        """Test validation with invalid YAML file."""
        config_file = self.temp_dir / "invalid_config.yaml"
        config_file.write_text("""
invalid: yaml: content:
  - missing closing bracket
""")
        
        result = self.validator.validate_config_file(config_file)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Failed to load configuration file" in error for error in result.errors)
    
    def test_validate_config_file_string_path(self):
        """Test validation with string file path."""
        config_file = self.temp_dir / "string_path_config.yaml"
        config_file.write_text("""
version: "1.0"
""")
        
        result = self.validator.validate_config_file(str(config_file))
        assert result.is_valid is True


class TestIntegrationScenarios:
    """Test complex integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()
    
    def test_complex_invalid_config(self):
        """Test validation with multiple errors and warnings using model_construct."""
        # Create a config with multiple validation issues using model_construct
        # to bypass Pydantic validation and test validator business logic
        
        ats_config = ATSRulesConfig.model_construct(
            max_line_length=30,  # Warning: too short
            bullet_style="☆",    # Error: invalid style
            section_order=["summary", "contact"]  # Warning: wrong order
        )
        
        output_config = OutputFormatsConfig.model_construct(
            enabled_formats=[],  # Error: empty
            html_theme="invalid"  # Error: invalid theme
        )
        
        styling_config = StylingConfig.model_construct(
            theme="different",   # Error: invalid theme
            font_size=5,         # Warning: too small
            font_weight="extra", # Error: invalid weight
            color_scheme={
                "primary": "red"    # Error: invalid hex
            }
        )
        
        processing_config = ProcessingConfig.model_construct(
            batch_size=0,        # Error: invalid
            max_workers=50       # Warning: too many
        )
        
        logging_config = LoggingConfig.model_construct(
            level="TRACE",       # Error: invalid level
            max_file_size=100    # Warning: too small
        )
        
        config = Config.model_construct(
            ats_rules=ats_config,
            output_formats=output_config,
            styling=styling_config,
            processing=processing_config,
            logging=logging_config
        )
        
        result = self.validator.validate_full_config(config)
        
        # Should be invalid due to multiple errors
        assert result.is_valid is False
        # Should have multiple errors and warnings
        assert len(result.errors) >= 6
        assert len(result.warnings) >= 4
    
    def test_all_warnings_scenario(self):
        """Test validation with only warnings (still valid)."""
        config = Config(
            ats_rules=ATSRulesConfig(
                max_line_length=30,  # Warning
                section_order=["summary", "contact", "experience"]  # Warning
            ),
            styling=StylingConfig(
                font_size=6,  # Warning
                font_family="Comic Sans MS",  # Warning
                section_spacing=60,  # Warning
                line_height=4.0  # Warning
            ),
            processing=ProcessingConfig(
                batch_size=150,  # Warning
                max_workers=20,  # Warning
                timeout_seconds=10  # Warning
            ),
            logging=LoggingConfig(
                max_file_size=100  # Warning
            )
        )
        
        result = self.validator.validate_full_config(config)
        
        # Should be valid despite warnings
        assert result.is_valid is True
        # Should have multiple warnings
        assert len(result.warnings) >= 8
        assert len(result.errors) == 0