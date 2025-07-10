"""
Utility functions and helper methods for the resume converter module.

This module provides various utility functions for format discovery, theme enumeration,
template validation, configuration validation, and system diagnostics.
"""

import logging
import sys
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import json
import yaml
from datetime import datetime

from src.config import Config, ConfigLoader, ConfigValidator
from .exceptions import ValidationError, ConfigurationError
from .types import ConversionResult, BatchConversionResult


logger = logging.getLogger(__name__)


class SystemInfo:
    """System information and diagnostics utilities."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Returns:
            Dictionary with system information
        """
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
            },
            "python": {
                "version": sys.version,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                },
                "executable": sys.executable,
                "path": sys.path[:3],  # First 3 entries
            },
            "memory": {
                "available": SystemInfo._get_memory_info(),
            },
            "disk": {
                "current_directory": str(Path.cwd()),
                "temp_directory": str(Path.cwd() / "temp"),
            }
        }
    
    @staticmethod
    def _get_memory_info() -> Optional[str]:
        """Get memory information if available."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return f"{memory.available / (1024**3):.1f} GB available"
        except ImportError:
            return "psutil not available"
        except Exception:
            return "unknown"
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """
        Check if all required dependencies are available.
        
        Returns:
            Dictionary mapping dependency names to availability
        """
        dependencies = {
            "mistune": False,
            "pydantic": False, 
            "yaml": False,
            "pathlib": False,
            "weasyprint": False,
            "python-docx": False,
            "jinja2": False,
        }
        
        for dep in dependencies:
            try:
                if dep == "python-docx":
                    import docx
                elif dep == "yaml":
                    import yaml
                else:
                    __import__(dep)
                dependencies[dep] = True
            except ImportError:
                dependencies[dep] = False
        
        return dependencies
    
    @staticmethod
    def validate_environment() -> List[str]:
        """
        Validate the environment for resume conversion.
        
        Returns:
            List of environment issues
        """
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 12):
            issues.append(f"Python 3.12+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check critical dependencies
        critical_deps = ["mistune", "pydantic", "yaml"]
        deps = SystemInfo.check_dependencies()
        
        for dep in critical_deps:
            if not deps.get(dep, False):
                issues.append(f"Critical dependency missing: {dep}")
        
        # Check optional dependencies
        optional_deps = ["weasyprint", "python-docx"]
        for dep in optional_deps:
            if not deps.get(dep, False):
                issues.append(f"Optional dependency missing: {dep} (some features may not work)")
        
        return issues


class FormatUtils:
    """Utilities for format discovery and validation."""
    
    SUPPORTED_FORMATS = ["html", "pdf", "docx"]
    
    FORMAT_EXTENSIONS = {
        "html": [".html", ".htm"],
        "pdf": [".pdf"],
        "docx": [".docx", ".doc"]
    }
    
    FORMAT_MIMETYPES = {
        "html": ["text/html"],
        "pdf": ["application/pdf"],
        "docx": [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]
    }
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported output formats."""
        return FormatUtils.SUPPORTED_FORMATS.copy()
    
    @staticmethod
    def validate_format(format_name: str) -> bool:
        """
        Validate if format is supported.
        
        Args:
            format_name: Format name to validate
            
        Returns:
            True if format is supported
        """
        return format_name.lower() in FormatUtils.SUPPORTED_FORMATS
    
    @staticmethod
    def detect_format_from_file(file_path: Path) -> Optional[str]:
        """
        Detect format from file extension or content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected format or None
        """
        if not file_path.exists():
            return None
        
        suffix = file_path.suffix.lower()
        
        for format_name, extensions in FormatUtils.FORMAT_EXTENSIONS.items():
            if suffix in extensions:
                return format_name
        
        return None
    
    @staticmethod
    def get_format_info(format_name: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a format.
        
        Args:
            format_name: Format name
            
        Returns:
            Dictionary with format information
        """
        if not FormatUtils.validate_format(format_name):
            raise ValueError(f"Unsupported format: {format_name}")
        
        format_name = format_name.lower()
        
        info = {
            "name": format_name,
            "extensions": FormatUtils.FORMAT_EXTENSIONS[format_name],
            "mimetypes": FormatUtils.FORMAT_MIMETYPES[format_name],
            "ats_friendly": format_name in ["pdf", "docx"],
            "web_compatible": format_name == "html",
            "editable": format_name == "docx",
            "print_ready": format_name in ["pdf", "docx"]
        }
        
        return info


class ThemeUtils:
    """Utilities for theme discovery and validation."""
    
    AVAILABLE_THEMES = {
        "html": ["professional", "modern", "minimal", "tech"],
        "pdf": ["professional", "modern", "minimal", "tech"],  
        "docx": ["professional", "modern", "minimal"]
    }
    
    THEME_DESCRIPTIONS = {
        "professional": "Clean, traditional business style",
        "modern": "Contemporary design with accent colors",
        "minimal": "Simple, clean layout with minimal styling",
        "tech": "Technology-focused with modern fonts and spacing"
    }
    
    @staticmethod
    def get_available_themes() -> Dict[str, List[str]]:
        """Get all available themes by format."""
        return ThemeUtils.AVAILABLE_THEMES.copy()
    
    @staticmethod
    def get_themes_for_format(format_name: str) -> List[str]:
        """
        Get available themes for a specific format.
        
        Args:
            format_name: Format name
            
        Returns:
            List of available theme names
        """
        return ThemeUtils.AVAILABLE_THEMES.get(format_name.lower(), [])
    
    @staticmethod
    def validate_theme(format_name: str, theme_name: str) -> bool:
        """
        Validate if theme is available for format.
        
        Args:
            format_name: Format name
            theme_name: Theme name
            
        Returns:
            True if theme is available for format
        """
        available_themes = ThemeUtils.get_themes_for_format(format_name)
        return theme_name.lower() in [t.lower() for t in available_themes]
    
    @staticmethod
    def get_theme_info(theme_name: str) -> Dict[str, Any]:
        """
        Get information about a theme.
        
        Args:
            theme_name: Theme name
            
        Returns:
            Dictionary with theme information
        """
        theme_name = theme_name.lower()
        
        # Find which formats support this theme
        supported_formats = []
        for format_name, themes in ThemeUtils.AVAILABLE_THEMES.items():
            if theme_name in [t.lower() for t in themes]:
                supported_formats.append(format_name)
        
        return {
            "name": theme_name,
            "description": ThemeUtils.THEME_DESCRIPTIONS.get(theme_name, "No description available"),
            "supported_formats": supported_formats,
            "is_ats_friendly": theme_name in ["professional", "minimal"]
        }


class ConfigUtils:
    """Utilities for configuration management and validation."""
    
    @staticmethod
    def validate_config_file(config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a configuration file comprehensively.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary with validation results
        """
        config_path = Path(config_path)
        
        result = {
            "is_valid": False,
            "file_exists": config_path.exists(),
            "file_readable": False,
            "yaml_valid": False,
            "schema_valid": False,
            "business_rules_valid": False,
            "errors": [],
            "warnings": [],
            "config_summary": {}
        }
        
        if not result["file_exists"]:
            result["errors"].append(f"Configuration file does not exist: {config_path}")
            return result
        
        # Check file readability
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result["file_readable"] = True
        except Exception as e:
            result["errors"].append(f"Cannot read configuration file: {e}")
            return result
        
        # Check YAML validity
        try:
            config_data = yaml.safe_load(content)
            result["yaml_valid"] = True
        except yaml.YAMLError as e:
            result["errors"].append(f"Invalid YAML syntax: {e}")
            return result
        
        # Check schema validity
        try:
            config = Config(**config_data)
            result["schema_valid"] = True
            result["config_summary"] = ConfigUtils._summarize_config(config)
        except Exception as e:
            result["errors"].append(f"Configuration schema validation failed: {e}")
            return result
        
        # Check business rules
        try:
            validator = ConfigValidator()
            validation_result = validator.validate_full_config(config)
            
            result["business_rules_valid"] = validation_result.is_valid
            result["errors"].extend(validation_result.errors)
            result["warnings"].extend(validation_result.warnings)
            
        except Exception as e:
            result["errors"].append(f"Business rule validation failed: {e}")
            return result
        
        result["is_valid"] = (
            result["file_readable"] and 
            result["yaml_valid"] and 
            result["schema_valid"] and 
            result["business_rules_valid"]
        )
        
        return result
    
    @staticmethod
    def _summarize_config(config: Config) -> Dict[str, Any]:
        """Create a summary of configuration settings."""
        return {
            "ats_rules": {
                "max_line_length": config.ats_rules.max_line_length,
                "bullet_style": config.ats_rules.bullet_style,
                "optimize_keywords": config.ats_rules.optimize_keywords
            },
            "output_formats": {
                "enabled_formats": config.output_formats.enabled_formats,
                "output_directory": config.output_formats.output_directory,
                "html_theme": config.output_formats.html_theme
            },
            "styling": {
                "theme": config.styling.theme,
                "font_family": config.styling.font_family,
                "font_size": config.styling.font_size
            },
            "processing": {
                "batch_size": config.processing.batch_size,
                "max_workers": config.processing.max_workers,
                "validate_input": config.processing.validate_input
            }
        }
    
    @staticmethod
    def create_sample_config(output_path: Union[str, Path]) -> None:
        """
        Create a sample configuration file.
        
        Args:
            output_path: Path where to create the sample config
        """
        sample_config = {
            "version": "1.0",
            "created_by": "resume-automation-cli",
            "created_at": datetime.now().isoformat(),
            
            "ats_rules": {
                "max_line_length": 80,
                "bullet_style": "•",
                "section_order": ["contact", "summary", "experience", "education", "skills"],
                "optimize_keywords": True,
                "remove_special_chars": True
            },
            
            "output_formats": {
                "enabled_formats": ["html", "pdf", "docx"],
                "html_theme": "professional",
                "pdf_page_size": "Letter",
                "docx_template": "professional",
                "output_directory": "output",
                "filename_prefix": "resume",
                "overwrite_existing": True
            },
            
            "styling": {
                "theme": "professional",
                "font_family": "Arial",
                "font_size": 11,
                "color_scheme": {
                    "primary": "#000000",
                    "secondary": "#333333",
                    "accent": "#0066cc"
                }
            },
            
            "processing": {
                "batch_size": 10,
                "max_workers": 4,
                "validate_input": True,
                "validate_output": True
            },
            
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        output_path = Path(output_path)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Sample configuration created: {output_path}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create sample configuration: {e}",
                config_path=str(output_path)
            )


class ResultUtils:
    """Utilities for processing and analyzing conversion results."""
    
    @staticmethod
    def analyze_conversion_result(result: ConversionResult) -> Dict[str, Any]:
        """
        Analyze a single conversion result.
        
        Args:
            result: ConversionResult to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "success": result.success,
            "performance": {
                "processing_time": result.processing_time,
                "files_per_second": 1 / result.processing_time if result.processing_time > 0 else 0,
                "efficiency_rating": ResultUtils._calculate_efficiency_rating(result)
            },
            "quality": {
                "output_count": len(result.output_files),
                "warning_count": len(result.warnings),
                "error_count": len(result.errors),
                "quality_score": ResultUtils._calculate_quality_score(result)
            },
            "outputs": [
                {
                    "path": str(f),
                    "format": FormatUtils.detect_format_from_file(f),
                    "size": f.stat().st_size if f.exists() else 0,
                    "exists": f.exists()
                }
                for f in result.output_files
            ]
        }
        
        return analysis
    
    @staticmethod
    def analyze_batch_result(batch_result: BatchConversionResult) -> Dict[str, Any]:
        """
        Analyze a batch conversion result.
        
        Args:
            batch_result: BatchConversionResult to analyze
            
        Returns:
            Dictionary with analysis results
        """
        individual_analyses = [
            ResultUtils.analyze_conversion_result(result)
            for result in batch_result.results
        ]
        
        analysis = {
            "summary": {
                "total_files": batch_result.total_files,
                "successful_files": batch_result.successful_files,
                "failed_files": batch_result.failed_files,
                "success_rate": batch_result.success_rate
            },
            "performance": {
                "total_processing_time": batch_result.total_processing_time,
                "average_time_per_file": (
                    batch_result.total_processing_time / batch_result.total_files
                    if batch_result.total_files > 0 else 0
                ),
                "throughput": (
                    batch_result.total_files / batch_result.total_processing_time
                    if batch_result.total_processing_time > 0 else 0
                )
            },
            "quality": {
                "average_quality_score": ResultUtils._calculate_average_quality_score(individual_analyses),
                "total_warnings": sum(len(r.warnings) for r in batch_result.results),
                "total_errors": sum(len(r.errors) for r in batch_result.results)
            },
            "individual_results": individual_analyses
        }
        
        return analysis
    
    @staticmethod
    def _calculate_efficiency_rating(result: ConversionResult) -> str:
        """Calculate efficiency rating based on processing time."""
        if result.processing_time < 2.0:
            return "excellent"
        elif result.processing_time < 5.0:
            return "good"
        elif result.processing_time < 10.0:
            return "fair"
        else:
            return "poor"
    
    @staticmethod
    def _calculate_quality_score(result: ConversionResult) -> float:
        """Calculate quality score based on outputs and issues."""
        base_score = 100.0
        
        # Penalize for errors and warnings
        base_score -= len(result.errors) * 20
        base_score -= len(result.warnings) * 5
        
        # Bonus for multiple successful outputs
        if result.success and len(result.output_files) > 1:
            base_score += len(result.output_files) * 2
        
        return max(0.0, min(100.0, base_score))
    
    @staticmethod
    def _calculate_average_quality_score(analyses: List[Dict[str, Any]]) -> float:
        """Calculate average quality score from individual analyses."""
        if not analyses:
            return 0.0
        
        total_score = sum(a["quality"]["quality_score"] for a in analyses)
        return total_score / len(analyses)
    
    @staticmethod
    def export_results_to_json(
        results: Union[ConversionResult, BatchConversionResult],
        output_path: Union[str, Path],
        include_analysis: bool = True
    ) -> None:
        """
        Export conversion results to JSON file.
        
        Args:
            results: Results to export
            output_path: Output file path
            include_analysis: Whether to include analysis
        """
        output_path = Path(output_path)
        
        # Prepare data for export
        if isinstance(results, BatchConversionResult):
            export_data = {
                "type": "batch_result",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_files": results.total_files,
                    "successful_files": results.successful_files,
                    "failed_files": results.failed_files,
                    "success_rate": results.success_rate,
                    "total_processing_time": results.total_processing_time
                },
                "results": [
                    {
                        "input_path": str(r.input_path),
                        "success": r.success,
                        "output_files": [str(f) for f in r.output_files],
                        "processing_time": r.processing_time,
                        "warnings": r.warnings,
                        "errors": r.errors,
                        "metadata": r.metadata
                    }
                    for r in results.results
                ]
            }
            
            if include_analysis:
                export_data["analysis"] = ResultUtils.analyze_batch_result(results)
        
        else:
            export_data = {
                "type": "single_result",
                "timestamp": datetime.now().isoformat(),
                "input_path": str(results.input_path),
                "success": results.success,
                "output_files": [str(f) for f in results.output_files],
                "processing_time": results.processing_time,
                "warnings": results.warnings,
                "errors": results.errors,
                "metadata": results.metadata
            }
            
            if include_analysis:
                export_data["analysis"] = ResultUtils.analyze_conversion_result(results)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to: {output_path}")
            
        except Exception as e:
            raise ValidationError(f"Failed to export results: {e}")


# Convenience functions for common operations

def get_system_diagnostics() -> Dict[str, Any]:
    """Get comprehensive system diagnostics."""
    return {
        "system_info": SystemInfo.get_system_info(),
        "dependencies": SystemInfo.check_dependencies(),
        "environment_issues": SystemInfo.validate_environment(),
        "supported_formats": FormatUtils.get_supported_formats(),
        "available_themes": ThemeUtils.get_available_themes()
    }


def validate_setup() -> Tuple[bool, List[str]]:
    """
    Validate the complete setup for resume conversion.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = SystemInfo.validate_environment()
    return len(issues) == 0, issues