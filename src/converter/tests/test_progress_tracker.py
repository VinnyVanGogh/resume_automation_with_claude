"""
Unit tests for the ProgressTracker class.

Tests progress tracking functionality including stage management,
time estimation, callback handling, and operation history.
"""

import time
from unittest.mock import MagicMock

import pytest

from ..progress_tracker import ProgressTracker


class TestProgressTrackerInitialization:
    """Test ProgressTracker initialization and setup."""

    def test_default_initialization(self):
        """Test progress tracker with default settings."""
        tracker = ProgressTracker()

        assert tracker is not None
        assert tracker.current_stage is None
        assert tracker.total_stages == 0
        assert tracker.current_progress == 0.0
        assert len(tracker.stage_history) == 0

    def test_initialization_with_callback(self):
        """Test progress tracker with callback function."""
        callback = MagicMock()
        tracker = ProgressTracker(callback=callback)

        assert tracker.callback == callback

    def test_initialization_with_stage_list(self):
        """Test progress tracker with predefined stages."""
        stages = ["validation", "parsing", "formatting", "generation"]
        tracker = ProgressTracker(stages=stages)

        assert tracker.total_stages == 4
        assert tracker.stages == stages

    def test_initialization_with_custom_settings(self):
        """Test progress tracker with custom settings."""
        callback = MagicMock()
        stages = ["stage1", "stage2"]

        tracker = ProgressTracker(
            callback=callback, stages=stages, enable_timing=True, enable_estimates=True
        )

        assert tracker.callback == callback
        assert tracker.stages == stages
        assert tracker.total_stages == 2


