"""
Unit tests for the BatchProcessor class.

Tests batch processing functionality including concurrent processing,
error handling, progress tracking, and resource management.
"""

import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ..batch_processor import BatchProcessor
from ..exceptions import ConversionError, ProcessingError
from ..types import BatchConversionResult, ConversionResult


class TestBatchProcessorInitialization:
    """Test BatchProcessor initialization and configuration."""

    def test_default_initialization(self):
        """Test batch processor with default settings."""

        def converter_factory():
            return MagicMock()

        processor = BatchProcessor(converter_factory=converter_factory)

        assert processor.converter_factory == converter_factory
        assert processor.max_workers == 4  # Default value
        assert processor.progress_callback is None

    def test_initialization_with_custom_settings(self):
        """Test batch processor with custom settings."""

        def converter_factory():
            return MagicMock()

        def progress_callback(stage, progress, message, metadata=None):
            pass

        processor = BatchProcessor(
            converter_factory=converter_factory,
            max_workers=8,
            progress_callback=progress_callback,
        )

        assert processor.converter_factory == converter_factory
        assert processor.max_workers == 8
        assert processor.progress_callback == progress_callback

    def test_initialization_with_invalid_max_workers(self):
        """Test batch processor with invalid max_workers."""

        def converter_factory():
            return MagicMock()

        # Test with zero workers
        processor = BatchProcessor(converter_factory=converter_factory, max_workers=0)
        assert processor.max_workers == 1  # Should be adjusted to minimum

        # Test with negative workers
        processor = BatchProcessor(converter_factory=converter_factory, max_workers=-1)
        assert processor.max_workers == 1  # Should be adjusted to minimum


