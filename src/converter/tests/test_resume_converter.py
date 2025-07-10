"""
Unit tests for the ResumeConverter class.

Tests the main converter class functionality including initialization,
single file conversion, batch processing, configuration management,
and error handling.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ..exceptions import ConfigurationError
from ..resume_converter import ResumeConverter
from ..types import BatchConversionResult, ConversionResult


class TestResumeConverterInitialization:
    """Test ResumeConverter initialization and setup."""

    def test_default_initialization(self):
        """Test converter with default configuration."""
        converter = ResumeConverter()

        assert converter is not None
        assert converter.config_manager is not None
        assert converter.progress_callback is None
        assert hasattr(converter, "parser")
        assert hasattr(converter, "formatter")
        assert hasattr(converter, "generator")

    def test_initialization_with_config_path(self):
        """Test converter with custom configuration path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
version: "1.0"
ats_rules:
  max_line_length: 85
output_formats:
  enabled_formats: ["html"]
"""
            )
            config_path = f.name

        try:
            converter = ResumeConverter(config_path=config_path)
            assert converter.config_manager.config.ats_rules.max_line_length == 85
        finally:
            Path(config_path).unlink()

    def test_initialization_with_progress_callback(self):
        """Test converter with progress callback."""
        callback = MagicMock()
        converter = ResumeConverter(progress_callback=callback)

        assert converter.progress_callback == callback

    def test_initialization_with_invalid_config(self):
        """Test converter with invalid configuration path."""
        with pytest.raises(ConfigurationError):
            ResumeConverter(config_path="/nonexistent/config.yaml")


class TestResumeConverterConversion:
    """Test single file conversion functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_content = """
# John Doe
john@example.com | (555) 123-4567

## Summary
Software engineer with 5+ years experience.

## Experience
### Senior Developer at TechCorp
2020 - Present
- Led development of web applications
- Improved performance by 40%
"""
        self.sample_file = self.temp_dir / "test_resume.md"
        self.sample_file.write_text(self.sample_content)
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("src.converter.resume_converter.MarkdownResumeParser")
    @patch("src.converter.resume_converter.ATSFormatter")
    @patch("src.converter.resume_converter.ResumeGenerator")
    def test_successful_conversion(self, mock_generator, mock_formatter, mock_parser):
        """Test successful single file conversion."""
        # Mock components
        mock_parser_instance = MagicMock()
        mock_formatter_instance = MagicMock()
        mock_generator_instance = MagicMock()

        mock_parser.return_value = mock_parser_instance
        mock_formatter.return_value = mock_formatter_instance
        mock_generator.return_value = mock_generator_instance

        # Mock return values
        mock_resume_data = {"name": "John Doe", "email": "john@example.com"}
        mock_formatted_data = {"formatted": True, **mock_resume_data}
        mock_output_files = [
            self.output_dir / "resume.html",
            self.output_dir / "resume.pdf",
        ]

        mock_parser_instance.parse.return_value = mock_resume_data
        mock_formatter_instance.format.return_value = mock_formatted_data
        mock_generator_instance.generate_all_formats.return_value = mock_output_files

        # Create output files
        for output_file in mock_output_files:
            output_file.touch()

        # Test conversion
        converter = ResumeConverter()
        result = converter.convert(
            input_path=self.sample_file, output_dir=self.output_dir
        )

        # Verify result
        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.input_path == self.sample_file
        assert len(result.output_files) == 2
        assert result.processing_time > 0
        assert len(result.errors) == 0

        # Verify component calls
        mock_parser_instance.parse.assert_called_once()
        mock_formatter_instance.format.assert_called_once_with(mock_resume_data)
        mock_generator_instance.generate_all_formats.assert_called_once()

    def test_conversion_with_nonexistent_file(self):
        """Test conversion with non-existent input file."""
        converter = ResumeConverter()

        result = converter.convert(
            input_path=self.temp_dir / "nonexistent.md", output_dir=self.output_dir
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "does not exist" in result.errors[0].lower()

    def test_conversion_with_custom_formats(self):
        """Test conversion with custom format specification."""
        with (
            patch("src.converter.resume_converter.MarkdownResumeParser") as mock_parser,
            patch("src.converter.resume_converter.ATSFormatter") as mock_formatter,
            patch("src.converter.resume_converter.ResumeGenerator") as mock_generator,
        ):

            # Setup mocks
            mock_parser.return_value.parse.return_value = {"test": "data"}
            mock_formatter.return_value.format.return_value = {"test": "data"}
            mock_generator.return_value.generate_all_formats.return_value = [
                self.output_dir / "resume.html"
            ]

            # Create output file
            (self.output_dir / "resume.html").touch()

            converter = ResumeConverter()
            result = converter.convert(
                input_path=self.sample_file,
                output_dir=self.output_dir,
                formats=["html"],
            )

            assert result.success is True

    def test_conversion_with_config_overrides(self):
        """Test conversion with configuration overrides."""
        with (
            patch("src.converter.resume_converter.MarkdownResumeParser") as mock_parser,
            patch("src.converter.resume_converter.ATSFormatter") as mock_formatter,
            patch("src.converter.resume_converter.ResumeGenerator") as mock_generator,
        ):

            # Setup mocks
            mock_parser.return_value.parse.return_value = {"test": "data"}
            mock_formatter.return_value.format.return_value = {"test": "data"}
            mock_generator.return_value.generate_all_formats.return_value = []

            converter = ResumeConverter()

            overrides = {
                "ats_rules.max_line_length": 100,
                "output_formats.enabled_formats": ["html"],
            }

            result = converter.convert(
                input_path=self.sample_file,
                output_dir=self.output_dir,
                overrides=overrides,
            )

            # Verify overrides were applied
            assert converter.config_manager.config.ats_rules.max_line_length == 100

    def test_conversion_with_progress_callback(self):
        """Test conversion with progress tracking."""
        progress_calls = []

        def progress_callback(stage, progress, message, metadata=None):
            progress_calls.append((stage, progress, message))

        with (
            patch("src.converter.resume_converter.MarkdownResumeParser") as mock_parser,
            patch("src.converter.resume_converter.ATSFormatter") as mock_formatter,
            patch("src.converter.resume_converter.ResumeGenerator") as mock_generator,
        ):

            # Setup mocks
            mock_parser.return_value.parse.return_value = {"test": "data"}
            mock_formatter.return_value.format.return_value = {"test": "data"}
            mock_generator.return_value.generate_all_formats.return_value = []

            converter = ResumeConverter(progress_callback=progress_callback)
            result = converter.convert(
                input_path=self.sample_file, output_dir=self.output_dir
            )

            # Verify progress was tracked
            assert len(progress_calls) > 0
            assert any("validation" in call[0] for call in progress_calls)


class TestResumeConverterBatchProcessing:
    """Test batch processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()

        # Create multiple test files
        self.input_files = []
        for i in range(3):
            file_path = self.temp_dir / f"resume_{i}.md"
            file_path.write_text(
                f"# Resume {i}\ntest@example.com\n## Summary\nTest resume {i}"
            )
            self.input_files.append(file_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("src.converter.resume_converter.BatchProcessor")
    def test_batch_conversion(self, mock_batch_processor):
        """Test successful batch conversion."""
        # Mock batch processor
        mock_processor_instance = MagicMock()
        mock_batch_processor.return_value = mock_processor_instance

        # Mock batch result
        mock_batch_result = BatchConversionResult(
            total_files=3,
            successful_files=3,
            failed_files=0,
            results=[
                ConversionResult(
                    success=True,
                    input_path=file_path,
                    output_files=[self.output_dir / f"resume_{i}.html"],
                    processing_time=1.0,
                )
                for i, file_path in enumerate(self.input_files)
            ],
            total_processing_time=3.0,
            summary={"success_rate": 100.0},
        )

        mock_processor_instance.process_batch.return_value = mock_batch_result

        # Test batch conversion
        converter = ResumeConverter()
        result = converter.convert_batch(
            input_paths=self.input_files, output_dir=self.output_dir
        )

        # Verify result
        assert isinstance(result, BatchConversionResult)
        assert result.total_files == 3
        assert result.successful_files == 3
        assert result.failed_files == 0
        assert result.success_rate == 100.0

        # Verify batch processor was used
        mock_batch_processor.assert_called_once()
        mock_processor_instance.process_batch.assert_called_once()

    def test_batch_conversion_with_custom_settings(self):
        """Test batch conversion with custom settings."""
        with patch(
            "src.converter.resume_converter.BatchProcessor"
        ) as mock_batch_processor:
            mock_processor_instance = MagicMock()
            mock_batch_processor.return_value = mock_processor_instance

            mock_batch_result = BatchConversionResult(
                total_files=3,
                successful_files=3,
                failed_files=0,
                results=[],
                total_processing_time=2.0,
                summary={},
            )
            mock_processor_instance.process_batch.return_value = mock_batch_result

            converter = ResumeConverter()
            result = converter.convert_batch(
                input_paths=self.input_files,
                output_dir=self.output_dir,
                formats=["html", "pdf"],
                max_workers=2,
            )

            # Verify batch processor was called with correct arguments
            call_args = mock_processor_instance.process_batch.call_args
            assert call_args[1]["formats"] == ["html", "pdf"]
            assert call_args[1]["max_workers"] == 2


class TestResumeConverterUtilityMethods:
    """Test utility methods of ResumeConverter."""

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        converter = ResumeConverter()
        formats = converter.get_supported_formats()

        assert isinstance(formats, list)
        assert "html" in formats
        assert "pdf" in formats
        assert "docx" in formats

    def test_get_available_themes(self):
        """Test getting available themes."""
        converter = ResumeConverter()
        themes = converter.get_available_themes()

        assert isinstance(themes, dict)
        assert "html" in themes
        assert "pdf" in themes
        assert isinstance(themes["html"], list)

    def test_get_config_summary(self):
        """Test getting configuration summary."""
        converter = ResumeConverter()
        summary = converter.get_config_summary()

        assert isinstance(summary, dict)
        assert "ats_rules" in summary
        assert "output_formats" in summary
        assert "styling" in summary
        assert "processing" in summary


class TestResumeConverterErrorHandling:
    """Test error handling in ResumeConverter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_file = self.temp_dir / "test.md"
        self.sample_file.write_text("# Test Resume\ntest@example.com")
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("src.converter.resume_converter.MarkdownResumeParser")
    def test_parser_error_handling(self, mock_parser):
        """Test error handling when parser fails."""
        mock_parser.return_value.parse.side_effect = Exception("Parser failed")

        converter = ResumeConverter()
        result = converter.convert(
            input_path=self.sample_file, output_dir=self.output_dir
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "parser failed" in result.errors[0].lower()

    @patch("src.converter.resume_converter.MarkdownResumeParser")
    @patch("src.converter.resume_converter.ATSFormatter")
    def test_formatter_error_handling(self, mock_formatter, mock_parser):
        """Test error handling when formatter fails."""
        mock_parser.return_value.parse.return_value = {"test": "data"}
        mock_formatter.return_value.format.side_effect = Exception("Formatter failed")

        converter = ResumeConverter()
        result = converter.convert(
            input_path=self.sample_file, output_dir=self.output_dir
        )

        assert result.success is False
        assert len(result.errors) > 0

    @patch("src.converter.resume_converter.MarkdownResumeParser")
    @patch("src.converter.resume_converter.ATSFormatter")
    @patch("src.converter.resume_converter.ResumeGenerator")
    def test_generator_error_handling(
        self, mock_generator, mock_formatter, mock_parser
    ):
        """Test error handling when generator fails."""
        mock_parser.return_value.parse.return_value = {"test": "data"}
        mock_formatter.return_value.format.return_value = {"test": "data"}
        mock_generator.return_value.generate_all_formats.side_effect = Exception(
            "Generator failed"
        )

        converter = ResumeConverter()
        result = converter.convert(
            input_path=self.sample_file, output_dir=self.output_dir
        )

        assert result.success is False
        assert len(result.errors) > 0


# Fixtures for pytest


@pytest.fixture
def sample_resume_content():
    """Sample resume content for testing."""
    return """
# Jane Smith
jane.smith@example.com | (555) 987-6543

## Summary
Experienced software engineer with expertise in full-stack development.

## Experience

### Senior Software Engineer at TechCorp
2020 - Present | San Francisco, CA
- Led development of microservices architecture
- Improved system performance by 30%
- Mentored junior developers

### Software Engineer at StartupCo
2018 - 2020 | Remote
- Built REST APIs using Python and Django
- Implemented CI/CD pipelines
- Collaborated with cross-functional teams

## Education

### Bachelor of Science in Computer Science
University of Technology | 2014 - 2018

## Skills
- Programming: Python, JavaScript, Java
- Frameworks: Django, React, Spring Boot
- Tools: Git, Docker, AWS
"""


@pytest.fixture
def temp_resume_file(tmp_path, sample_resume_content):
    """Create a temporary resume file for testing."""
    resume_file = tmp_path / "test_resume.md"
    resume_file.write_text(sample_resume_content)
    return resume_file


@pytest.fixture
def converter_with_mocked_components():
    """Create converter with mocked components for testing."""
    with (
        patch("src.converter.resume_converter.MarkdownResumeParser") as mock_parser,
        patch("src.converter.resume_converter.ATSFormatter") as mock_formatter,
        patch("src.converter.resume_converter.ResumeGenerator") as mock_generator,
    ):

        # Setup default mock behaviors
        mock_parser.return_value.parse.return_value = {"name": "Test User"}
        mock_formatter.return_value.format.return_value = {
            "name": "Test User",
            "formatted": True,
        }
        mock_generator.return_value.generate_all_formats.return_value = []

        converter = ResumeConverter()
        converter._mock_parser = mock_parser
        converter._mock_formatter = mock_formatter
        converter._mock_generator = mock_generator

        yield converter
