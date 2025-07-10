"""
Unit tests for the types module.

Tests data structures, protocols, validation, and type safety
for the converter module types.
"""

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from ..types import (
    BatchConversionResult,
    ConversionResult,
    FileValidationMetrics,
    ProcessingStage,
    ValidationReport,
)


class TestConversionResult:
    """Test ConversionResult data class."""

    def test_successful_conversion_result(self):
        """Test creation of successful conversion result."""
        output_files = [Path("resume.html"), Path("resume.pdf")]

        result = ConversionResult(
            success=True,
            input_path=Path("resume.md"),
            output_files=output_files,
            processing_time=2.5,
            warnings=["Minor formatting adjustment"],
            errors=[],
            metadata={"theme": "professional", "formats": 2},
        )

        assert result.success is True
        assert result.input_path == Path("resume.md")
        assert len(result.output_files) == 2
        assert result.processing_time == 2.5
        assert len(result.warnings) == 1
        assert len(result.errors) == 0
        assert result.metadata["theme"] == "professional"

    def test_failed_conversion_result(self):
        """Test creation of failed conversion result."""
        result = ConversionResult(
            success=False,
            input_path=Path("invalid.md"),
            output_files=[],
            processing_time=0.1,
            warnings=[],
            errors=["File format not supported", "Parsing failed"],
            metadata={},
        )

        assert result.success is False
        assert result.input_path == Path("invalid.md")
        assert len(result.output_files) == 0
        assert len(result.errors) == 2
        assert "File format not supported" in result.errors
        assert "Parsing failed" in result.errors

    def test_conversion_result_default_values(self):
        """Test default values for ConversionResult."""
        result = ConversionResult(success=True, input_path=Path("test.md"))

        assert result.success is True
        assert result.input_path == Path("test.md")
        assert result.output_files == []
        assert result.processing_time == 0.0
        assert result.warnings == []
        assert result.errors == []
        assert result.metadata == {}

    def test_conversion_result_mutability(self):
        """Test that ConversionResult supports required mutations."""
        result = ConversionResult(success=True, input_path=Path("test.md"))

        # Should be able to modify fields for error tracking
        result.success = False
        result.processing_time = 5.0
        
        # Verify changes were applied
        assert result.success is False
        assert result.processing_time == 5.0

    def test_conversion_result_list_fields_mutable(self):
        """Test that list fields in ConversionResult are mutable."""
        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html")],
            warnings=["warning"],
            errors=[],
        )

        # List contents should be mutable
        result.output_files.append(Path("test.pdf"))
        result.warnings.append("another warning")
        result.errors.append("an error")

        assert len(result.output_files) == 2
        assert len(result.warnings) == 2
        assert len(result.errors) == 1

    def test_conversion_result_metadata_type(self):
        """Test metadata field type flexibility."""
        complex_metadata = {
            "theme": "professional",
            "formats": ["html", "pdf"],
            "settings": {"font_size": 12, "margins": {"top": 1, "bottom": 1}},
            "processing_stats": {
                "parse_time": 0.5,
                "format_time": 1.0,
                "generate_time": 1.5,
            },
        }

        result = ConversionResult(
            success=True, input_path=Path("test.md"), metadata=complex_metadata
        )

        assert result.metadata["theme"] == "professional"
        assert result.metadata["formats"] == ["html", "pdf"]
        assert result.metadata["settings"]["font_size"] == 12
        assert result.metadata["processing_stats"]["parse_time"] == 0.5


