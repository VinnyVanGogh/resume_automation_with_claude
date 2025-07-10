"""
Configuration manager for the resume converter module.

This module provides a unified interface for loading and managing
configurations for the resume conversion pipeline.
"""

import logging
from pathlib import Path
from typing import Any

from src.config import Config, ConfigLoader, ConfigValidator

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConverterConfigManager:
    """
    Configuration manager for the resume converter.

    Provides a unified interface for loading, validating, and managing
    configurations for the conversion pipeline.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """
        Initialize the configuration manager.

        Args:
            config_path: Optional path to configuration file
        """
        self._config: Config | None = None
        self._config_path = Path(config_path) if config_path else None
        self._loader = ConfigLoader()
        self._validator = ConfigValidator()

        # Load configuration on initialization
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load and validate configuration."""
        try:
            if self._config_path:
                logger.info(f"Loading configuration from: {self._config_path}")
                self._config = self._loader.load_config(self._config_path)
            else:
                logger.info("Using default configuration")
                self._config = self._load_default_config()

            # Validate configuration
            self._validate_configuration()

        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                config_path=str(self._config_path) if self._config_path else None,
            )

    def _load_default_config(self) -> Config:
        """Load the default configuration."""
        try:
            return self._loader.load_default_config()
        except Exception as e:
            raise ConfigurationError(f"Failed to load default configuration: {e}")

    def _validate_configuration(self) -> None:
        """Validate the loaded configuration."""
        if not self._config:
            raise ConfigurationError("No configuration loaded")

        try:
            result = self._validator.validate_full_config(self._config)

            if not result.is_valid:
                error_msg = "Configuration validation failed:\n"
                error_msg += "\n".join(f"  - {error}" for error in result.errors)
                raise ConfigurationError(error_msg)

            if result.warnings:
                logger.warning("Configuration warnings:")
                for warning in result.warnings:
                    logger.warning(f"  - {warning}")

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Configuration validation error: {e}")

    @property
    def config(self) -> Config:
        """Get the current configuration."""
        if not self._config:
            raise ConfigurationError("Configuration not loaded")
        return self._config

    @property
    def config_path(self) -> Path | None:
        """Get the configuration file path."""
        return self._config_path

    def reload_config(self, new_config_path: str | Path | None = None) -> None:
        """
        Reload configuration from file.

        Args:
            new_config_path: Optional new configuration file path
        """
        if new_config_path:
            self._config_path = Path(new_config_path)

        self._load_configuration()
        logger.info("Configuration reloaded successfully")

    def update_config_overrides(self, overrides: dict[str, Any]) -> None:
        """
        Apply runtime configuration overrides.

        Args:
            overrides: Dictionary of configuration overrides
        """
        if not self._config:
            raise ConfigurationError("No configuration loaded")

        try:
            # Create a new config with overrides
            config_dict = self._config.model_dump()
            self._apply_overrides(config_dict, overrides)

            # Validate the updated configuration
            updated_config = Config(**config_dict)
            temp_config = self._config
            self._config = updated_config

            try:
                self._validate_configuration()
                logger.info("Configuration overrides applied successfully")
            except Exception:
                # Restore previous config if validation fails
                self._config = temp_config
                raise

        except Exception as e:
            raise ConfigurationError(f"Failed to apply configuration overrides: {e}")

    def _apply_overrides(
        self, config_dict: dict[str, Any], overrides: dict[str, Any]
    ) -> None:
        """
        Apply overrides to configuration dictionary.

        Args:
            config_dict: Configuration dictionary to modify
            overrides: Overrides to apply
        """
        for key, value in overrides.items():
            if "." in key:
                # Handle nested keys like "ats_rules.max_line_length"
                parts = key.split(".")
                current = config_dict
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config_dict[key] = value

    def get_output_formats(self) -> list[str]:
        """Get enabled output formats from configuration."""
        return self.config.output_formats.enabled_formats

    def get_output_directory(self) -> Path:
        """Get output directory from configuration."""
        return Path(self.config.output_formats.output_directory)

    def get_filename_prefix(self) -> str:
        """Get filename prefix from configuration."""
        return self.config.output_formats.filename_prefix

    def should_overwrite_existing(self) -> bool:
        """Check if existing files should be overwritten."""
        return self.config.output_formats.overwrite_existing

    def should_validate_input(self) -> bool:
        """Check if input validation is enabled."""
        return self.config.processing.validate_input

    def should_validate_output(self) -> bool:
        """Check if output validation is enabled."""
        return self.config.processing.validate_output

    def get_max_workers(self) -> int:
        """Get maximum number of workers for batch processing."""
        return self.config.processing.max_workers

    def get_batch_size(self) -> int:
        """Get batch size for processing."""
        return self.config.processing.batch_size

    def get_timeout_seconds(self) -> int:
        """Get processing timeout in seconds."""
        return self.config.processing.timeout_seconds

    def is_strict_validation(self) -> bool:
        """Check if strict validation mode is enabled."""
        return getattr(self.config.processing, "strict_validation", False)

    def get_config_summary(self) -> dict[str, Any]:
        """
        Get a summary of current configuration settings.

        Returns:
            Dictionary with key configuration settings
        """
        return {
            "config_path": str(self._config_path) if self._config_path else "default",
            "output_formats": {
                "enabled_formats": self.get_output_formats(),
                "output_directory": str(self.get_output_directory()),
                "filename_prefix": self.get_filename_prefix(),
                "overwrite_existing": self.should_overwrite_existing(),
            },
            "max_workers": self.get_max_workers(),
            "batch_size": self.get_batch_size(),
            "validate_input": self.should_validate_input(),
            "validate_output": self.should_validate_output(),
            "ats_rules": {
                "max_line_length": self.config.ats_rules.max_line_length,
                "bullet_style": self.config.ats_rules.bullet_style,
                "optimize_keywords": self.config.ats_rules.optimize_keywords,
                "remove_special_chars": self.config.ats_rules.remove_special_chars,
                "formatting_rules": self.config.ats_rules.formatting_rules,
            },
            "styling": {
                "theme": self.config.styling.theme,
                "font_family": self.config.styling.font_family,
                "font_size": self.config.styling.font_size,
                "line_height": self.config.styling.line_height,
            },
            "processing": {
                "max_workers": self.config.processing.max_workers,
                "batch_size": self.config.processing.batch_size,
                "timeout_seconds": self.config.processing.timeout_seconds,
                "validate_input": self.config.processing.validate_input,
                "validate_output": self.config.processing.validate_output,
            },
        }

    def get_effective_config(self):
        """
        Get the effective configuration object.

        Returns:
            The current configuration object
        """
        return self.config

    def export_config(self, file_path: str | Path) -> None:
        """
        Export current configuration to file.

        Args:
            file_path: Path to save the configuration
        """
        import yaml
        
        config_dict = self.config.model_dump()
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration exported to {file_path}")

    def validate_config(self) -> tuple[bool, list[str]]:
        """
        Validate current configuration and return validation results.

        Returns:
            Tuple of (is_valid, errors)
        """
        try:
            result = self._validator.validate_full_config(self.config)
            return result.is_valid, result.errors
        except Exception as e:
            return False, [str(e)]

    def clear_overrides(self) -> None:
        """
        Clear any runtime overrides and reload from file.
        """
        self._load_configuration()
        logger.info("Configuration overrides cleared")
