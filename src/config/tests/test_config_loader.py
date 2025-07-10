"""
Tests for configuration loader functionality.

Tests YAML loading, merging, validation, and error handling.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from ..config_loader import ConfigLoader, load_config_from_path, load_default_config
from ..config_model import Config


class TestConfigLoader:
    """Test configuration loader functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = ConfigLoader()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()
        assert loader.default_config_path.name == "default_config.yaml"
        assert loader._default_config_obj is None
        assert loader._default_config_dict is None
        
        # Test with custom default path
        custom_path = Path("custom_default.yaml")
        loader = ConfigLoader(custom_path)
        assert loader.default_config_path == custom_path
    
    def test_load_default_config_from_file(self):
        """Test loading default configuration from file."""
        # Create a test default config file
        default_config_data = {
            "version": "1.0",
            "ats_rules": {
                "max_line_length": 85,
                "bullet_style": "-"
            },
            "styling": {
                "theme": "modern"
            }
        }
        
        default_file = self.temp_dir / "default_config.yaml"
        with open(default_file, 'w') as f:
            yaml.dump(default_config_data, f)
        
        loader = ConfigLoader(default_file)
        config = loader.load_default_config()
        
        assert isinstance(config, Config)
        assert config.ats_rules.max_line_length == 85
        assert config.ats_rules.bullet_style == "-"
        assert config.styling.theme == "modern"
    
    def test_load_default_config_without_file(self):
        """Test loading default config when file doesn't exist."""
        non_existent_file = self.temp_dir / "nonexistent.yaml"
        loader = ConfigLoader(non_existent_file)
        
        config = loader.load_default_config()
        assert isinstance(config, Config)
        # Should use model defaults
        assert config.ats_rules.max_line_length == 80
        assert config.styling.theme == "professional"
    
    def test_load_config_success(self):
        """Test successful configuration loading."""
        config_data = {
            "version": "1.0",
            "ats_rules": {
                "max_line_length": 75,
                "bullet_style": "*"
            },
            "output_formats": {
                "enabled_formats": ["html", "pdf"],
                "html_theme": "minimal"
            }
        }
        
        config_file = self.temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = self.loader.load_config(config_file)
        
        assert isinstance(config, Config)
        assert config.ats_rules.max_line_length == 75
        assert config.ats_rules.bullet_style == "*"
        assert config.output_formats.html_theme == "minimal"
    
    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        non_existent_file = self.temp_dir / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            self.loader.load_config(non_existent_file)
    
    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML."""
        config_file = self.temp_dir / "invalid.yaml"
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        with pytest.raises(yaml.YAMLError):
            self.loader.load_config(config_file)
    
    def test_load_config_empty_file(self):
        """Test loading empty configuration file."""
        config_file = self.temp_dir / "empty.yaml"
        config_file.touch()  # Create empty file
        
        config = self.loader.load_config(config_file)
        assert isinstance(config, Config)
        # Should use all defaults
        assert config.ats_rules.max_line_length == 80
        assert config.styling.theme == "professional"
    
    def test_load_config_validation_error(self):
        """Test loading config with validation errors."""
        config_data = {
            "ats_rules": {
                "max_line_length": -10,  # Invalid value
                "bullet_style": "☆"      # Invalid bullet style
            }
        }
        
        config_file = self.temp_dir / "invalid_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        with pytest.raises(ValueError):
            self.loader.load_config(config_file)
    
    def test_merge_with_defaults(self):
        """Test merging user config with defaults."""
        # Create default config
        default_data = {
            "ats_rules": {
                "max_line_length": 80,
                "bullet_style": "•",
                "optimize_keywords": True
            },
            "styling": {
                "theme": "professional",
                "font_size": 11
            }
        }
        
        # User config overrides some values
        user_data = {
            "ats_rules": {
                "max_line_length": 75,
                "bullet_style": "-"
                # optimize_keywords not specified, should use default
            },
            "styling": {
                "theme": "modern"
                # font_size not specified, should use default
            }
        }
        
        # Create test files
        default_file = self.temp_dir / "default.yaml"
        with open(default_file, 'w') as f:
            yaml.dump(default_data, f)
        
        config_file = self.temp_dir / "user.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(user_data, f)
        
        # Load with custom default
        loader = ConfigLoader(default_file)
        config = loader.load_config(config_file)
        
        # Check merged values
        assert config.ats_rules.max_line_length == 75  # User override
        assert config.ats_rules.bullet_style == "-"    # User override
        assert config.ats_rules.optimize_keywords is True  # Default value
        assert config.styling.theme == "modern"        # User override
        assert config.styling.font_size == 11          # Default value
    
    def test_deep_merge(self):
        """Test deep merging of nested configurations."""
        base = {
            "ats_rules": {
                "max_line_length": 80,
                "bullet_style": "•",
                "section_order": ["contact", "summary"]
            },
            "styling": {
                "theme": "professional",
                "color_scheme": {
                    "primary": "#000000",
                    "secondary": "#333333"
                }
            }
        }
        
        override = {
            "ats_rules": {
                "max_line_length": 75,
                # bullet_style should remain from base
                "section_order": ["contact", "experience"]  # Complete override
            },
            "styling": {
                "color_scheme": {
                    "primary": "#111111",
                    # secondary should remain from base
                    "accent": "#0066cc"  # New value
                }
            }
        }
        
        result = self.loader._deep_merge(base, override)
        
        assert result["ats_rules"]["max_line_length"] == 75
        assert result["ats_rules"]["bullet_style"] == "•"
        assert result["ats_rules"]["section_order"] == ["contact", "experience"]
        assert result["styling"]["theme"] == "professional"
        assert result["styling"]["color_scheme"]["primary"] == "#111111"
        assert result["styling"]["color_scheme"]["secondary"] == "#333333"
        assert result["styling"]["color_scheme"]["accent"] == "#0066cc"
    
    def test_merge_configs_multiple_files(self):
        """Test merging multiple configuration files."""
        # Base config
        base_data = {
            "ats_rules": {"max_line_length": 80},
            "styling": {"theme": "professional"}
        }
        base_file = self.temp_dir / "base.yaml"
        with open(base_file, 'w') as f:
            yaml.dump(base_data, f)
        
        # Override 1
        override1_data = {
            "ats_rules": {"bullet_style": "-"},
            "output_formats": {"html_theme": "modern"}
        }
        override1_file = self.temp_dir / "override1.yaml"
        with open(override1_file, 'w') as f:
            yaml.dump(override1_data, f)
        
        # Override 2
        override2_data = {
            "styling": {"font_size": 12}
        }
        override2_file = self.temp_dir / "override2.yaml"
        with open(override2_file, 'w') as f:
            yaml.dump(override2_data, f)
        
        # Create loader with base as default
        loader = ConfigLoader(base_file)
        config = loader.merge_configs(override1_file, override2_file)
        
        assert config.ats_rules.max_line_length == 80        # From base
        assert config.ats_rules.bullet_style == "-"          # From override1
        assert config.output_formats.html_theme == "modern"  # From override1
        assert config.styling.font_size == 12                # From override2
    
    def test_merge_configs_missing_files(self):
        """Test merging configs when some files are missing."""
        # Only create one file
        valid_data = {"ats_rules": {"max_line_length": 75}}
        valid_file = self.temp_dir / "valid.yaml"
        with open(valid_file, 'w') as f:
            yaml.dump(valid_data, f)
        
        missing_file = self.temp_dir / "missing.yaml"
        
        # Should not raise error, just skip missing files
        config = self.loader.merge_configs(valid_file, missing_file)
        assert config.ats_rules.max_line_length == 75
    
    def test_validate_config_file_valid(self):
        """Test validating a valid configuration file."""
        config_data = {
            "ats_rules": {"max_line_length": 75},
            "styling": {"theme": "modern"}
        }
        
        config_file = self.temp_dir / "valid.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        is_valid, error = self.loader.validate_config_file(config_file)
        assert is_valid is True
        assert error is None
    
    def test_validate_config_file_invalid(self):
        """Test validating an invalid configuration file."""
        config_data = {
            "ats_rules": {"max_line_length": -10}  # Invalid value
        }
        
        config_file = self.temp_dir / "invalid.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        is_valid, error = self.loader.validate_config_file(config_file)
        assert is_valid is False
        assert error is not None
        assert "validation" in error.lower()
    
    def test_validate_config_file_not_found(self):
        """Test validating a non-existent configuration file."""
        missing_file = self.temp_dir / "missing.yaml"
        
        is_valid, error = self.loader.validate_config_file(missing_file)
        assert is_valid is False
        assert "not found" in error
    
    def test_get_config_schema(self):
        """Test getting configuration schema."""
        schema = self.loader.get_config_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "ats_rules" in schema["properties"]
        assert "output_formats" in schema["properties"]
    
    def test_save_config(self):
        """Test saving configuration to file."""
        config = Config()
        config.ats_rules.max_line_length = 85
        config.styling.theme = "tech"
        
        output_file = self.temp_dir / "saved_config.yaml"
        self.loader.save_config(config, output_file)
        
        assert output_file.exists()
        
        # Verify saved content
        with open(output_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data["ats_rules"]["max_line_length"] == 85
        assert saved_data["styling"]["theme"] == "tech"
    
    def test_create_sample_config(self):
        """Test creating sample configuration file."""
        sample_file = self.temp_dir / "sample_config.yaml"
        self.loader.create_sample_config(sample_file)
        
        assert sample_file.exists()
        
        # Should be able to load the sample config
        config = self.loader.load_config(sample_file)
        assert isinstance(config, Config)


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_config_from_path(self):
        """Test load_config_from_path convenience function."""
        config_data = {"ats_rules": {"max_line_length": 85}}
        config_file = self.temp_dir / "test.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = load_config_from_path(config_file)
        assert isinstance(config, Config)
        assert config.ats_rules.max_line_length == 85
    
    def test_load_default_config_function(self):
        """Test load_default_config convenience function."""
        config = load_default_config()
        assert isinstance(config, Config)
    
    def test_load_config_with_yaml_error(self):
        """Test handling YAML parsing errors."""
        invalid_yaml_file = self.temp_dir / "invalid.yaml"
        with open(invalid_yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        with pytest.raises(yaml.YAMLError):
            load_config_from_path(invalid_yaml_file)


class TestCaching:
    """Test configuration caching functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = ConfigLoader()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_default_config_caching(self):
        """Test that default config is cached."""
        # Create default config file
        default_data = {"ats_rules": {"max_line_length": 85}}
        default_file = self.temp_dir / "default.yaml"
        with open(default_file, 'w') as f:
            yaml.dump(default_data, f)
        
        loader = ConfigLoader(default_file)
        
        # Load twice - should be cached
        config1 = loader.load_default_config()
        config2 = loader.load_default_config()
        
        # Should be the same object (cached)
        assert config1 is config2
    
    def test_config_caching_by_path(self):
        """Test that configurations are cached by path."""
        config_data = {"ats_rules": {"max_line_length": 75}}
        config_file = self.temp_dir / "cached.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load same file twice
        config1 = self.loader.load_config(config_file)
        config2 = self.loader.load_config(config_file)
        
        # Should be the same object (cached)
        assert config1 is config2