class TestBatchConversionResult:
    """Test BatchConversionResult data class."""

    def test_successful_batch_result(self):
        """Test creation of successful batch result."""
        individual_results = [
            ConversionResult(
                success=True,
                input_path=Path(f"resume_{i}.md"),
                output_files=[Path(f"resume_{i}.html")],
                processing_time=1.0 + i * 0.5,
            )
            for i in range(3)
        ]

        batch_result = BatchConversionResult(
            total_files=3,
            successful_files=3,
            failed_files=0,
            results=individual_results,
            total_processing_time=4.5,
            summary={"success_rate": 100.0, "average_time": 1.5},
        )

        assert batch_result.total_files == 3
        assert batch_result.successful_files == 3
        assert batch_result.failed_files == 0
        assert len(batch_result.results) == 3
        assert batch_result.total_processing_time == 4.5
        assert batch_result.summary["success_rate"] == 100.0

    def test_batch_result_with_failures(self):
        """Test batch result with some failures."""
        mixed_results = [
            ConversionResult(success=True, input_path=Path("good1.md")),
            ConversionResult(
                success=False, input_path=Path("bad.md"), errors=["Failed"]
            ),
            ConversionResult(success=True, input_path=Path("good2.md")),
        ]

        batch_result = BatchConversionResult(
            total_files=3,
            successful_files=2,
            failed_files=1,
            results=mixed_results,
            total_processing_time=3.0,
            summary={"success_rate": 66.67},
        )

        assert batch_result.total_files == 3
        assert batch_result.successful_files == 2
        assert batch_result.failed_files == 1
        assert batch_result.success_rate == pytest.approx(66.67, rel=1e-2)

    def test_batch_result_success_rate_property(self):
        """Test success_rate property calculation."""
        batch_result = BatchConversionResult(
            total_files=5,
            successful_files=4,
            failed_files=1,
            results=[],
            total_processing_time=10.0,
            summary={},
        )

        expected_rate = (4 / 5) * 100
        assert batch_result.success_rate == expected_rate

    def test_batch_result_success_rate_zero_files(self):
        """Test success_rate property with zero files."""
        batch_result = BatchConversionResult(
            total_files=0,
            successful_files=0,
            failed_files=0,
            results=[],
            total_processing_time=0.0,
            summary={},
        )

        assert batch_result.success_rate == 0.0

    def test_batch_result_default_values(self):
        """Test default values for BatchConversionResult."""
        batch_result = BatchConversionResult(
            total_files=5,
            successful_files=4,
            failed_files=1,
            results=[],
            total_processing_time=10.0,
        )

        assert batch_result.summary == {}

    def test_batch_result_mutability(self):
        """Test that BatchConversionResult supports required mutations."""
        batch_result = BatchConversionResult(
            total_files=3,
            successful_files=2,
            failed_files=1,
            results=[],
            total_processing_time=5.0,
        )

        # Should be able to modify fields for tracking
        batch_result.total_files = 5
        batch_result.total_processing_time = 10.0
        
        # Verify changes were applied
        assert batch_result.total_files == 5
        assert batch_result.total_processing_time == 10.0


class TestProcessingStage:
    """Test ProcessingStage enumeration."""

    def test_processing_stage_values(self):
        """Test ProcessingStage enumeration values."""
        # Test that expected stages exist
        assert hasattr(ProcessingStage, "VALIDATION")
        assert hasattr(ProcessingStage, "PARSING")
        assert hasattr(ProcessingStage, "FORMATTING")
        assert hasattr(ProcessingStage, "GENERATION")
        assert hasattr(ProcessingStage, "VALIDATION_OUTPUT")
        assert hasattr(ProcessingStage, "COMPLETE")

        # Test string values
        assert ProcessingStage.VALIDATION.value == "validation"
        assert ProcessingStage.PARSING.value == "parsing"
        assert ProcessingStage.FORMATTING.value == "formatting"
        assert ProcessingStage.GENERATION.value == "generation"
        assert ProcessingStage.VALIDATION_OUTPUT.value == "validation_output"
        assert ProcessingStage.COMPLETE.value == "complete"

    def test_processing_stage_iteration(self):
        """Test iteration over ProcessingStage values."""
        stages = list(ProcessingStage)

        assert len(stages) >= 6  # At least the core stages
        assert ProcessingStage.VALIDATION in stages
        assert ProcessingStage.COMPLETE in stages

    def test_processing_stage_string_representation(self):
        """Test string representation of ProcessingStage."""
        assert str(ProcessingStage.VALIDATION) == "ProcessingStage.VALIDATION"
        assert ProcessingStage.PARSING.value == "parsing"