class TestBatchProcessorProcessing:
    """Test batch processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()

        # Create test input files
        self.input_files = []
        for i in range(3):
            file_path = self.temp_dir / f"resume_{i}.md"
            file_path.write_text(
                f"# Resume {i}\ntest{i}@example.com\n## Summary\nTest resume {i}"
            )
            self.input_files.append(file_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_successful_batch_processing(self):
        """Test successful batch processing of multiple files."""
        # Mock converter factory
        mock_results = [
            ConversionResult(
                success=True,
                input_path=file_path,
                output_files=[self.output_dir / f"resume_{i}.html"],
                processing_time=1.0 + i * 0.1,
            )
            for i, file_path in enumerate(self.input_files)
        ]

        def converter_factory():
            mock_converter = MagicMock()
            mock_converter.convert.side_effect = mock_results
            return mock_converter

        # Track progress calls
        progress_calls = []

        def progress_callback(stage, progress, message, metadata=None):
            progress_calls.append((stage, progress, message, metadata))

        processor = BatchProcessor(
            converter_factory=converter_factory,
            max_workers=2,
            progress_callback=progress_callback,
        )

        result = processor.process_batch(
            input_paths=self.input_files, output_dir=self.output_dir
        )

        # Verify batch result
        assert isinstance(result, BatchConversionResult)
        assert result.total_files == 3
        assert result.successful_files == 3
        assert result.failed_files == 0
        assert result.success_rate == 100.0
        assert result.total_processing_time > 0
        assert len(result.results) == 3

        # Verify all individual results are successful
        for individual_result in result.results:
            assert individual_result.success is True

        # Verify progress tracking
        assert len(progress_calls) > 0
        assert any("preparation" in call[0] for call in progress_calls)
        assert any("processing" in call[0] for call in progress_calls)

    def test_batch_processing_with_failures(self):
        """Test batch processing with some failures."""

        # Mock converter with mixed results
        def converter_factory():
            mock_converter = MagicMock()

            def convert_side_effect(input_path, **kwargs):
                if "resume_1" in str(input_path):
                    # Simulate failure for second file
                    return ConversionResult(
                        success=False,
                        input_path=input_path,
                        output_files=[],
                        processing_time=0.5,
                        errors=["Conversion failed"],
                    )
                else:
                    # Success for other files
                    return ConversionResult(
                        success=True,
                        input_path=input_path,
                        output_files=[self.output_dir / f"{input_path.stem}.html"],
                        processing_time=1.0,
                    )

            mock_converter.convert.side_effect = convert_side_effect
            return mock_converter

        processor = BatchProcessor(converter_factory=converter_factory)

        result = processor.process_batch(
            input_paths=self.input_files,
            output_dir=self.output_dir,
            continue_on_error=True,
        )

        # Verify batch result
        assert result.total_files == 3
        assert result.successful_files == 2
        assert result.failed_files == 1
        assert result.success_rate == pytest.approx(66.67, rel=1e-2)

        # Verify individual results
        failed_results = [r for r in result.results if not r.success]
        assert len(failed_results) == 1
        assert "resume_1" in str(failed_results[0].input_path)

    def test_batch_processing_fail_fast(self):
        """Test batch processing with fail_fast enabled."""

        def converter_factory():
            mock_converter = MagicMock()

            def convert_side_effect(input_path, **kwargs):
                if "resume_1" in str(input_path):
                    raise ConversionError("Critical conversion error")
                return ConversionResult(
                    success=True,
                    input_path=input_path,
                    output_files=[],
                    processing_time=1.0,
                )

            mock_converter.convert.side_effect = convert_side_effect
            return mock_converter

        processor = BatchProcessor(converter_factory=converter_factory)

        with pytest.raises(ProcessingError):
            processor.process_batch(
                input_paths=self.input_files, output_dir=self.output_dir, fail_fast=True
            )

    def test_batch_processing_with_custom_formats(self):
        """Test batch processing with custom output formats."""

        def converter_factory():
            mock_converter = MagicMock()
            mock_converter.convert.return_value = ConversionResult(
                success=True,
                input_path=Path("test.md"),
                output_files=[],
                processing_time=1.0,
            )
            return mock_converter

        processor = BatchProcessor(converter_factory=converter_factory)

        result = processor.process_batch(
            input_paths=self.input_files,
            output_dir=self.output_dir,
            formats=["html", "pdf"],
        )

        # Verify convert was called with correct formats
        mock_converter = processor.converter_factory()
        for call_args in mock_converter.convert.call_args_list:
            assert call_args[1]["formats"] == ["html", "pdf"]

    def test_batch_processing_progress_tracking(self):
        """Test detailed progress tracking during batch processing."""

        def converter_factory():
            mock_converter = MagicMock()

            def slow_convert(*args, **kwargs):
                time.sleep(0.1)  # Simulate processing time
                return ConversionResult(
                    success=True,
                    input_path=args[0],
                    output_files=[],
                    processing_time=0.1,
                )

            mock_converter.convert.side_effect = slow_convert
            return mock_converter

        progress_calls = []

        def progress_callback(stage, progress, message, metadata=None):
            progress_calls.append((stage, progress, message, metadata))

        processor = BatchProcessor(
            converter_factory=converter_factory,
            max_workers=1,  # Single worker for predictable progress
            progress_callback=progress_callback,
        )

        result = processor.process_batch(
            input_paths=self.input_files, output_dir=self.output_dir
        )

        # Verify progress tracking
        assert len(progress_calls) > 0

        # Check for specific progress stages
        stages = [call[0] for call in progress_calls]
        assert "preparation" in stages
        assert "processing" in stages
        assert "batch_complete" in stages

        # Verify progress percentages increase
        processing_calls = [call for call in progress_calls if call[0] == "processing"]
        if len(processing_calls) > 1:
            assert processing_calls[0][1] <= processing_calls[-1][1]


class TestBatchProcessorConcurrency:
    """Test concurrent processing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_files = []
        for i in range(5):
            file_path = self.temp_dir / f"resume_{i}.md"
            file_path.write_text(f"# Resume {i}")
            self.input_files.append(file_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_concurrent_processing_performance(self):
        """Test that concurrent processing is faster than sequential."""

        def converter_factory():
            mock_converter = MagicMock()

            def slow_convert(*args, **kwargs):
                time.sleep(0.1)  # Simulate processing time
                return ConversionResult(
                    success=True,
                    input_path=args[0],
                    output_files=[],
                    processing_time=0.1,
                )

            mock_converter.convert.side_effect = slow_convert
            return mock_converter

        # Test with multiple workers
        start_time = time.time()
        processor_concurrent = BatchProcessor(
            converter_factory=converter_factory, max_workers=3
        )
        result_concurrent = processor_concurrent.process_batch(
            input_paths=self.input_files
        )
        concurrent_time = time.time() - start_time

        # Test with single worker
        start_time = time.time()
        processor_sequential = BatchProcessor(
            converter_factory=converter_factory, max_workers=1
        )
        result_sequential = processor_sequential.process_batch(
            input_paths=self.input_files
        )
        sequential_time = time.time() - start_time

        # Concurrent should be faster (allowing some tolerance)
        assert concurrent_time < sequential_time * 0.8

        # Both should process all files successfully
        assert result_concurrent.successful_files == 5
        assert result_sequential.successful_files == 5

    def test_worker_count_optimization(self):
        """Test automatic worker count optimization."""

        def converter_factory():
            return MagicMock()

        # Test with more workers than files
        processor = BatchProcessor(converter_factory=converter_factory, max_workers=10)

        # Should automatically adjust worker count
        with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__.return_value.map.return_value = []

            processor.process_batch(input_paths=self.input_files[:2])

            # Should use at most as many workers as files
            call_args = mock_executor.call_args
            actual_workers = call_args[1]["max_workers"]
            assert actual_workers <= len(self.input_files[:2])


class TestBatchProcessorErrorHandling:
    """Test error handling in batch processing."""

    def test_converter_factory_failure(self):
        """Test handling of converter factory failures."""

        def failing_converter_factory():
            raise Exception("Factory failed")

        processor = BatchProcessor(converter_factory=failing_converter_factory)

        with pytest.raises(ProcessingError):
            processor.process_batch(input_paths=[Path("test.md")])

    def test_individual_converter_failure(self):
        """Test handling of individual converter failures."""

        def converter_factory():
            mock_converter = MagicMock()
            mock_converter.convert.side_effect = Exception("Converter failed")
            return mock_converter

        processor = BatchProcessor(converter_factory=converter_factory)

        result = processor.process_batch(
            input_paths=[Path("test.md")], continue_on_error=True
        )

        assert result.failed_files == 1
        assert result.successful_files == 0
        assert len(result.results) == 1
        assert not result.results[0].success

    def test_resource_cleanup_on_error(self):
        """Test that resources are cleaned up on error."""

        def converter_factory():
            mock_converter = MagicMock()
            mock_converter.convert.side_effect = Exception("Critical error")
            return mock_converter

        processor = BatchProcessor(converter_factory=converter_factory)

        with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
            mock_context = mock_executor.return_value.__enter__.return_value
            mock_context.map.side_effect = Exception("Executor error")

            with pytest.raises(ProcessingError):
                processor.process_batch(input_paths=[Path("test.md")], fail_fast=True)

            # Verify executor context was properly handled
            mock_executor.return_value.__exit__.assert_called_once()


class TestBatchProcessorResourceManagement:
    """Test resource management in batch processing."""

    def test_memory_usage_with_large_batch(self):
        """Test memory management with large batch sizes."""
        # Create many input files
        temp_dir = Path(tempfile.mkdtemp())
        try:
            large_input_files = []
            for i in range(20):
                file_path = temp_dir / f"resume_{i}.md"
                file_path.write_text(f"# Resume {i}")
                large_input_files.append(file_path)

            def converter_factory():
                mock_converter = MagicMock()
                mock_converter.convert.return_value = ConversionResult(
                    success=True,
                    input_path=Path("test.md"),
                    output_files=[],
                    processing_time=0.01,
                )
                return mock_converter

            processor = BatchProcessor(
                converter_factory=converter_factory, max_workers=4
            )

            result = processor.process_batch(input_paths=large_input_files)

            # Should handle large batch without issues
            assert result.total_files == 20
            assert result.successful_files == 20

        finally:
            shutil.rmtree(temp_dir)

    def test_thread_pool_lifecycle(self):
        """Test proper thread pool lifecycle management."""

        def converter_factory():
            return MagicMock()

        processor = BatchProcessor(converter_factory=converter_factory)

        with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
            mock_context = mock_executor.return_value.__enter__.return_value
            mock_context.map.return_value = []

            processor.process_batch(input_paths=[Path("test.md")])

            # Verify executor was properly created and cleaned up
            mock_executor.assert_called_once()
            mock_executor.return_value.__enter__.assert_called_once()
            mock_executor.return_value.__exit__.assert_called_once()


# Fixtures for pytest


@pytest.fixture
def sample_batch_files(tmp_path):
    """Create sample files for batch testing."""
    files = []
    for i in range(3):
        file_path = tmp_path / f"resume_{i}.md"
        file_path.write_text(
            f"""
# Resume {i}
user{i}@example.com | (555) 123-456{i}

## Summary
Test resume {i} for batch processing.

## Experience
### Job {i}
Company {i} | 2020 - Present
- Achievement {i}
"""
        )
        files.append(file_path)
    return files


@pytest.fixture
def mock_converter_factory():
    """Create a mock converter factory for testing."""

    def factory():
        mock_converter = MagicMock()
        mock_converter.convert.return_value = ConversionResult(
            success=True,
            input_path=Path("test.md"),
            output_files=[Path("test.html")],
            processing_time=0.1,
        )
        return mock_converter

    return factory


@pytest.fixture
def batch_processor(mock_converter_factory):
    """Create a batch processor for testing."""
    return BatchProcessor(converter_factory=mock_converter_factory, max_workers=2)
