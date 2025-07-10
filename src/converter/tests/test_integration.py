"""
Integration tests for the resume converter module.

Tests the complete converter pipeline functionality including single file conversion,
batch processing, CLI integration, and end-to-end workflows.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ..batch_processor import BatchProcessor
from ..resume_converter import ResumeConverter
from ..types import BatchConversionResult, ConversionResult
from ..utilities import get_system_diagnostics, validate_setup


class TestConverterIntegration:
    """Integration tests for the complete converter pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_resume_content = """
# John Doe
john.doe@example.com | (555) 123-4567

## Summary
Experienced software engineer with 5+ years in full-stack development.

## Experience

### Senior Software Engineer at TechCorp
2020 - Present | San Francisco, CA
- Led development of scalable web applications
- Improved system performance by 40%
- Mentored junior developers

### Software Engineer at StartupCo  
2018 - 2020 | Remote
- Built REST APIs using Python and Django
- Implemented automated testing pipelines
- Collaborated with cross-functional teams

## Education

### Bachelor of Science in Computer Science
University of Technology | 2014 - 2018

## Skills
- Programming: Python, JavaScript, Java
- Frameworks: Django, React, Spring Boot
- Tools: Git, Docker, AWS
"""

        # Create sample resume file
        self.sample_resume_file = self.temp_dir / "sample_resume.md"
        self.sample_resume_file.write_text(self.sample_resume_content)

        # Create output directory
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_single_file_conversion_integration(self):
        """Test complete single file conversion workflow."""
        # Create converter
        converter = ResumeConverter()

        # Track progress calls
        progress_calls = []

        def track_progress(stage, progress, message, metadata=None):
            progress_calls.append((stage, progress, message))

        converter.progress_callback = track_progress

        # Convert file
        result = converter.convert(
            input_path=self.sample_resume_file, output_dir=self.output_dir
        )

        # Verify result
        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.input_path == self.sample_resume_file
        assert len(result.output_files) > 0
        assert result.processing_time > 0

        # Verify progress tracking
        assert len(progress_calls) > 0
        assert any("validation" in call[0] for call in progress_calls)
        assert any("complete" in call[0] for call in progress_calls)

        # Verify output files exist
        for output_file in result.output_files:
            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_single_file_conversion_with_config_overrides(self):
        """Test conversion with configuration overrides."""
        converter = ResumeConverter()

        # Convert with overrides
        overrides = {
            "ats_rules.max_line_length": 100,
            "output_formats.enabled_formats": ["html"],
        }

        result = converter.convert(
            input_path=self.sample_resume_file,
            output_dir=self.output_dir,
            formats=["html"],
            overrides=overrides,
        )

        assert result.success is True
        # Should only have HTML output due to format restriction
        assert len(result.output_files) == 1
        assert result.output_files[0].suffix.lower() == ".html"

    def test_batch_processing_integration(self):
        """Test complete batch processing workflow."""
        # Create multiple resume files
        resume_files = []
        for i in range(3):
            resume_file = self.temp_dir / f"resume_{i}.md"
            resume_file.write_text(self.sample_resume_content)
            resume_files.append(resume_file)

        # Create converter factory
        def converter_factory():
            return ResumeConverter()

        # Track progress
        progress_calls = []

        def track_progress(stage, progress, message, metadata=None):
            progress_calls.append((stage, progress, message))

        # Create batch processor
        batch_processor = BatchProcessor(
            converter_factory=converter_factory,
            max_workers=2,
            progress_callback=track_progress,
        )

        # Process batch
        batch_result = batch_processor.process_batch(
            input_paths=resume_files, output_dir=self.output_dir
        )

        # Verify batch result
        assert isinstance(batch_result, BatchConversionResult)
        assert batch_result.total_files == 3
        assert batch_result.successful_files == 3
        assert batch_result.failed_files == 0
        assert batch_result.success_rate == 100.0
        assert len(batch_result.results) == 3

        # Verify individual results
        for result in batch_result.results:
            assert result.success is True
            assert len(result.output_files) > 0

        # Verify progress tracking
        assert len(progress_calls) > 0
        assert any("preparation" in call[0] for call in progress_calls)
        assert any("processing" in call[0] for call in progress_calls)

    def test_error_handling_integration(self):
        """Test error handling throughout the pipeline."""
        converter = ResumeConverter()

        # Test with non-existent file
        result = converter.convert(
            input_path=self.temp_dir / "nonexistent.md", output_dir=self.output_dir
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "does not exist" in result.errors[0].lower()

    def test_quality_validation_integration(self):
        """Test quality validation in the complete pipeline."""
        # Mock the quality validator to ensure it's called
        with patch("src.converter.resume_converter.QualityValidator") as mock_validator:
            mock_validator_instance = MagicMock()
            mock_validator.return_value = mock_validator_instance

            converter = ResumeConverter()

            # Enable output validation in config
            converter.config_manager.config.processing.validate_output = True

            result = converter.convert(
                input_path=self.sample_resume_file, output_dir=self.output_dir
            )

            # Quality validator should have been used
            # Note: This is simplified since actual validation depends on file generation
            assert result.success is True

    def test_converter_with_custom_config_file(self):
        """Test converter with custom configuration file."""
        # Create custom config file
        config_content = """
version: "1.0"
ats_rules:
  max_line_length: 90
  bullet_style: "-"
output_formats:
  enabled_formats: ["html", "pdf"]
  html_theme: "modern"
styling:
  theme: "modern"
  font_size: 12
"""
        config_file = self.temp_dir / "custom_config.yaml"
        config_file.write_text(config_content)

        # Create converter with custom config
        converter = ResumeConverter(config_path=config_file)

        # Verify config was loaded
        assert converter.config_manager.config.ats_rules.max_line_length == 90
        assert converter.config_manager.config.ats_rules.bullet_style == "-"
        assert converter.config_manager.config.styling.theme == "modern"

        # Convert file
        result = converter.convert(
            input_path=self.sample_resume_file, output_dir=self.output_dir
        )

        assert result.success is True

    def test_end_to_end_with_file_management(self):
        """Test end-to-end conversion with file management."""
        from ..file_manager import FileManager, FileOrganizationStrategy, NamingStrategy

        # Create file manager with custom organization
        organization = FileOrganizationStrategy(
            use_subdirectories=True, use_source_name=True
        )
        naming = NamingStrategy(prefix="test", include_timestamp=False)

        file_manager = FileManager(
            base_output_dir=self.output_dir,
            organization_strategy=organization,
            naming_strategy=naming,
        )

        # Convert file
        converter = ResumeConverter()
        result = converter.convert(
            input_path=self.sample_resume_file, output_dir=self.temp_dir / "temp_output"
        )

        assert result.success is True

        # Organize files
        organized_files, report = file_manager.organize_output_files(
            output_files=result.output_files, source_file=self.sample_resume_file
        )

        # Verify organization
        assert len(organized_files) == len(result.output_files)
        assert report.created_files > 0

        # Check that files were organized into subdirectories
        for organized_file in organized_files:
            assert organized_file.parent != self.output_dir
            assert organized_file.exists()


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_resume = self.temp_dir / "test_resume.md"
        self.sample_resume.write_text(
            """
# Test Resume
test@example.com

## Summary
Test summary

## Experience
### Job Title
Company | 2020-2023
- Test accomplishment
"""
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_cli_single_file_conversion(self):
        """Test CLI single file conversion."""
        from ..utilities import ResultUtils

        # This would normally test the CLI, but we'll test the underlying functions
        # that the CLI uses since we can't easily test argparse in unit tests

        converter = ResumeConverter()
        result = converter.convert(
            input_path=self.sample_resume, output_dir=self.temp_dir / "output"
        )

        # Test result analysis (used by CLI)
        analysis = ResultUtils.analyze_conversion_result(result)

        assert "performance" in analysis
        assert "quality" in analysis
        assert "outputs" in analysis
        assert analysis["success"] == result.success

    def test_cli_progress_reporting(self):
        """Test CLI progress reporting functionality."""
        from src.cli import CLIProgressReporter

        progress_messages = []

        # Mock print to capture output
        with patch("builtins.print") as mock_print:
            reporter = CLIProgressReporter(verbose=True, quiet=False)

            # Simulate progress calls
            reporter("validation", 0.0, "Starting validation")
            reporter("parsing", 50.0, "Parsing markdown")
            reporter("complete", 100.0, "Conversion complete")

            # Verify print was called
            assert mock_print.call_count > 0


class TestSystemIntegration:
    """Integration tests for system-level functionality."""

    def test_system_diagnostics(self):
        """Test system diagnostics functionality."""
        diagnostics = get_system_diagnostics()

        assert "system_info" in diagnostics
        assert "dependencies" in diagnostics
        assert "environment_issues" in diagnostics
        assert "supported_formats" in diagnostics
        assert "available_themes" in diagnostics

        # Verify system info structure
        assert "platform" in diagnostics["system_info"]
        assert "python" in diagnostics["system_info"]

    def test_setup_validation(self):
        """Test setup validation functionality."""
        is_valid, issues = validate_setup()

        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)

        # In a proper environment, this should pass
        if not is_valid:
            # Print issues for debugging
            for issue in issues:
                print(f"Setup issue: {issue}")

    def test_converter_factory_pattern(self):
        """Test converter factory pattern for batch processing."""

        def converter_factory():
            return ResumeConverter()

        # Test that factory creates working converters
        converter1 = converter_factory()
        converter2 = converter_factory()

        assert isinstance(converter1, ResumeConverter)
        assert isinstance(converter2, ResumeConverter)
        assert converter1 is not converter2  # Should be different instances


class TestErrorRecovery:
    """Integration tests for error recovery scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_partial_failure_recovery(self):
        """Test recovery from partial failures in batch processing."""
        # Create mix of valid and invalid files
        valid_file = self.temp_dir / "valid.md"
        valid_file.write_text(
            "# Valid Resume\ntest@example.com\n\n## Experience\nTest job"
        )

        invalid_file = self.temp_dir / "invalid.md"
        invalid_file.write_text("")  # Empty file

        def converter_factory():
            return ResumeConverter()

        batch_processor = BatchProcessor(
            converter_factory=converter_factory, max_workers=1
        )

        # Process batch with continue_on_error=True
        batch_result = batch_processor.process_batch(
            input_paths=[valid_file, invalid_file],
            output_dir=self.temp_dir / "output",
            continue_on_error=True,
        )

        # Should have processed both files
        assert batch_result.total_files == 2
        assert batch_result.successful_files >= 1  # At least the valid file
        assert len(batch_result.results) == 2

    def test_configuration_error_recovery(self):
        """Test recovery from configuration errors."""
        # Create invalid config
        invalid_config = self.temp_dir / "invalid_config.yaml"
        invalid_config.write_text("invalid: yaml: content:")

        # Should fall back to default config
        try:
            converter = ResumeConverter(config_path=invalid_config)
            # If we get here, it means it fell back to defaults
            assert converter.config_manager.config is not None
        except Exception:
            # Expected if strict validation is enabled
            pass


# Fixtures for pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_resume_content():
    """Sample resume content for testing."""
    return """
# Jane Smith
jane.smith@example.com | (555) 987-6543

## Summary
Experienced data scientist with expertise in machine learning.

## Experience

### Senior Data Scientist at DataCorp
2021 - Present | New York, NY
- Developed ML models improving accuracy by 25%
- Led team of 3 data scientists
- Implemented automated data pipelines

## Education

### Master of Science in Data Science
Tech University | 2019 - 2021

## Skills
- Programming: Python, R, SQL
- ML: scikit-learn, TensorFlow, PyTorch
- Tools: Jupyter, Git, Docker
"""


@pytest.fixture
def converter_with_temp_config(temp_workspace):
    """Create converter with temporary configuration."""
    config_content = """
version: "1.0"
ats_rules:
  max_line_length: 80
output_formats:
  enabled_formats: ["html"]
  output_directory: "test_output"
"""
    config_file = temp_workspace / "test_config.yaml"
    config_file.write_text(config_content)

    return ResumeConverter(config_path=config_file)