class TestProgressCallback:
    """Test ProgressCallback protocol."""

    def test_progress_callback_protocol_compliance(self):
        """Test that functions comply with ProgressCallback protocol."""

        def simple_callback(
            stage: str,
            progress: float,
            message: str,
            metadata: dict[str, Any] | None = None,
        ) -> None:
            pass

        def detailed_callback(
            stage: str,
            progress: float,
            message: str,
            metadata: dict[str, Any] | None = None,
        ) -> None:
            pass

        def lambda_callback(stage, progress, message, metadata=None):
            None

        # These should all be valid ProgressCallback implementations
        # (The test passes if no type checker errors occur)
        callbacks = [simple_callback, detailed_callback, lambda_callback]

        for callback in callbacks:
            # Test that we can call them with the expected signature
            callback("test", 50.0, "test message")
            callback("test", 50.0, "test message", {"extra": "data"})

    def test_progress_callback_with_class_method(self):
        """Test ProgressCallback with class methods."""

        class ProgressTracker:
            def __init__(self):
                self.calls = []

            def __call__(
                self,
                stage: str,
                progress: float,
                message: str,
                metadata: dict[str, Any] | None = None,
            ) -> None:
                self.calls.append((stage, progress, message, metadata))

            def track_progress(
                self,
                stage: str,
                progress: float,
                message: str,
                metadata: dict[str, Any] | None = None,
            ) -> None:
                self.calls.append((stage, progress, message, metadata))

        tracker = ProgressTracker()

        # Both callable instance and method should work as ProgressCallback
        tracker("test", 25.0, "callable test")
        tracker.track_progress("test", 75.0, "method test", {"key": "value"})

        assert len(tracker.calls) == 2
        assert tracker.calls[0] == ("test", 25.0, "callable test", None)
        assert tracker.calls[1] == ("test", 75.0, "method test", {"key": "value"})


class TestFileValidationMetrics:
    """Test FileValidationMetrics data class."""

    def test_file_validation_metrics_creation(self):
        """Test creation of FileValidationMetrics."""
        metrics = FileValidationMetrics(
            file_path=Path("test.html"),
            format_type="html",
            file_size=1024,
            is_valid=True,
            content_score=85.5,
            ats_score=90.0,
            formatting_score=88.2,
            overall_score=87.9,
            issues=[],
            validation_details={"structure": "good", "accessibility": "excellent"},
        )

        assert metrics.file_path == Path("test.html")
        assert metrics.format_type == "html"
        assert metrics.file_size == 1024
        assert metrics.is_valid is True
        assert metrics.content_score == 85.5
        assert metrics.ats_score == 90.0
        assert metrics.formatting_score == 88.2
        assert metrics.overall_score == 87.9
        assert len(metrics.issues) == 0
        assert metrics.validation_details["structure"] == "good"

    def test_file_validation_metrics_with_issues(self):
        """Test FileValidationMetrics with validation issues."""
        issues = [
            "File size too small",
            "Missing required metadata",
            "Poor content structure",
        ]

        metrics = FileValidationMetrics(
            file_path=Path("problematic.pdf"),
            format_type="pdf",
            file_size=100,
            is_valid=False,
            content_score=45.0,
            ats_score=30.0,
            formatting_score=60.0,
            overall_score=45.0,
            issues=issues,
            validation_details={"errors": 3, "warnings": 1},
        )

        assert metrics.is_valid is False
        assert len(metrics.issues) == 3
        assert "File size too small" in metrics.issues
        assert metrics.overall_score == 45.0

    def test_file_validation_metrics_default_values(self):
        """Test default values for FileValidationMetrics."""
        metrics = FileValidationMetrics(
            file_path=Path("test.docx"),
            format_type="docx",
            file_size=2048,
            is_valid=True,
        )

        assert metrics.content_score == 0.0
        assert metrics.ats_score == 0.0
        assert metrics.formatting_score == 0.0
        assert metrics.overall_score == 0.0
        assert metrics.issues == []
        assert metrics.validation_details == {}


