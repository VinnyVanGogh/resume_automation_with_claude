"""
Unit tests for the utilities module.

Tests utility functions including system diagnostics, format discovery,
theme enumeration, configuration validation, and result analysis.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from ..types import BatchConversionResult, ConversionResult
from ..utilities import (
    ConfigUtils,
    FormatUtils,
    ResultUtils,
    SystemInfo,
    ThemeUtils,
    get_system_diagnostics,
    validate_setup,
)


class TestSystemInfo:
    """Test SystemInfo utility class."""

    def test_get_system_info(self):
        """Test getting comprehensive system information."""
        system_info = SystemInfo.get_system_info()

        assert isinstance(system_info, dict)
        assert "platform" in system_info
        assert "python" in system_info
        assert "memory" in system_info
        assert "disk" in system_info

        # Verify platform information
        platform_info = system_info["platform"]
        assert "system" in platform_info
        assert "release" in platform_info
        assert "version" in platform_info
        assert "machine" in platform_info
        assert "architecture" in platform_info

        # Verify Python information
        python_info = system_info["python"]
        assert "version" in python_info
        assert "version_info" in python_info
        assert "executable" in python_info
        assert "path" in python_info

        # Verify version info structure
        version_info = python_info["version_info"]
        assert "major" in version_info
        assert "minor" in version_info
        assert "micro" in version_info
        assert version_info["major"] == sys.version_info.major

    def test_check_dependencies(self):
        """Test dependency checking functionality."""
        dependencies = SystemInfo.check_dependencies()

        assert isinstance(dependencies, dict)

        # Check expected dependencies
        expected_deps = [
            "mistune",
            "pydantic",
            "yaml",
            "pathlib",
            "weasyprint",
            "python-docx",
            "jinja2",
        ]
        for dep in expected_deps:
            assert dep in dependencies
            assert isinstance(dependencies[dep], bool)

        # Pathlib should always be available (built-in)
        assert dependencies["pathlib"] is True

        # Pydantic and yaml should be available (required dependencies)
        assert dependencies["pydantic"] is True
        assert dependencies["yaml"] is True

    def test_validate_environment(self):
        """Test environment validation."""
        issues = SystemInfo.validate_environment()

        assert isinstance(issues, list)

        # Current environment should have Python 3.12+ (based on project requirements)
        python_issues = [issue for issue in issues if "python" in issue.lower()]
        # In a properly configured environment, this should be empty

        # Check for critical dependencies
        critical_issues = [issue for issue in issues if "critical" in issue.lower()]
        # Should have minimal critical issues in a proper environment

    @patch("src.converter.utilities.psutil")
    def test_get_memory_info_with_psutil(self, mock_psutil):
        """Test memory information retrieval with psutil available."""
        # Mock psutil
        mock_memory = MagicMock()
        mock_memory.available = 8 * 1024**3  # 8GB
        mock_psutil.virtual_memory.return_value = mock_memory

        memory_info = SystemInfo._get_memory_info()

        assert "8.0 GB" in memory_info
        mock_psutil.virtual_memory.assert_called_once()

    @patch("src.converter.utilities.psutil")
    def test_get_memory_info_without_psutil(self, mock_psutil):
        """Test memory information retrieval without psutil."""
        # Set up mock to raise ImportError when virtual_memory is called
        mock_psutil.virtual_memory.side_effect = ImportError("No module named 'psutil'")
        
        memory_info = SystemInfo._get_memory_info()

        assert memory_info == "psutil not available"


class TestFormatUtils:
    """Test FormatUtils utility class."""

    def test_get_supported_formats(self):
        """Test getting supported output formats."""
        formats = FormatUtils.get_supported_formats()

        assert isinstance(formats, list)
        assert "html" in formats
        assert "pdf" in formats
        assert "docx" in formats
        assert len(formats) >= 3

    def test_validate_format(self):
        """Test format validation."""
        # Valid formats
        assert FormatUtils.validate_format("html") is True
        assert FormatUtils.validate_format("HTML") is True  # Case insensitive
        assert FormatUtils.validate_format("pdf") is True
        assert FormatUtils.validate_format("docx") is True

        # Invalid formats
        assert FormatUtils.validate_format("txt") is False
        assert FormatUtils.validate_format("xyz") is False
        assert FormatUtils.validate_format("") is False

    def test_detect_format_from_file(self):
        """Test format detection from file extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            html_file = temp_path / "test.html"
            html_file.touch()

            pdf_file = temp_path / "test.pdf"
            pdf_file.touch()

            docx_file = temp_path / "test.docx"
            docx_file.touch()

            unknown_file = temp_path / "test.txt"
            unknown_file.touch()

            # Test detection
            assert FormatUtils.detect_format_from_file(html_file) == "html"
            assert FormatUtils.detect_format_from_file(pdf_file) == "pdf"
            assert FormatUtils.detect_format_from_file(docx_file) == "docx"
            assert FormatUtils.detect_format_from_file(unknown_file) is None

            # Test non-existent file
            nonexistent = temp_path / "nonexistent.html"
            assert FormatUtils.detect_format_from_file(nonexistent) is None

    def test_get_format_info(self):
        """Test getting comprehensive format information."""
        # Test HTML format info
        html_info = FormatUtils.get_format_info("html")

        assert isinstance(html_info, dict)
        assert html_info["name"] == "html"
        assert ".html" in html_info["extensions"]
        assert ".htm" in html_info["extensions"]
        assert "text/html" in html_info["mimetypes"]
        assert html_info["web_compatible"] is True
        assert html_info["ats_friendly"] is False

        # Test PDF format info
        pdf_info = FormatUtils.get_format_info("pdf")

        assert pdf_info["name"] == "pdf"
        assert ".pdf" in pdf_info["extensions"]
        assert "application/pdf" in pdf_info["mimetypes"]
        assert pdf_info["ats_friendly"] is True
        assert pdf_info["print_ready"] is True

        # Test DOCX format info
        docx_info = FormatUtils.get_format_info("docx")

        assert docx_info["name"] == "docx"
        assert ".docx" in docx_info["extensions"]
        assert docx_info["editable"] is True
        assert docx_info["ats_friendly"] is True

        # Test invalid format
        with pytest.raises(ValueError):
            FormatUtils.get_format_info("invalid_format")


