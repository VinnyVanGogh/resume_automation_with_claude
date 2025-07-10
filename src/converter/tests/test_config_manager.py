"""
Unit tests for the ConverterConfigManager class.

Tests configuration loading, validation, merging, runtime overrides,
and integration with the existing configuration system.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from ..config_manager import ConverterConfigManager
from ..exceptions import ConfigurationError


class TestConverterConfigManagerInitialization:
    """Test ConverterConfigManager initialization and setup."""

    def test_default_initialization(self):
        """Test config manager with default configuration."""
        config_manager = ConverterConfigManager()

        assert config_manager is not None
        assert config_manager.config is not None
        assert config_manager.config_path is None
        assert hasattr(config_manager.config, "ats_rules")
        assert hasattr(config_manager.config, "output_formats")
        assert hasattr(config_manager.config, "styling")
        assert hasattr(config_manager.config, "processing")

    def test_initialization_with_config_path(self):
        """Test config manager with custom configuration file."""
        # Create temporary config file
        config_content = {
            "version": "1.0",
            "ats_rules": {"max_line_length": 85, "bullet_style": "-"},
            "output_formats": {
                "enabled_formats": ["html", "pdf"],
                "html_theme": "modern",
            },
            "styling": {"theme": "modern", "font_size": 12},
            "processing": {"max_workers": 6, "validate_input": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_content, f)
            config_path = f.name

        try:
            config_manager = ConverterConfigManager(config_path=config_path)

            assert config_manager.config_path == Path(config_path)
            assert config_manager.config.ats_rules.max_line_length == 85
            assert config_manager.config.ats_rules.bullet_style == "-"
            assert config_manager.config.output_formats.html_theme == "modern"
            assert config_manager.config.styling.theme == "modern"
            assert config_manager.config.processing.max_workers == 6
        finally:
            Path(config_path).unlink()

    def test_initialization_with_nonexistent_config(self):
        """Test config manager with non-existent configuration file."""
        with pytest.raises(ConfigurationError):
            ConverterConfigManager(config_path="/nonexistent/config.yaml")

    def test_initialization_with_invalid_yaml(self):
        """Test config manager with invalid YAML file."""
        # Create invalid YAML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_config_path = f.name

        try:
            with pytest.raises(ConfigurationError):
                ConverterConfigManager(config_path=invalid_config_path)
        finally:
            Path(invalid_config_path).unlink()


class TestConverterConfigManagerOverrides:
    """Test configuration override functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_manager = ConverterConfigManager()
        self.original_max_line_length = (
            self.config_manager.config.ats_rules.max_line_length
        )
        self.original_theme = self.config_manager.config.styling.theme

    def test_simple_override(self):
        """Test simple configuration override."""
        overrides = {"ats_rules.max_line_length": 100}

        self.config_manager.update_config_overrides(overrides)

        assert self.config_manager.config.ats_rules.max_line_length == 100
        assert self.config_manager.config.styling.theme == self.original_theme

    def test_multiple_overrides(self):
        """Test multiple configuration overrides."""
        overrides = {
            "ats_rules.max_line_length": 95,
            "ats_rules.bullet_style": "*",
            "styling.theme": "minimal",
            "styling.font_size": 14,
            "processing.max_workers": 8,
        }

        self.config_manager.update_config_overrides(overrides)

        assert self.config_manager.config.ats_rules.max_line_length == 95
        assert self.config_manager.config.ats_rules.bullet_style == "*"
        assert self.config_manager.config.styling.theme == "minimal"
        assert self.config_manager.config.styling.font_size == 14
        assert self.config_manager.config.processing.max_workers == 8

    def test_nested_override(self):
        """Test nested configuration override."""
        overrides = {
            "output_formats.enabled_formats": ["html"],
            "output_formats.html_theme": "tech",
        }

        self.config_manager.update_config_overrides(overrides)

        assert self.config_manager.config.output_formats.enabled_formats == ["html"]
        assert self.config_manager.config.output_formats.html_theme == "tech"

    def test_invalid_override_key(self):
        """Test invalid configuration override key."""
        overrides = {"nonexistent.section.key": "value"}

        with pytest.raises(ConfigurationError):
            self.config_manager.update_config_overrides(overrides)

    def test_invalid_override_value(self):
        """Test invalid configuration override value."""
        overrides = {"ats_rules.max_line_length": "not_a_number"}

        with pytest.raises(ConfigurationError):
            self.config_manager.update_config_overrides(overrides)

    def test_override_type_validation(self):
        """Test type validation for overrides."""
        # Test string override
        overrides = {"ats_rules.bullet_style": "•"}
        self.config_manager.update_config_overrides(overrides)
        assert self.config_manager.config.ats_rules.bullet_style == "•"

        # Test integer override
        overrides = {"styling.font_size": 13}
        self.config_manager.update_config_overrides(overrides)
        assert self.config_manager.config.styling.font_size == 13

        # Test boolean override
        overrides = {"processing.validate_input": False}
        self.config_manager.update_config_overrides(overrides)
        assert self.config_manager.config.processing.validate_input is False

        # Test list override
        overrides = {"output_formats.enabled_formats": ["pdf", "docx"]}
        self.config_manager.update_config_overrides(overrides)
        assert self.config_manager.config.output_formats.enabled_formats == [
            "pdf",
            "docx",
        ]

    def test_clear_overrides(self):
        """Test clearing configuration overrides."""
        # Apply overrides
        overrides = {"ats_rules.max_line_length": 100, "styling.theme": "minimal"}
        self.config_manager.update_config_overrides(overrides)

        assert self.config_manager.config.ats_rules.max_line_length == 100
        assert self.config_manager.config.styling.theme == "minimal"

        # Clear overrides
        self.config_manager.clear_overrides()

        assert (
            self.config_manager.config.ats_rules.max_line_length
            == self.original_max_line_length
        )
        assert self.config_manager.config.styling.theme == self.original_theme