class TestValidationReport:
    """Test ValidationReport data class."""

    def test_validation_report_creation(self):
        """Test creation of ValidationReport."""
        file_metrics = [
            FileValidationMetrics(
                file_path=Path("test1.html"),
                format_type="html",
                file_size=1024,
                is_valid=True,
                overall_score=90.0,
            ),
            FileValidationMetrics(
                file_path=Path("test2.pdf"),
                format_type="pdf",
                file_size=2048,
                is_valid=True,
                overall_score=85.0,
            ),
            FileValidationMetrics(
                file_path=Path("test3.docx"),
                format_type="docx",
                file_size=512,
                is_valid=False,
                overall_score=40.0,
                issues=["File corrupted"],
            ),
        ]

        summary = {
            "average_scores": {"overall": 71.67},
            "quality_distribution": {"excellent": 0, "good": 2, "poor": 1},
            "common_issues": ["File corrupted"],
        }

        recommendations = [
            "Fix corrupted DOCX file",
            "Consider improving overall content quality",
        ]

        report = ValidationReport(
            file_metrics=file_metrics,
            total_files=3,
            valid_files=2,
            invalid_files=1,
            is_valid=False,
            summary=summary,
            recommendations=recommendations,
        )

        assert len(report.file_metrics) == 3
        assert report.total_files == 3
        assert report.valid_files == 2
        assert report.invalid_files == 1
        assert report.is_valid is False
        assert report.summary["average_scores"]["overall"] == 71.67
        assert len(report.recommendations) == 2

    def test_validation_report_all_valid(self):
        """Test ValidationReport with all valid files."""
        file_metrics = [
            FileValidationMetrics(
                file_path=Path(f"test{i}.html"),
                format_type="html",
                file_size=1024,
                is_valid=True,
                overall_score=90.0 + i,
            )
            for i in range(3)
        ]

        report = ValidationReport(
            file_metrics=file_metrics,
            total_files=3,
            valid_files=3,
            invalid_files=0,
            is_valid=True,
            summary={"average_scores": {"overall": 91.0}},
            recommendations=[],
        )

        assert report.is_valid is True
        assert report.valid_files == 3
        assert report.invalid_files == 0
        assert len(report.recommendations) == 0

    def test_validation_report_export_to_file(self):
        """Test exporting ValidationReport to file."""
        import json
        import tempfile

        file_metrics = [
            FileValidationMetrics(
                file_path=Path("test.html"),
                format_type="html",
                file_size=1024,
                is_valid=True,
                overall_score=85.0,
            )
        ]

        report = ValidationReport(
            file_metrics=file_metrics,
            total_files=1,
            valid_files=1,
            invalid_files=0,
            is_valid=True,
            summary={"test": "data"},
            recommendations=["Keep up the good work"],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report_path = f.name

        try:
            report.export_to_file(report_path)

            # Verify file was created and contains expected data
            assert Path(report_path).exists()

            with open(report_path) as f:
                exported_data = json.load(f)

            assert "summary" in exported_data
            assert "file_metrics" in exported_data
            assert "recommendations" in exported_data
            assert exported_data["summary"]["total_files"] == 1
            assert exported_data["summary"]["is_valid"] is True
        finally:
            Path(report_path).unlink()

    def test_validation_report_default_values(self):
        """Test default values for ValidationReport."""
        report = ValidationReport(
            file_metrics=[],
            total_files=0,
            valid_files=0,
            invalid_files=0,
            is_valid=True,
        )

        assert report.summary == {}
        assert report.recommendations == []


class TestTypeValidation:
    """Test type validation and edge cases."""

    def test_path_type_validation(self):
        """Test that Path objects work correctly in types."""
        # Test with string paths (should be converted)
        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html"), Path("test.pdf")],
        )

        assert isinstance(result.input_path, Path)
        assert all(isinstance(f, Path) for f in result.output_files)

    def test_numeric_type_validation(self):
        """Test numeric type validation."""
        # Test with various numeric types
        result = ConversionResult(
            success=True, input_path=Path("test.md"), processing_time=2.5  # float
        )

        assert result.processing_time == 2.5
        assert isinstance(result.processing_time, float)

        # Test with int (should work too)
        result2 = ConversionResult(
            success=True, input_path=Path("test.md"), processing_time=3  # int
        )

        assert result2.processing_time == 3

    def test_list_type_validation(self):
        """Test list type validation."""
        # Test with different list types
        result = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[],  # empty list
            warnings=["warning1", "warning2"],  # string list
            errors=[],  # empty list
        )

        assert isinstance(result.output_files, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.errors, list)
        assert len(result.warnings) == 2

    def test_optional_type_validation(self):
        """Test optional type handling."""
        # Test with None values where allowed
        metrics = FileValidationMetrics(
            file_path=Path("test.html"),
            format_type="html",
            file_size=1024,
            is_valid=True,
            validation_details={},  # Can be empty dict
        )

        assert metrics.validation_details == {}

        # Test with actual values
        metrics2 = FileValidationMetrics(
            file_path=Path("test.html"),
            format_type="html",
            file_size=1024,
            is_valid=True,
            validation_details={"key": "value"},
        )

        assert metrics2.validation_details["key"] == "value"