class TestProgressTrackerStageManagement:
    """Test stage management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.callback = MagicMock()
        self.tracker = ProgressTracker(callback=self.callback)

    def test_start_stage(self):
        """Test starting a new stage."""
        stage_name = "validation"
        message = "Starting input validation"

        self.tracker.start_stage(stage_name, message)

        assert self.tracker.current_stage == stage_name
        assert self.tracker.current_progress == 0.0
        assert len(self.tracker.stage_history) == 1

        # Verify callback was called
        self.callback.assert_called_once()
        call_args = self.callback.call_args
        assert call_args[0][0] == stage_name  # stage
        assert call_args[0][1] == 0.0  # progress
        assert call_args[0][2] == message  # message

    def test_update_stage_progress(self):
        """Test updating progress within a stage."""
        # Start a stage first
        self.tracker.start_stage("processing", "Starting processing")
        self.callback.reset_mock()

        # Update progress
        progress = 50.0
        message = "Processing 50% complete"
        metadata = {"items_processed": 5, "total_items": 10}

        self.tracker.update_stage_progress(progress, message, metadata)

        assert self.tracker.current_progress == progress

        # Verify callback was called with updated progress
        self.callback.assert_called_once()
        call_args = self.callback.call_args
        assert call_args[0][0] == "processing"  # stage
        assert call_args[0][1] == progress  # progress
        assert call_args[0][2] == message  # message
        assert call_args[1]["metadata"] == metadata  # metadata

    def test_complete_stage(self):
        """Test completing a stage."""
        # Start a stage
        self.tracker.start_stage("generation", "Starting generation")
        self.tracker.update_stage_progress(75.0, "Generation in progress")
        self.callback.reset_mock()

        # Complete the stage
        completion_message = "Generation completed successfully"
        self.tracker.complete_stage(completion_message)

        assert self.tracker.current_progress == 100.0

        # Verify callback was called for completion
        self.callback.assert_called_once()
        call_args = self.callback.call_args
        assert call_args[0][0] == "generation"  # stage
        assert call_args[0][1] == 100.0  # progress
        assert call_args[0][2] == completion_message  # message

        # Verify stage history
        assert len(self.tracker.stage_history) == 1
        stage_record = self.tracker.stage_history[0]
        assert stage_record["stage"] == "generation"
        assert stage_record["completed"] is True
        assert "start_time" in stage_record
        assert "end_time" in stage_record

    def test_multiple_stages(self):
        """Test tracking multiple sequential stages."""
        stages = ["validation", "parsing", "formatting"]

        for i, stage in enumerate(stages):
            self.tracker.start_stage(stage, f"Starting {stage}")
            self.tracker.update_stage_progress(50.0, f"{stage} halfway")
            self.tracker.complete_stage(f"{stage} completed")

        # Verify all stages were tracked
        assert len(self.tracker.stage_history) == 3
        for i, stage_record in enumerate(self.tracker.stage_history):
            assert stage_record["stage"] == stages[i]
            assert stage_record["completed"] is True

    def test_stage_without_callback(self):
        """Test stage management without callback."""
        tracker = ProgressTracker()  # No callback

        # Should not raise errors
        tracker.start_stage("test_stage", "Test message")
        tracker.update_stage_progress(50.0, "Test progress")
        tracker.complete_stage("Test complete")

        assert tracker.current_stage == "test_stage"
        assert tracker.current_progress == 100.0


class TestProgressTrackerTiming:
    """Test timing and estimation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker(enable_timing=True, enable_estimates=True)

    def test_stage_timing(self):
        """Test timing measurement for stages."""
        stage_name = "timed_stage"

        # Start stage
        start_time = time.time()
        self.tracker.start_stage(stage_name, "Starting timed stage")

        # Simulate some processing time
        time.sleep(0.1)

        # Complete stage
        self.tracker.complete_stage("Timed stage completed")
        end_time = time.time()

        # Verify timing was recorded
        stage_record = self.tracker.stage_history[0]
        assert "start_time" in stage_record
        assert "end_time" in stage_record
        assert "duration" in stage_record

        # Verify duration is reasonable
        recorded_duration = stage_record["duration"]
        expected_duration = end_time - start_time
        assert abs(recorded_duration - expected_duration) < 0.05  # 50ms tolerance

    def test_overall_operation_timing(self):
        """Test overall operation timing."""
        # Start operation
        self.tracker.start_operation("test_operation")

        # Process multiple stages
        for i in range(3):
            self.tracker.start_stage(f"stage_{i}", f"Stage {i}")
            time.sleep(0.05)  # Small delay
            self.tracker.complete_stage(f"Stage {i} completed")

        # End operation
        self.tracker.end_operation()

        # Verify overall timing
        operation_duration = self.tracker.get_operation_duration()
        assert operation_duration > 0.1  # Should be at least 150ms
        assert operation_duration < 1.0  # But not unreasonably long

    def test_time_estimation(self):
        """Test time estimation functionality."""
        # Start with predefined stages
        stages = ["stage1", "stage2", "stage3"]
        tracker = ProgressTracker(stages=stages, enable_estimates=True)

        # Complete first stage with known duration
        tracker.start_stage("stage1", "Starting stage 1")
        time.sleep(0.1)
        tracker.complete_stage("Stage 1 completed")

        # Start second stage and get estimate
        tracker.start_stage("stage2", "Starting stage 2")
        tracker.update_stage_progress(50.0, "Stage 2 halfway")

        estimate = tracker.get_time_estimate()

        # Estimate should be reasonable (more than current time, but not too much)
        assert estimate > 0.1  # Should take at least as long as stage 1
        assert estimate < 1.0  # But not unreasonably long

    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        stages = ["fast_stage", "slow_stage"]
        tracker = ProgressTracker(stages=stages, enable_timing=True)

        # Fast stage
        tracker.start_stage("fast_stage", "Fast stage")
        time.sleep(0.05)
        tracker.complete_stage("Fast stage done")

        # Slow stage
        tracker.start_stage("slow_stage", "Slow stage")
        time.sleep(0.15)
        tracker.complete_stage("Slow stage done")

        # Get performance metrics
        metrics = tracker.get_performance_metrics()

        assert "total_duration" in metrics
        assert "average_stage_duration" in metrics
        assert "fastest_stage" in metrics
        assert "slowest_stage" in metrics

        assert metrics["fastest_stage"]["stage"] == "fast_stage"
        assert metrics["slowest_stage"]["stage"] == "slow_stage"


