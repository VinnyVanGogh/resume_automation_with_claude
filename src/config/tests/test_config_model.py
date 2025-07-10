"""
Tests for configuration data models.

Tests Pydantic models, validation, and conversion methods.
"""

import pytest
from pydantic import ValidationError
from pydantic_core import ValidationError as PydanticCoreValidationError

from ..config_model import (
    Config,
    ATSRulesConfig,
    OutputFormatsConfig,
    StylingConfig,
    ProcessingConfig,
    LoggingConfig
)


class TestATSRulesConfig:
    """Test ATS rules configuration model."""
    
    def test_default_creation(self):
        """Test creating ATS config with defaults."""
        config = ATSRulesConfig()
        assert config.max_line_length == 80
        assert config.bullet_style == "•"
        assert config.optimize_keywords is True
        assert config.remove_special_chars is True
        assert "contact" in config.section_order
        assert "summary" in config.section_order
    
    def test_custom_values(self):
        """Test creating ATS config with custom values."""
        config = ATSRulesConfig(
            max_line_length=75,
            bullet_style="-",
            optimize_keywords=False,
            section_order=["contact", "experience", "skills"]
        )
        assert config.max_line_length == 75
        assert config.bullet_style == "-"
        assert config.optimize_keywords is False
        assert config.section_order == ["contact", "experience", "skills"]
    
    def test_bullet_style_validation(self):
        """Test bullet style validation."""
        # Valid styles
        for style in ["•", "-", "*"]:
            config = ATSRulesConfig(bullet_style=style)
            assert config.bullet_style == style
        
        # Invalid style should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            ATSRulesConfig(bullet_style="☆")
    
    def test_to_ats_config(self):
        """Test conversion to legacy ATSConfig."""
        config = ATSRulesConfig(
            max_line_length=70,
            bullet_style="-",
            optimize_keywords=False
        )
        legacy_config = config.to_ats_config()
        
        assert legacy_config.max_line_length == 70
        assert legacy_config.bullet_style == "-"
        assert legacy_config.optimize_keywords is False


class TestOutputFormatsConfig:
    """Test output formats configuration model."""
    
    def test_default_creation(self):
        """Test creating output config with defaults."""
        config = OutputFormatsConfig()
        assert "html" in config.enabled_formats
        assert "pdf" in config.enabled_formats
        assert "docx" in config.enabled_formats
        assert config.html_theme == "professional"
        assert config.pdf_page_size == "Letter"
    
    def test_format_validation(self):
        """Test enabled formats validation."""
        # Valid formats
        config = OutputFormatsConfig(enabled_formats=["html", "pdf"])
        assert config.enabled_formats == ["html", "pdf"]
        
        # Invalid format should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            OutputFormatsConfig(enabled_formats=["xml"])
    
    def test_pdf_page_size_validation(self):
        """Test PDF page size validation."""
        # Valid sizes
        for size in ["Letter", "A4", "Legal"]:
            config = OutputFormatsConfig(pdf_page_size=size)
            assert config.pdf_page_size == size
        
        # Invalid size should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            OutputFormatsConfig(pdf_page_size="Tabloid")
    
    def test_to_output_config(self):
        """Test conversion to legacy OutputConfig."""
        config = OutputFormatsConfig(
            html_theme="modern",
            pdf_page_size="A4",
            docx_template="minimal"
        )
        legacy_config = config.to_output_config()
        
        assert legacy_config.html.theme == "modern"
        assert legacy_config.pdf.page_size == "A4"
        assert legacy_config.docx.template_name == "minimal"


class TestStylingConfig:
    """Test styling configuration model."""
    
    def test_default_creation(self):
        """Test creating styling config with defaults."""
        config = StylingConfig()
        assert config.font_family == "Arial"
        assert config.font_size == 11
        assert config.font_weight == "normal"
        assert config.theme == "professional"
        assert config.line_height == 1.15
    
    def test_theme_validation(self):
        """Test theme validation."""
        # Valid themes
        for theme in ["professional", "modern", "minimal", "tech"]:
            config = StylingConfig(theme=theme)
            assert config.theme == theme
        
        # Invalid theme should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            StylingConfig(theme="rainbow")
    
    def test_font_weight_validation(self):
        """Test font weight validation."""
        # Valid weights
        for weight in ["normal", "bold", "light"]:
            config = StylingConfig(font_weight=weight)
            assert config.font_weight == weight
        
        # Invalid weight should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            StylingConfig(font_weight="ultra-bold")
    
    def test_color_scheme(self):
        """Test color scheme configuration."""
        config = StylingConfig(
            color_scheme={
                "primary": "#000000",
                "secondary": "#333333",
                "accent": "#0066cc",
                "background": "#ffffff"
            }
        )
        assert config.color_scheme["primary"] == "#000000"
        assert config.color_scheme["accent"] == "#0066cc"