class TestConverterConfigManagerUtilities:
    """Test utility methods of ConverterConfigManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_manager = ConverterConfigManager()

    def test_get_config_summary(self):
        """Test getting configuration summary."""
        summary = self.config_manager.get_config_summary()

        assert isinstance(summary, dict)
        assert "ats_rules" in summary
        assert "output_formats" in summary
        assert "styling" in summary
        assert "processing" in summary

        # Verify structure
        assert "max_line_length" in summary["ats_rules"]
        assert "bullet_style" in summary["ats_rules"]
        assert "enabled_formats" in summary["output_formats"]
        assert "theme" in summary["styling"]
        assert "max_workers" in summary["processing"]

    def test_validate_config(self):
        """Test configuration validation."""
        # Default config should be valid
        is_valid, errors = self.config_manager.validate_config()
        assert is_valid is True
        assert len(errors) == 0

        # Test with invalid override
        try:
            invalid_overrides = {"ats_rules.max_line_length": -1}
            self.config_manager.update_config_overrides(invalid_overrides)

            is_valid, errors = self.config_manager.validate_config()
            assert is_valid is False
            assert len(errors) > 0
        except ConfigurationError:
            # Expected if validation happens during override
            pass

    def test_get_effective_config(self):
        """Test getting effective configuration with overrides."""
        # Get original config
        original_config = self.config_manager.get_effective_config()
        original_max_line = original_config.ats_rules.max_line_length

        # Apply overrides
        overrides = {"ats_rules.max_line_length": 120}
        self.config_manager.update_config_overrides(overrides)

        # Get effective config after overrides
        effective_config = self.config_manager.get_effective_config()

        assert effective_config.ats_rules.max_line_length == 120
        assert effective_config.ats_rules.max_line_length != original_max_line

    def test_export_config(self):
        """Test exporting configuration to file."""
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            output_path = f.name

        try:
            # Export config
            self.config_manager.export_config(output_path)

            # Verify file was created
            assert Path(output_path).exists()

            # Verify content
            with open(output_path) as f:
                exported_data = yaml.safe_load(f)

            assert "ats_rules" in exported_data
            assert "output_formats" in exported_data
            assert "styling" in exported_data
            assert "processing" in exported_data
        finally:
            Path(output_path).unlink()

    def test_reload_config(self):
        """Test reloading configuration from file."""
        # Create config file with specific values
        config_content = {
            "version": "1.0",
            "ats_rules": {"max_line_length": 77},
            "styling": {"theme": "tech"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_content, f)
            config_path = f.name

        try:
            # Create config manager with file
            config_manager = ConverterConfigManager(config_path=config_path)
            assert config_manager.config.ats_rules.max_line_length == 77

            # Modify file
            config_content["ats_rules"]["max_line_length"] = 88
            with open(config_path, "w") as f:
                yaml.dump(config_content, f)

            # Reload
            config_manager.reload_config()
            assert config_manager.config.ats_rules.max_line_length == 88
        finally:
            Path(config_path).unlink()


class TestConverterConfigManagerIntegration:
    """Test integration with existing configuration system."""

    @patch("src.converter.config_manager.ConfigLoader")
    def test_config_loader_integration(self, mock_config_loader):
        """Test integration with ConfigLoader."""
        # Mock config loader
        mock_loader_instance = MagicMock()
        mock_config_loader.return_value = mock_loader_instance

        mock_config = MagicMock()
        mock_loader_instance.load_config.return_value = mock_config

        # Create config manager
        config_manager = ConverterConfigManager()

        # Verify ConfigLoader was used
        mock_config_loader.assert_called_once()
        mock_loader_instance.load_config.assert_called_once()

    @patch("src.converter.config_manager.ConfigValidator")
    def test_config_validator_integration(self, mock_config_validator):
        """Test integration with ConfigValidator."""
        # Mock validator
        mock_validator_instance = MagicMock()
        mock_config_validator.return_value = mock_validator_instance

        mock_validation_result = MagicMock()
        mock_validation_result.is_valid = True
        mock_validation_result.errors = []
        mock_validator_instance.validate_full_config.return_value = (
            mock_validation_result
        )

        # Test validation
        config_manager = ConverterConfigManager()
        is_valid, errors = config_manager.validate_config()

        assert is_valid is True
        assert errors == []
        mock_config_validator.assert_called_once()

    def test_config_merging_behavior(self):
        """Test configuration merging behavior."""
        # Create base config file
        base_config = {
            "version": "1.0",
            "ats_rules": {"max_line_length": 80, "bullet_style": "•"},
            "styling": {"theme": "professional", "font_size": 11},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(base_config, f)
            config_path = f.name

        try:
            config_manager = ConverterConfigManager(config_path=config_path)

            # Apply partial overrides
            overrides = {"ats_rules.max_line_length": 90, "styling.font_size": 12}
            config_manager.update_config_overrides(overrides)

            # Verify merging behavior
            config = config_manager.config
            assert config.ats_rules.max_line_length == 90  # Overridden
            assert config.ats_rules.bullet_style == "•"  # Preserved
            assert config.styling.theme == "professional"  # Preserved
            assert config.styling.font_size == 12  # Overridden
        finally:
            Path(config_path).unlink()


class TestConverterConfigManagerErrorHandling:
    """Test error handling in ConverterConfigManager."""

    def test_file_permission_error(self):
        """Test handling of file permission errors."""
        # Create a directory instead of a file to cause permission error
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_config_path = Path(temp_dir) / "subdir"
            fake_config_path.mkdir()

            with pytest.raises(ConfigurationError):
                ConverterConfigManager(config_path=str(fake_config_path))

    def test_malformed_yaml_error(self):
        """Test handling of malformed YAML."""
        malformed_yaml = """