class TestProgressTrackerCallbacks:
    """Test callback functionality and metadata handling."""

    def test_callback_with_metadata(self):
        """Test callback invocation with metadata."""
        callback = MagicMock()
        tracker = ProgressTracker(callback=callback)

        metadata = {
            "files_processed": 3,
            "total_files": 10,
            "current_file": "resume.md",
            "errors": 0,
        }

        tracker.start_stage("processing", "Processing files")
        tracker.update_stage_progress(30.0, "Processing file 3/10", metadata)

        # Verify callback was called with metadata
        assert callback.call_count == 2  # start_stage + update_stage_progress

        # Check the update call
        update_call = callback.call_args_list[1]
        assert update_call[1]["metadata"] == metadata

    def test_callback_error_handling(self):
        """Test error handling in callback invocation."""

        # Create callback that raises an error
        def failing_callback(stage, progress, message, metadata=None):
            raise Exception("Callback failed")

        tracker = ProgressTracker(callback=failing_callback)

        # Should not raise error, just log and continue
        tracker.start_stage("test_stage", "Test message")
        tracker.update_stage_progress(50.0, "Test progress")
        tracker.complete_stage("Test complete")

        # Tracker should still function normally
        assert tracker.current_stage == "test_stage"
        assert tracker.current_progress == 100.0

    def test_multiple_callback_invocations(self):
        """Test multiple callback invocations during operation."""
        callback = MagicMock()
        tracker = ProgressTracker(callback=callback)

        # Simulate a complete operation
        tracker.start_stage("validation", "Starting validation")
        tracker.update_stage_progress(25.0, "Validating input")
        tracker.update_stage_progress(75.0, "Validation almost done")
        tracker.complete_stage("Validation completed")

        tracker.start_stage("processing", "Starting processing")
        tracker.update_stage_progress(50.0, "Processing halfway")
        tracker.complete_stage("Processing completed")

        # Verify all callback invocations
        assert callback.call_count == 6  # 2 starts + 3 updates + 1 completion

        # Verify progress sequence
        progress_values = [call[0][1] for call in callback.call_args_list]
        expected_progress = [0.0, 25.0, 75.0, 100.0, 0.0, 50.0, 100.0]
        assert progress_values == expected_progress