class TestThemeUtils:
    """Test ThemeUtils utility class."""

    def test_get_available_themes(self):
        """Test getting all available themes."""
        themes = ThemeUtils.get_available_themes()

        assert isinstance(themes, dict)
        assert "html" in themes
        assert "pdf" in themes
        assert "docx" in themes

        # Verify theme lists
        for format_type, theme_list in themes.items():
            assert isinstance(theme_list, list)
            assert len(theme_list) > 0
            assert "professional" in theme_list

    def test_get_themes_for_format(self):
        """Test getting themes for specific format."""
        html_themes = ThemeUtils.get_themes_for_format("html")

        assert isinstance(html_themes, list)
        assert "professional" in html_themes
        assert "modern" in html_themes
        assert "minimal" in html_themes

        # Test case insensitivity
        html_themes_upper = ThemeUtils.get_themes_for_format("HTML")
        assert html_themes_upper == html_themes

        # Test non-existent format
        unknown_themes = ThemeUtils.get_themes_for_format("unknown")
        assert unknown_themes == []

    def test_validate_theme(self):
        """Test theme validation for formats."""
        # Valid combinations
        assert ThemeUtils.validate_theme("html", "professional") is True
        assert ThemeUtils.validate_theme("pdf", "modern") is True
        assert ThemeUtils.validate_theme("docx", "minimal") is True

        # Case insensitive
        assert ThemeUtils.validate_theme("HTML", "Professional") is True

        # Invalid combinations
        assert ThemeUtils.validate_theme("html", "nonexistent") is False
        assert ThemeUtils.validate_theme("unknown_format", "professional") is False

    def test_get_theme_info(self):
        """Test getting theme information."""
        professional_info = ThemeUtils.get_theme_info("professional")

        assert isinstance(professional_info, dict)
        assert professional_info["name"] == "professional"
        assert "description" in professional_info
        assert "supported_formats" in professional_info
        assert "is_ats_friendly" in professional_info

        # Professional theme should support multiple formats
        assert len(professional_info["supported_formats"]) > 1
        assert "html" in professional_info["supported_formats"]
        assert "pdf" in professional_info["supported_formats"]

        # Professional theme should be ATS-friendly
        assert professional_info["is_ats_friendly"] is True

        # Test tech theme (if available)
        tech_info = ThemeUtils.get_theme_info("tech")
        assert tech_info["name"] == "tech"


