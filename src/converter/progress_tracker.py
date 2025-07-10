"""
Progress tracking utilities for the resume converter module.

This module provides comprehensive progress tracking, time estimation,
and callback management for conversion operations.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .types import ProgressCallback, ProcessingStage

logger = logging.getLogger(__name__)


@dataclass
class ProgressState:
    """
    Current state of progress tracking.

    Attributes:
        current_stage: Name of current processing stage
        overall_progress: Overall progress percentage (0-100)
        stage_progress: Progress within current stage (0-100)
        estimated_completion: Estimated completion time
        started_at: When processing started
        metadata: Additional progress metadata
    """

    current_stage: str = ""
    overall_progress: float = 0.0
    stage_progress: float = 0.0
    estimated_completion: datetime | None = None
    started_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ProgressTracker:
    """
    Comprehensive progress tracker for conversion operations.

    Provides stage-based progress tracking, time estimation, and
    callback management with detailed reporting capabilities.
    """

    def __init__(
        self,
        callback: ProgressCallback | None = None,
        stages: list[str] | None = None,
        enable_estimation: bool = True,
        enable_timing: bool = True,
        enable_estimates: bool = True,
        history_size: int = 100,
    ) -> None:
        """
        Initialize the progress tracker.

        Args:
            callback: Optional callback for progress updates
            stages: Optional list of stage names to predefine
            enable_estimation: Whether to enable time estimation
            enable_timing: Whether to enable timing measurements
            enable_estimates: Whether to enable completion estimates  
            history_size: Number of operations to keep in history
        """
        self.callback = callback
        self.enable_estimation = enable_estimation
        self.enable_timing = enable_timing
        self.enable_estimates = enable_estimates
        self.history_size = history_size

        # Current progress state
        self.state = ProgressState()

        # Stage definitions
        self._stages_dict: dict[str, ProcessingStage] = {}
        self.stage_order: list[str] = stages or []
        self.current_stage_index: int = 0

        # History for estimation
        self.operation_history: list[dict[str, Any]] = []
        
        # Stage timing history
        self.stage_history: list[dict[str, Any]] = []

        # Stage timing
        self.stage_start_times: dict[str, float] = {}
        self.stage_durations: dict[str, float] = {}
        self.stage_start_time: datetime | None = None  # For individual stage timing

        # Initialize stage weights if stages provided
        if stages:
            self.define_stages(stages)

        logger.debug("ProgressTracker initialized")

    @property
    def current_stage(self) -> str | None:
        """Get the name of the current processing stage."""
        return self.state.current_stage if self.state.current_stage else None

    @property
    def total_stages(self) -> int:
        """Get the total number of defined stages."""
        return len(self.stage_order)

    @property
    def current_progress(self) -> float:
        """Get the current progress percentage."""
        return self.state.stage_progress

    @property
    def stages(self) -> list[str]:
        """Get the list of stage names."""
        return self.stage_order.copy()

    def define_stages(self, stages: list[str]) -> None:
        """
        Define the processing stages for tracking.

        Args:
            stages: List of stage names
        """
        self.stage_order = stages
        self.current_stage_index = 0
        # Reset weights to equal distribution
        weight = 1.0 / len(stages) if stages else 0.0
        self.stage_weights = {stage: weight for stage in stages}
        
        logger.debug(f"Defined {len(stages)} processing stages")

    def start_operation(self, operation_name: str = "conversion") -> None:
        """
        Start tracking a new operation.

        Args:
            operation_name: Name of the operation being tracked
        """
        self.state = ProgressState(
            started_at=datetime.now(), metadata={"operation_name": operation_name}
        )

        self.current_stage_index = 0
        self.stage_start_times.clear()
        self.stage_durations.clear()

        self._report_progress(
            stage="start",
            progress=0.0,
            message=f"Starting {operation_name}",
            metadata={"operation_name": operation_name},
        )

        logger.info(f"Started tracking operation: {operation_name}")

    def start_stage(self, stage_name: str, message: str | None = None) -> None:
        """
        Start a new processing stage.

        Args:
            stage_name: Name of the stage to start
            message: Optional custom message
        """
        # Complete previous stage if any
        if self.state.current_stage:
            self.complete_stage()

        # Find stage index
        if stage_name in self.stage_order:
            self.current_stage_index = self.stage_order.index(stage_name)

        # Update state
        self.state.current_stage = stage_name
        self.state.stage_progress = 0.0

        # Record start time
        self.stage_start_times[stage_name] = time.time()

        # Update stage object
        if stage_name in self._stages_dict:
            self._stages_dict[stage_name].started_at = datetime.now()
            
        # Record start time for individual stage timing
        self.stage_start_time = datetime.now()
        
        # Add stage to history if not already present
        stage_exists = any(record.get("stage") == stage_name or record.get("stage_name") == stage_name for record in self.stage_history)
        if not stage_exists:
            stage_record = {
                "stage": stage_name,
                "stage_name": stage_name,
                "start_time": time.time(),
                "started_at": datetime.now().isoformat(),
                "completed": False,
                "message": message or f"Starting {stage_name}"
            }
            self.stage_history.append(stage_record)

        # Calculate overall progress
        self._update_overall_progress()

        # Report progress
        display_message = message or f"Starting {stage_name}"
        self._report_progress(
            stage=stage_name,
            progress=0.0,
            message=display_message,
            metadata=None,
        )

        logger.debug(f"Started stage: {stage_name}")

    def update_stage_progress(
        self,
        progress: float,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Update progress within the current stage.

        Args:
            progress: Progress within stage (0-100)
            message: Optional progress message
            metadata: Optional additional metadata
        """
        if not self.state.current_stage:
            logger.warning("Attempted to update stage progress without active stage")
            return

        # Clamp progress to valid range
        progress = max(0.0, min(100.0, progress))
        self.state.stage_progress = progress

        # Update overall progress
        self._update_overall_progress()

        # Update estimated completion time
        if self.enable_estimation:
            self._update_time_estimation()

        # Report progress
        display_message = message or f"Processing {self.state.current_stage}..."
        self._report_progress(
            stage=self.state.current_stage,
            progress=self.state.stage_progress,
            message=display_message,
            metadata=metadata,
        )

    def complete_stage(self, message: str | None = None) -> None:
        """
        Complete the current processing stage.

        Args:
            message: Optional completion message
        """
        if not self.state.current_stage:
            return

        stage_name = self.state.current_stage

        # Record completion time
        if stage_name in self.stage_start_times:
            start_time = self.stage_start_times[stage_name]
            end_time = time.time()
            duration = end_time - start_time
            self.stage_durations[stage_name] = duration
            
            # Record in stage history if timing is enabled
            if self.enable_timing:
                stage_record = {
                    "stage": stage_name,
                    "stage_name": stage_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "message": message or f"Completed {stage_name}",
                    "completed": True
                }
                # Update existing record or add new one
                existing_record = None
                for i, record in enumerate(self.stage_history):
                    if record.get("stage") == stage_name or record.get("stage_name") == stage_name:
                        existing_record = i
                        break
                
                if existing_record is not None:
                    self.stage_history[existing_record].update(stage_record)
                else:
                    self.stage_history.append(stage_record)

        # Update stage object
        if stage_name in self._stages_dict:
            self._stages_dict[stage_name].completed_at = datetime.now()

        # Set stage progress to 100%
        self.state.stage_progress = 100.0
        self._update_overall_progress()

        # Report completion
        display_message = message or f"Completed {stage_name}"
        self._report_progress(
            stage=stage_name,
            progress=100.0,
            message=display_message,
            metadata={"stage_progress": 100.0, "stage_completed": True},
        )

        logger.debug(f"Completed stage: {stage_name}")
    
    def _record_stage_completion(self) -> None:
        """
        Record completion of the current stage.
        """
        if self.current_stage and self.stage_start_time:
            duration = (datetime.now() - self.stage_start_time).total_seconds()
            stage_record = {
                "stage": self.current_stage,
                "started_at": self.stage_start_time.isoformat(),
                "completed_at": datetime.now().isoformat(),
                "duration": duration,
                "completed": True
            }
            # Update or add to stage history
            for i, record in enumerate(self.stage_history):
                if record.get("stage") == self.current_stage:
                    self.stage_history[i].update(stage_record)
                    return
            self.stage_history.append(stage_record)

    def complete_operation(self, message: str | None = None) -> None:
        """
        Complete the entire operation.

        Args:
            message: Optional completion message
        """
        # Complete current stage if any
        if self.state.current_stage:
            self.complete_stage()

        # Set overall progress to 100%
        self.state.overall_progress = 100.0

        # Record operation in history
        if self.state.started_at:
            operation_duration = (
                datetime.now() - self.state.started_at
            ).total_seconds()
            self._record_operation_history(operation_duration)

        # Report completion
        display_message = message or "Operation completed successfully"
        self._report_progress(
            stage="complete",
            progress=100.0,
            message=display_message,
            metadata={"operation_completed": True},
        )

        logger.info(
            f"Completed operation: {self.state.metadata.get('operation_name', 'unknown')}"
        )

    def report_error(self, error_message: str, stage: str | None = None) -> None:
        """
        Report an error during processing.

        Args:
            error_message: Description of the error
            stage: Optional stage where error occurred
        """
        error_stage = stage or self.state.current_stage or "unknown"

        self._report_progress(
            stage=error_stage,
            progress=self.state.overall_progress,
            message=f"Error: {error_message}",
            metadata={"error": True, "error_message": error_message},
        )

        logger.error(f"Error reported in stage {error_stage}: {error_message}")

    def _update_overall_progress(self) -> None:
        """Update overall progress based on stages and current stage progress."""
        if not self.stage_order:
            return

        total_progress = 0.0

        # Add progress from completed stages
        for i, stage_name in enumerate(self.stage_order):
            if i < self.current_stage_index:
                # Stage completed
                if stage_name in self._stages_dict:
                    total_progress += self._stages_dict[stage_name].weight * 100
                else:
                    # Use equal weight if not defined
                    weight = 1.0 / len(self.stage_order) if self.stage_order else 0.0
                    total_progress += weight * 100
            elif i == self.current_stage_index:
                # Current stage
                if stage_name in self._stages_dict:
                    stage_weight = self._stages_dict[stage_name].weight
                    total_progress += stage_weight * self.state.stage_progress
                else:
                    # Use equal weight if not defined
                    weight = 1.0 / len(self.stage_order) if self.stage_order else 0.0
                    total_progress += weight * self.state.stage_progress

        self.state.overall_progress = min(100.0, total_progress)

    def _update_time_estimation(self) -> None:
        """Update estimated completion time based on current progress."""
        if not self.state.started_at or self.state.overall_progress <= 0:
            return

        elapsed_time = (datetime.now() - self.state.started_at).total_seconds()

        # Estimate based on current progress
        if self.state.overall_progress > 0:
            estimated_total_time = elapsed_time * (100.0 / self.state.overall_progress)
            remaining_time = estimated_total_time - elapsed_time

            if remaining_time > 0:
                self.state.estimated_completion = datetime.now() + timedelta(
                    seconds=remaining_time
                )

        # Refine estimate using historical data if available
        if self.operation_history:
            avg_duration = sum(op["duration"] for op in self.operation_history) / len(
                self.operation_history
            )
            historical_estimate = self.state.started_at + timedelta(
                seconds=avg_duration
            )

            # Use weighted average of current and historical estimates
            if self.state.estimated_completion:
                current_weight = 0.7
                historical_weight = 0.3

                current_seconds = (
                    self.state.estimated_completion - datetime.now()
                ).total_seconds()
                historical_seconds = (
                    historical_estimate - datetime.now()
                ).total_seconds()

                weighted_seconds = (current_weight * current_seconds) + (
                    historical_weight * historical_seconds
                )

                if weighted_seconds > 0:
                    self.state.estimated_completion = datetime.now() + timedelta(
                        seconds=weighted_seconds
                    )

    def _record_operation_history(self, duration: float) -> None:
        """Record completed operation for future estimation."""
        operation_record = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "stages": len(self.stage_order),
            "stage_durations": dict(self.stage_durations),
        }

        self.operation_history.append(operation_record)

        # Keep only recent history
        if len(self.operation_history) > self.history_size:
            self.operation_history = self.operation_history[-self.history_size :]

    def _report_progress(
        self,
        stage: str,
        progress: float,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Report progress via callback if available."""
        if self.callback:
            try:
                self.callback(stage, progress, message, metadata=metadata)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def get_progress_summary(self) -> dict[str, Any]:
        """
        Get comprehensive progress summary.

        Returns:
            Dictionary with current progress information
        """
        summary = {
            "overall_progress": self.state.overall_progress,
            "current_stage": self.state.current_stage,
            "stage_progress": self.state.stage_progress,
            "started_at": (
                self.state.started_at.isoformat() if self.state.started_at else None
            ),
            "estimated_completion": (
                self.state.estimated_completion.isoformat()
                if self.state.estimated_completion
                else None
            ),
            "elapsed_time": (
                (datetime.now() - self.state.started_at).total_seconds()
                if self.state.started_at
                else 0
            ),
            "stages": [],
        }

        # Add stage information
        for stage_name in self.stage_order:
            stage_info = {
                "name": stage_name,
                "weight": (
                    self._stages_dict[stage_name].weight if stage_name in self._stages_dict else (1.0 / len(self.stage_order) if self.stage_order else 0.0)
                ),
                "status": "pending",
            }

            if stage_name in self.stage_durations:
                stage_info["status"] = "completed"
                stage_info["duration"] = self.stage_durations[stage_name]
            elif stage_name == self.state.current_stage:
                stage_info["status"] = "in_progress"
                stage_info["progress"] = self.state.stage_progress

            summary["stages"].append(stage_info)

        return summary

    def set_callback(self, callback: ProgressCallback | None) -> None:
        """
        Set or update the progress callback.

        Args:
            callback: New progress callback function
        """
        self.callback = callback
        logger.debug("Progress callback updated")