class TestProgressTrackerUtilities:
    """Test utility methods and reporting."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker(enable_timing=True)

        # Simulate completed operation
        stages = ["validation", "parsing", "generation"]
        for stage in stages:
            self.tracker.start_stage(stage, f"Starting {stage}")
            time.sleep(0.02)  # Small delay
            self.tracker.complete_stage(f"{stage} completed")

    def test_get_progress_summary(self):
        """Test getting progress summary."""
        summary = self.tracker.get_progress_summary()

        assert isinstance(summary, dict)
        assert "current_stage" in summary
        assert "total_stages" in summary
        assert "completed_stages" in summary
        assert "overall_progress" in summary
        assert "stage_history" in summary

        assert summary["completed_stages"] == 3
        assert summary["overall_progress"] == 100.0

    def test_get_stage_details(self):
        """Test getting details for specific stage."""
        stage_details = self.tracker.get_stage_details("parsing")

        assert stage_details is not None
        assert stage_details["stage"] == "parsing"
        assert stage_details["completed"] is True
        assert "start_time" in stage_details
        assert "end_time" in stage_details
        assert "duration" in stage_details

    def test_export_progress_report(self):
        """Test exporting progress report."""
        import json
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report_path = f.name

        try:
            self.tracker.export_progress_report(report_path)

            # Verify file was created
            assert Path(report_path).exists()

            # Verify content
            with open(report_path) as f:
                report_data = json.load(f)

            assert "summary" in report_data
            assert "stage_history" in report_data
            assert "performance_metrics" in report_data
            assert report_data["summary"]["completed_stages"] == 3
        finally:
            Path(report_path).unlink()

    def test_reset_tracker(self):
        """Test resetting tracker state."""
        # Verify initial state has data
        assert len(self.tracker.stage_history) == 3
        assert self.tracker.current_stage is not None

        # Reset tracker
        self.tracker.reset()

        # Verify reset state
        assert len(self.tracker.stage_history) == 0
        assert self.tracker.current_stage is None
        assert self.tracker.current_progress == 0.0
        assert self.tracker.total_stages == 0


class TestProgressTrackerBatchOperations:
    """Test progress tracking for batch operations."""

    def test_batch_progress_tracking(self):
        """Test progress tracking across batch operations."""
        callback = MagicMock()
        tracker = ProgressTracker(callback=callback)

        total_items = 5
        tracker.start_batch_operation("batch_conversion", total_items)

        # Process items in batch
        for i in range(total_items):
            tracker.start_batch_item(f"item_{i}", f"Processing item {i}")
            tracker.update_batch_progress(
                items_completed=i, message=f"Completed {i}/{total_items} items"
            )
            tracker.complete_batch_item(f"Item {i} completed")

        tracker.complete_batch_operation("Batch conversion completed")

        # Verify batch tracking
        batch_summary = tracker.get_batch_summary()
        assert batch_summary["total_items"] == total_items
        assert batch_summary["completed_items"] == total_items
        assert batch_summary["success_rate"] == 100.0

    def test_batch_progress_with_failures(self):
        """Test batch progress tracking with some failures."""
        tracker = ProgressTracker()

        total_items = 4
        tracker.start_batch_operation("batch_with_failures", total_items)

        # Process items with some failures
        for i in range(total_items):
            tracker.start_batch_item(f"item_{i}", f"Processing item {i}")

            if i == 2:  # Simulate failure on item 2
                tracker.fail_batch_item(f"Item {i} failed", error="Processing error")
            else:
                tracker.complete_batch_item(f"Item {i} completed")

        tracker.complete_batch_operation("Batch completed with some failures")

        # Verify batch tracking with failures
        batch_summary = tracker.get_batch_summary()
        assert batch_summary["total_items"] == 4
        assert batch_summary["completed_items"] == 3
        assert batch_summary["failed_items"] == 1
        assert batch_summary["success_rate"] == 75.0


class TestProgressTrackerErrorHandling:
    """Test error handling in progress tracking."""

    def test_invalid_progress_values(self):
        """Test handling of invalid progress values."""
        tracker = ProgressTracker()

        tracker.start_stage("test_stage", "Test stage")

        # Test negative progress
        tracker.update_stage_progress(-10.0, "Invalid negative progress")
        assert tracker.current_progress == 0.0  # Should be clamped to 0

        # Test progress > 100
        tracker.update_stage_progress(150.0, "Invalid high progress")
        assert tracker.current_progress == 100.0  # Should be clamped to 100

    def test_stage_operations_without_current_stage(self):
        """Test stage operations when no current stage is set."""
        tracker = ProgressTracker()

        # These operations should handle missing current stage gracefully
        tracker.update_stage_progress(50.0, "Update without stage")
        tracker.complete_stage("Complete without stage")

        # Should not raise errors and should have sensible state
        assert tracker.current_stage is None

    def test_concurrent_access_safety(self):
        """Test thread safety of progress tracker."""
        import threading

        callback = MagicMock()
        tracker = ProgressTracker(callback=callback)

        def worker(worker_id):
            for i in range(5):
                tracker.start_stage(
                    f"stage_{worker_id}_{i}", f"Worker {worker_id} stage {i}"
                )
                time.sleep(0.01)
                tracker.complete_stage(f"Worker {worker_id} stage {i} done")

        # Start multiple worker threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify that all stages were tracked (though order may vary)
        assert len(tracker.stage_history) == 15  # 3 workers × 5 stages


# Fixtures for pytest


@pytest.fixture
def progress_callback():
    """Create a mock progress callback for testing."""
    return MagicMock()


@pytest.fixture
def progress_tracker(progress_callback):
    """Create a progress tracker with mock callback."""
    return ProgressTracker(callback=progress_callback)


@pytest.fixture
def predefined_stages():
    """Predefined stages for testing."""
    return ["validation", "parsing", "formatting", "generation", "output"]


@pytest.fixture
def progress_tracker_with_stages(progress_callback, predefined_stages):
    """Create progress tracker with predefined stages."""
    return ProgressTracker(callback=progress_callback, stages=predefined_stages)


from pathlib import Path
