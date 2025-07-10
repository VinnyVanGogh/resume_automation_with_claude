"""
Configuration loader for YAML-based configuration files.

This module provides functionality to load, merge, and validate
configuration files for the resume automation system.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml

from .config_model import Config


logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    YAML configuration loader with merging and validation capabilities.
    
    Handles loading default configurations, user configurations, and
    merging them together with proper error handling.
    """
    
    def __init__(self, default_config_path: Optional[Path] = None):
        """
        Initialize the configuration loader.
        
        Args:
            default_config_path: Path to default configuration file
        """
        self.default_config_path = default_config_path or self._get_default_config_path()
        self._default_config_dict: Optional[Dict[str, Any]] = None
        self._default_config_obj: Optional[Config] = None
        self._config_cache: Dict[str, Config] = {}
        
    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        return Path(__file__).parent / "default_config.yaml"
    
    def load_config(self, config_path: Union[str, Path]) -> Config:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Config: Validated configuration instance
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValueError: If configuration validation fails
        """
        config_path = Path(config_path)
        cache_key = str(config_path.absolute())
        
        # Check cache first
        if cache_key in self._config_cache:
            logger.debug(f"Returning cached configuration for: {config_path}")
            return self._config_cache[cache_key]
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        logger.info(f"Loading configuration from: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML configuration: {e}")
        
        if config_data is None:
            config_data = {}
        
        # Merge with default configuration
        merged_config = self._merge_with_defaults(config_data)
        
        # Validate and return configuration
        try:
            config = Config.from_dict(merged_config)
            # Cache the result
            self._config_cache[cache_key] = config
            return config
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    def load_default_config(self) -> Config:
        """
        Load the default configuration.
        
        Returns:
            Config: Default configuration instance
            
        Raises:
            FileNotFoundError: If default configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        # Return cached default config if available
        if self._default_config_obj is not None:
            return self._default_config_obj
        
        if not self.default_config_path.exists():
            logger.warning(f"Default configuration file not found: {self.default_config_path}")
            # Return empty configuration that will use model defaults
            self._default_config_obj = Config()
            return self._default_config_obj
        
        logger.info(f"Loading default configuration from: {self.default_config_path}")
        
        try:
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse default YAML configuration: {e}")
        
        if config_data is None:
            config_data = {}
        
        self._default_config_obj = Config.from_dict(config_data)
        return self._default_config_obj
    
    def _load_default_config_dict(self) -> Dict[str, Any]:
        """Load default configuration as dictionary."""
        if self._default_config_dict is None:
            if self.default_config_path.exists():
                with open(self.default_config_path, 'r', encoding='utf-8') as f:
                    self._default_config_dict = yaml.safe_load(f) or {}
            else:
                self._default_config_dict = {}
        return self._default_config_dict
    
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with default configuration.
        
        Args:
            user_config: User configuration dictionary
            
        Returns:
            Dict[str, Any]: Merged configuration dictionary
        """
        default_config = self._load_default_config_dict()
        return self._deep_merge(default_config, user_config)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Dict[str, Any]: Merged dictionary
        """
        merged = base.copy()
        
        for key, value in override.items():
            if (key in merged and 
                isinstance(merged[key], dict) and 
                isinstance(value, dict)):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def merge_configs(self, *config_paths: Union[str, Path]) -> Config:
        """
        Merge multiple configuration files.
        
        Args:
            *config_paths: Paths to configuration files
            
        Returns:
            Config: Merged configuration instance
        """
        merged_config = self._load_default_config_dict()
        
        for config_path in config_paths:
            config_path = Path(config_path)
            
            if not config_path.exists():
                logger.warning(f"Configuration file not found, skipping: {config_path}")
                continue
                
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                merged_config = self._deep_merge(merged_config, config_data)
                logger.info(f"Merged configuration from: {config_path}")
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse configuration file {config_path}: {e}")
                continue
        
        return Config.from_dict(merged_config)
    
    def validate_config_file(self, config_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """
        Validate a configuration file without loading it.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            return False, f"Configuration file not found: {config_path}"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return False, f"YAML parsing error: {e}"
        
        if config_data is None:
            config_data = {}
        
        try:
            merged_config = self._merge_with_defaults(config_data)
            Config.from_dict(merged_config)
            return True, None
        except Exception as e:
            return False, f"Configuration validation error: {e}"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get the configuration schema.
        
        Returns:
            Dict[str, Any]: JSON schema for configuration
        """
        return Config.model_json_schema()
    
    def save_config(self, config: Config, output_path: Union[str, Path]) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            config: Configuration instance to save
            output_path: Output file path
        """
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = config.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2, sort_keys=False)
        
        logger.info(f"Configuration saved to: {output_path}")
    
    def create_sample_config(self, output_path: Union[str, Path]) -> None:
        """
        Create a sample configuration file with default values.
        
        Args:
            output_path: Output file path for sample configuration
        """
        default_config = self.load_default_config()
        self.save_config(default_config, output_path)
        logger.info(f"Sample configuration created at: {output_path}")


def load_config_from_path(config_path: Union[str, Path]) -> Config:
    """
    Convenience function to load configuration from a path.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Config: Loaded configuration instance
    """
    loader = ConfigLoader()
    return loader.load_config(config_path)


def load_default_config() -> Config:
    """
    Convenience function to load default configuration.
    
    Returns:
        Config: Default configuration instance
    """
    loader = ConfigLoader()
    return loader.load_default_config()