class TestProcessingConfig:
    """Test processing configuration model."""
    
    def test_default_creation(self):
        """Test creating processing config with defaults."""
        config = ProcessingConfig()
        assert config.batch_size == 1
        assert config.max_workers == 1
        assert config.timeout_seconds == 300
        assert config.validate_input is True
        assert config.cache_templates is True
    
    def test_batch_size_validation(self):
        """Test batch size validation."""
        # Valid batch size
        config = ProcessingConfig(batch_size=5)
        assert config.batch_size == 5
        
        # Invalid batch size should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            ProcessingConfig(batch_size=0)
    
    def test_max_workers_validation(self):
        """Test max workers validation."""
        # Valid max workers
        config = ProcessingConfig(max_workers=4)
        assert config.max_workers == 4
        
        # Invalid max workers should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            ProcessingConfig(max_workers=0)


class TestLoggingConfig:
    """Test logging configuration model."""
    
    def test_default_creation(self):
        """Test creating logging config with defaults."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.file_path is None
        assert config.max_file_size == 10485760  # 10MB
        assert config.backup_count == 3
    
    def test_level_validation(self):
        """Test logging level validation."""
        # Valid levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = LoggingConfig(level=level)
            assert config.level == level
        
        # Invalid level should raise validation error
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            LoggingConfig(level="TRACE")
    
    def test_level_normalization(self):
        """Test logging level case normalization."""
        config = LoggingConfig(level="debug")
        assert config.level == "DEBUG"


class TestConfig:
    """Test main configuration model."""
    
    def test_default_creation(self):
        """Test creating main config with defaults."""
        config = Config()
        assert isinstance(config.ats_rules, ATSRulesConfig)
        assert isinstance(config.output_formats, OutputFormatsConfig)
        assert isinstance(config.styling, StylingConfig)
        assert isinstance(config.processing, ProcessingConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert config.version == "1.0"
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "ats_rules": {
                "max_line_length": 75,
                "bullet_style": "-"
            },
            "output_formats": {
                "enabled_formats": ["html", "pdf"],
                "html_theme": "modern"
            },
            "styling": {
                "theme": "minimal",
                "font_size": 12
            }
        }
        
        config = Config.from_dict(config_dict)
        assert config.ats_rules.max_line_length == 75
        assert config.ats_rules.bullet_style == "-"
        assert config.output_formats.html_theme == "modern"
        assert config.styling.theme == "minimal"
        assert config.styling.font_size == 12
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "ats_rules" in config_dict
        assert "output_formats" in config_dict
        assert "styling" in config_dict
        assert "processing" in config_dict
        assert "logging" in config_dict
        assert "version" in config_dict
    
    def test_get_ats_config(self):
        """Test getting legacy ATS config."""
        config = Config()
        config.ats_rules.max_line_length = 90
        config.ats_rules.bullet_style = "*"
        
        ats_config = config.get_ats_config()
        assert ats_config.max_line_length == 90
        assert ats_config.bullet_style == "*"
    
    def test_get_output_config(self):
        """Test getting legacy output config."""
        config = Config()
        config.output_formats.html_theme = "tech"
        config.output_formats.pdf_page_size = "A4"
        
        output_config = config.get_output_config()
        assert output_config.html.theme == "tech"
        assert output_config.pdf.page_size == "A4"
    
    def test_model_post_init(self):
        """Test post-initialization setup."""
        config = Config()
        config.output_formats.output_directory = "test_output"
        
        # Call post_init manually since it's called during construction
        config.model_post_init(None)
        
        # Verify output directory would be created (we can't test actual creation in unit tests)
        assert config.output_formats.output_directory == "test_output"


class TestConfigurationValidation:
    """Test configuration validation scenarios."""
    
    def test_invalid_configuration_raises_error(self):
        """Test that invalid configurations raise appropriate errors."""
        # Invalid ATS rules
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            Config.from_dict({
                "ats_rules": {
                    "max_line_length": -10  # Invalid negative value
                }
            })
        
        # Invalid output formats
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            Config.from_dict({
                "output_formats": {
                    "enabled_formats": ["xml"]  # Unsupported format
                }
            })
        
        # Invalid styling
        with pytest.raises((ValidationError, PydanticCoreValidationError)):
            Config.from_dict({
                "styling": {
                    "theme": "nonexistent"  # Invalid theme
                }
            })
    
    def test_partial_configuration_uses_defaults(self):
        """Test that partial configurations use defaults for missing values."""
        config = Config.from_dict({
            "ats_rules": {
                "max_line_length": 75
            }
        })
        
        # Should use provided value
        assert config.ats_rules.max_line_length == 75
        
        # Should use defaults for missing values
        assert config.ats_rules.bullet_style == "•"
        assert config.styling.theme == "professional"
        assert config.processing.batch_size == 1