# Fixtures for pytest


@pytest.fixture
def sample_conversion_result():
    """Sample ConversionResult for testing."""
    return ConversionResult(
        success=True,
        input_path=Path("sample.md"),
        output_files=[Path("sample.html"), Path("sample.pdf"), Path("sample.docx")],
        processing_time=2.5,
        warnings=["Minor formatting issue"],
        errors=[],
        metadata={"theme": "professional", "formats": 3, "quality_score": 85.5},
    )


@pytest.fixture
def sample_batch_result(sample_conversion_result):
    """Sample BatchConversionResult for testing."""
    return BatchConversionResult(
        total_files=3,
        successful_files=2,
        failed_files=1,
        results=[
            sample_conversion_result,
            ConversionResult(success=True, input_path=Path("test2.md")),
            ConversionResult(
                success=False, input_path=Path("test3.md"), errors=["Conversion failed"]
            ),
        ],
        total_processing_time=7.5,
        summary={
            "success_rate": 66.67,
            "average_time": 2.5,
            "total_warnings": 1,
            "total_errors": 1,
        },
    )


@pytest.fixture
def sample_file_metrics():
    """Sample FileValidationMetrics for testing."""
    return [
        FileValidationMetrics(
            file_path=Path("high_quality.html"),
            format_type="html",
            file_size=2048,
            is_valid=True,
            content_score=90.0,
            ats_score=88.0,
            formatting_score=92.0,
            overall_score=90.0,
            issues=[],
            validation_details={"structure": "excellent"},
        ),
        FileValidationMetrics(
            file_path=Path("medium_quality.pdf"),
            format_type="pdf",
            file_size=1024,
            is_valid=True,
            content_score=75.0,
            ats_score=80.0,
            formatting_score=70.0,
            overall_score=75.0,
            issues=["Minor formatting issues"],
            validation_details={"structure": "good"},
        ),
        FileValidationMetrics(
            file_path=Path("low_quality.docx"),
            format_type="docx",
            file_size=512,
            is_valid=False,
            content_score=40.0,
            ats_score=35.0,
            formatting_score=45.0,
            overall_score=40.0,
            issues=["Poor content structure", "Missing metadata"],
            validation_details={"structure": "poor", "errors": 2},
        ),
    ]


@pytest.fixture
def sample_validation_report(sample_file_metrics):
    """Sample ValidationReport for testing."""
    return ValidationReport(
        file_metrics=sample_file_metrics,
        total_files=3,
        valid_files=2,
        invalid_files=1,
        is_valid=False,
        summary={
            "average_scores": {
                "overall": 68.33,
                "content": 68.33,
                "ats": 67.67,
                "formatting": 69.0,
            },
            "quality_distribution": {"excellent": 1, "good": 1, "poor": 1},
            "common_issues": ["Minor formatting issues", "Poor content structure"],
        },
        recommendations=[
            "Improve content structure in low-quality files",
            "Address formatting inconsistencies",
            "Add missing metadata to DOCX files",
        ],
    )