ats_rules:
  max_line_length: 80
  bullet_style: "•"
invalid_structure:
  - item1
  - item2
    nested_without_dash: value
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(malformed_yaml)
            config_path = f.name

        try:
            with pytest.raises(ConfigurationError):
                ConverterConfigManager(config_path=config_path)
        finally:
            Path(config_path).unlink()

    def test_schema_validation_error(self):
        """Test handling of schema validation errors."""
        invalid_config = {
            "version": "1.0",
            "ats_rules": {
                "max_line_length": "not_a_number",  # Should be int
                "bullet_style": 123,  # Should be string
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_config, f)
            config_path = f.name

        try:
            with pytest.raises(ConfigurationError):
                ConverterConfigManager(config_path=config_path)
        finally:
            Path(config_path).unlink()


# Fixtures for pytest


@pytest.fixture
def sample_config_content():
    """Sample configuration content for testing."""
    return {
        "version": "1.0",
        "ats_rules": {
            "max_line_length": 85,
            "bullet_style": "-",
            "section_order": [
                "contact",
                "summary",
                "experience",
                "education",
                "skills",
            ],
            "optimize_keywords": True,
        },
        "output_formats": {
            "enabled_formats": ["html", "pdf", "docx"],
            "html_theme": "professional",
            "output_directory": "output",
        },
        "styling": {"theme": "professional", "font_family": "Arial", "font_size": 11},
        "processing": {"batch_size": 10, "max_workers": 4, "validate_input": True},
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config_content):
    """Create a temporary configuration file for testing."""
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_content, f)
    return config_file


@pytest.fixture
def config_manager_with_file(temp_config_file):
    """Create a config manager with a temporary config file."""
    return ConverterConfigManager(config_path=str(temp_config_file))