class TestConfigUtils:
    """Test ConfigUtils utility class."""

    def test_validate_config_file_valid(self):
        """Test validation of valid configuration file."""
        valid_config = {
            "version": "1.0",
            "ats_rules": {"max_line_length": 80, "bullet_style": "•"},
            "output_formats": {
                "enabled_formats": ["html", "pdf"],
                "html_theme": "professional",
            },
            "styling": {"theme": "professional", "font_size": 11},
            "processing": {"max_workers": 4, "validate_input": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(valid_config, f)
            config_path = f.name

        try:
            result = ConfigUtils.validate_config_file(config_path)

            assert result["is_valid"] is True
            assert result["file_exists"] is True
            assert result["file_readable"] is True
            assert result["yaml_valid"] is True
            assert result["schema_valid"] is True
            assert result["business_rules_valid"] is True
            assert len(result["errors"]) == 0
            assert "config_summary" in result
        finally:
            Path(config_path).unlink()

    def test_validate_config_file_nonexistent(self):
        """Test validation of non-existent configuration file."""
        result = ConfigUtils.validate_config_file("/nonexistent/config.yaml")

        assert result["is_valid"] is False
        assert result["file_exists"] is False
        assert len(result["errors"]) > 0
        assert "does not exist" in result["errors"][0]

    def test_validate_config_file_invalid_yaml(self):
        """Test validation of invalid YAML file."""
        invalid_yaml = "invalid: yaml: content: ["

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            config_path = f.name

        try:
            result = ConfigUtils.validate_config_file(config_path)

            assert result["is_valid"] is False
            assert result["file_exists"] is True
            assert result["file_readable"] is True
            assert result["yaml_valid"] is False
            assert len(result["errors"]) > 0
            assert "yaml" in result["errors"][0].lower()
        finally:
            Path(config_path).unlink()

    def test_create_sample_config(self):
        """Test creation of sample configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            sample_path = f.name

        try:
            ConfigUtils.create_sample_config(sample_path)

            # Verify file was created
            assert Path(sample_path).exists()

            # Verify content
            with open(sample_path) as f:
                sample_config = yaml.safe_load(f)

            assert "version" in sample_config
            assert "ats_rules" in sample_config
            assert "output_formats" in sample_config
            assert "styling" in sample_config
            assert "processing" in sample_config

            # Verify specific values
            assert sample_config["ats_rules"]["max_line_length"] == 80
            assert "html" in sample_config["output_formats"]["enabled_formats"]
        finally:
            Path(sample_path).unlink()


class TestResultUtils:
    """Test ResultUtils utility class."""

    def test_analyze_conversion_result(self):
        """Test analysis of single conversion result."""
        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html"), Path("test.pdf")],
            processing_time=2.5,
            warnings=["Minor formatting issue"],
            errors=[],
        )

        analysis = ResultUtils.analyze_conversion_result(result)

        assert isinstance(analysis, dict)
        assert "success" in analysis
        assert "performance" in analysis
        assert "quality" in analysis
        assert "outputs" in analysis

        # Verify performance metrics
        performance = analysis["performance"]
        assert performance["processing_time"] == 2.5
        assert performance["files_per_second"] == pytest.approx(0.4, rel=1e-1)
        assert "efficiency_rating" in performance

        # Verify quality metrics
        quality = analysis["quality"]
        assert quality["output_count"] == 2
        assert quality["warning_count"] == 1
        assert quality["error_count"] == 0
        assert "quality_score" in quality

        # Verify outputs
        outputs = analysis["outputs"]
        assert len(outputs) == 2
        assert all("path" in output for output in outputs)
        assert all("format" in output for output in outputs)

    def test_analyze_batch_result(self):
        """Test analysis of batch conversion result."""
        individual_results = [
            ConversionResult(
                success=True,
                input_path=Path(f"test_{i}.md"),
                output_files=[Path(f"test_{i}.html")],
                processing_time=1.0 + i * 0.5,
                warnings=[],
                errors=[],
            )
            for i in range(3)
        ]

        batch_result = BatchConversionResult(
            total_files=3,
            successful_files=3,
            failed_files=0,
            results=individual_results,
            total_processing_time=4.5,
            summary={"success_rate": 100.0},
        )

        analysis = ResultUtils.analyze_batch_result(batch_result)

        assert isinstance(analysis, dict)
        assert "summary" in analysis
        assert "performance" in analysis
        assert "quality" in analysis
        assert "individual_results" in analysis

        # Verify summary
        summary = analysis["summary"]
        assert summary["total_files"] == 3
        assert summary["successful_files"] == 3
        assert summary["failed_files"] == 0
        assert summary["success_rate"] == 100.0

        # Verify performance
        performance = analysis["performance"]
        assert performance["total_processing_time"] == 4.5
        assert performance["average_time_per_file"] == 1.5
        assert performance["throughput"] == pytest.approx(0.67, rel=1e-1)

        # Verify individual results
        individual_analyses = analysis["individual_results"]
        assert len(individual_analyses) == 3

    def test_export_results_to_json(self):
        """Test exporting results to JSON file."""
        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html")],
            processing_time=1.5,
            warnings=[],
            errors=[],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            ResultUtils.export_results_to_json(
                result, output_path, include_analysis=True
            )

            # Verify file was created
            assert Path(output_path).exists()

            # Verify content
            with open(output_path) as f:
                exported_data = json.load(f)

            assert "type" in exported_data
            assert "timestamp" in exported_data
            assert "success" in exported_data
            assert "analysis" in exported_data

            assert exported_data["type"] == "single_result"
            assert exported_data["success"] is True
        finally:
            Path(output_path).unlink()

    def test_calculate_efficiency_rating(self):
        """Test efficiency rating calculation."""
        # Excellent performance
        fast_result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[],
            processing_time=1.0,
        )
        assert ResultUtils._calculate_efficiency_rating(fast_result) == "excellent"

        # Good performance
        good_result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[],
            processing_time=3.0,
        )
        assert ResultUtils._calculate_efficiency_rating(good_result) == "good"

        # Fair performance
        fair_result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[],
            processing_time=7.0,
        )
        assert ResultUtils._calculate_efficiency_rating(fair_result) == "fair"

        # Poor performance
        slow_result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[],
            processing_time=15.0,
        )
        assert ResultUtils._calculate_efficiency_rating(slow_result) == "poor"

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        # Perfect result
        perfect_result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html"), Path("test.pdf")],
            processing_time=1.0,
            warnings=[],
            errors=[],
        )
        perfect_score = ResultUtils._calculate_quality_score(perfect_result)
        assert perfect_score > 100  # Bonus for multiple outputs

        # Result with warnings
        warning_result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html")],
            processing_time=1.0,
            warnings=["Warning 1", "Warning 2"],
            errors=[],
        )
        warning_score = ResultUtils._calculate_quality_score(warning_result)
        assert warning_score == 90.0  # 100 - (2 * 5)

        # Result with errors
        error_result = ConversionResult(
            success=False,
            input_path=Path("test.md"),
            output_files=[],
            processing_time=1.0,
            warnings=[],
            errors=["Error 1"],
        )
        error_score = ResultUtils._calculate_quality_score(error_result)
        assert error_score == 80.0  # 100 - (1 * 20)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_system_diagnostics(self):
        """Test comprehensive system diagnostics function."""
        diagnostics = get_system_diagnostics()

        assert isinstance(diagnostics, dict)
        assert "system_info" in diagnostics
        assert "dependencies" in diagnostics
        assert "environment_issues" in diagnostics
        assert "supported_formats" in diagnostics
        assert "available_themes" in diagnostics

        # Verify supported formats
        formats = diagnostics["supported_formats"]
        assert "html" in formats
        assert "pdf" in formats
        assert "docx" in formats

        # Verify available themes
        themes = diagnostics["available_themes"]
        assert "html" in themes
        assert "pdf" in themes
        assert isinstance(themes["html"], list)

    def test_validate_setup(self):
        """Test setup validation function."""
        is_valid, issues = validate_setup()

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

        # In a properly configured environment, should be mostly valid
        if not is_valid:
            # Issues should be descriptive
            assert all(isinstance(issue, str) for issue in issues)
            assert all(len(issue) > 0 for issue in issues)


# Fixtures for pytest


@pytest.fixture
def sample_conversion_result():
    """Sample conversion result for testing."""
    return ConversionResult(
        success=True,
        input_path=Path("sample_resume.md"),
        output_files=[
            Path("sample_resume.html"),
            Path("sample_resume.pdf"),
            Path("sample_resume.docx"),
        ],
        processing_time=3.2,
        warnings=["Minor formatting adjustment"],
        errors=[],
        metadata={"theme": "professional", "format_count": 3},
    )


@pytest.fixture
def sample_batch_result(sample_conversion_result):
    """Sample batch result for testing."""
    results = [sample_conversion_result] * 3
    return BatchConversionResult(
        total_files=3,
        successful_files=3,
        failed_files=0,
        results=results,
        total_processing_time=9.6,
        summary={"success_rate": 100.0, "average_time": 3.2},
    )


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config_content = {
        "version": "1.0",
        "ats_rules": {
            "max_line_length": 80,
            "bullet_style": "•",
            "optimize_keywords": True,
        },
        "output_formats": {
            "enabled_formats": ["html", "pdf", "docx"],
            "html_theme": "professional",
        },
        "styling": {"theme": "professional", "font_size": 11},
        "processing": {"max_workers": 4, "validate_input": True},
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    return config_file
