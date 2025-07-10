"""
Batch processing utilities for the resume converter module.

This module provides efficient batch processing capabilities with concurrent
execution, resource management, and comprehensive reporting.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from pathlib import Path
from typing import List, Union, Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from .types import ConversionResult, BatchConversionResult, ProgressCallback
from .exceptions import ConversionError, ProcessingError
from .progress_tracker import ProgressTracker, ProcessingStage


logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """
    Represents a single job in a batch operation.
    
    Attributes:
        input_path: Path to input file
        job_id: Unique identifier for the job
        output_dir: Optional output directory override
        formats: Optional formats override
        overrides: Optional configuration overrides
        priority: Job priority (higher numbers = higher priority)
    """
    input_path: Path
    job_id: str
    output_dir: Optional[Path] = None
    formats: Optional[List[str]] = None
    overrides: Optional[Dict[str, Any]] = None
    priority: int = 0


@dataclass
class BatchStats:
    """
    Statistics for batch processing operations.
    
    Attributes:
        total_jobs: Total number of jobs in batch
        completed_jobs: Number of completed jobs
        successful_jobs: Number of successful jobs
        failed_jobs: Number of failed jobs
        skipped_jobs: Number of skipped jobs
        start_time: Batch start time
        end_time: Batch end time
        total_processing_time: Total processing time
        average_job_time: Average time per job
        throughput: Jobs per second
    """
    total_jobs: int = 0
    completed_jobs: int = 0
    successful_jobs: int = 0
    failed_jobs: int = 0
    skipped_jobs: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_processing_time: float = 0.0
    average_job_time: float = 0.0
    throughput: float = 0.0


class BatchProcessor:
    """
    Efficient batch processor for resume conversion operations.
    
    Provides concurrent processing, resource management, progress tracking,
    and comprehensive error handling for batch operations.
    """
    
    def __init__(
        self,
        converter_factory: Callable,
        max_workers: Optional[int] = None,
        chunk_size: int = 10,
        progress_callback: Optional[ProgressCallback] = None
    ) -> None:
        """
        Initialize the batch processor.
        
        Args:
            converter_factory: Factory function to create converter instances
            max_workers: Maximum number of worker threads
            chunk_size: Size of processing chunks
            progress_callback: Optional progress callback
        """
        self.converter_factory = converter_factory
        self.max_workers = max_workers or min(32, (len(os.sched_getaffinity(0)) or 1) + 4)
        self.chunk_size = chunk_size
        self.progress_callback = progress_callback
        
        # Processing state
        self.is_processing = False
        self.should_stop = False
        self.stats = BatchStats()
        
        # Progress tracking
        self.progress_tracker = ProgressTracker(progress_callback)
        self._setup_batch_stages()
        
        logger.debug(f"BatchProcessor initialized with {self.max_workers} workers")
    
    def _setup_batch_stages(self) -> None:
        """Setup processing stages for batch operations."""
        stages = [
            ProcessingStage("preparation", "Preparing batch jobs", 0.1),
            ProcessingStage("processing", "Processing resumes", 0.8),
            ProcessingStage("finalization", "Finalizing results", 0.1)
        ]
        self.progress_tracker.define_stages(stages)
    
    def process_batch(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        formats: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
        fail_fast: bool = False,
        continue_on_error: bool = True
    ) -> BatchConversionResult:
        """
        Process a batch of resume files concurrently.
        
        Args:
            input_paths: List of input file paths
            output_dir: Optional output directory for all files
            formats: Optional list of formats for all files
            max_workers: Optional worker count override
            fail_fast: Whether to stop on first error
            continue_on_error: Whether to continue processing on errors
            
        Returns:
            BatchConversionResult: Results of batch processing
            
        Raises:
            ProcessingError: If batch processing fails critically
        """
        start_time = time.time()
        
        try:
            self.is_processing = True
            self.should_stop = False
            
            # Initialize stats
            self.stats = BatchStats(
                total_jobs=len(input_paths),
                start_time=datetime.now()
            )
            
            # Start progress tracking
            self.progress_tracker.start_operation("batch_conversion")
            
            # Prepare jobs
            jobs = self._prepare_jobs(input_paths, output_dir, formats)
            
            # Process jobs
            results = self._process_jobs_concurrent(
                jobs, 
                max_workers or self.max_workers,
                fail_fast,
                continue_on_error
            )
            
            # Finalize results
            batch_result = self._finalize_batch_results(results, start_time)
            
            self.progress_tracker.complete_operation("Batch processing completed")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            self.progress_tracker.report_error(str(e))
            raise ProcessingError(
                f"Batch processing failed: {e}",
                stage="batch_processing",
                component="BatchProcessor",
                original_error=e
            )
        
        finally:
            self.is_processing = False
            self.stats.end_time = datetime.now()
            self.stats.total_processing_time = time.time() - start_time
            
            if self.stats.completed_jobs > 0:
                self.stats.average_job_time = self.stats.total_processing_time / self.stats.completed_jobs
                self.stats.throughput = self.stats.completed_jobs / self.stats.total_processing_time
    
    def _prepare_jobs(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]],
        formats: Optional[List[str]]
    ) -> List[BatchJob]:
        """Prepare batch jobs from input parameters."""
        self.progress_tracker.start_stage("preparation", "Preparing batch jobs")
        
        jobs = []
        output_path = Path(output_dir) if output_dir else None
        
        for i, input_path in enumerate(input_paths):
            input_file = Path(input_path)
            job_id = f"job_{i:04d}_{input_file.stem}"
            
            job = BatchJob(
                input_path=input_file,
                job_id=job_id,
                output_dir=output_path,
                formats=formats
            )
            jobs.append(job)
            
            # Update progress
            progress = (i + 1) / len(input_paths) * 100
            self.progress_tracker.update_stage_progress(
                progress,
                f"Prepared job {i+1}/{len(input_paths)}: {input_file.name}"
            )
        
        self.progress_tracker.complete_stage("Job preparation completed")
        return jobs
    
    def _process_jobs_concurrent(
        self,
        jobs: List[BatchJob],
        max_workers: int,
        fail_fast: bool,
        continue_on_error: bool
    ) -> List[ConversionResult]:
        """Process jobs using concurrent execution."""
        self.progress_tracker.start_stage("processing", "Processing resumes concurrently")
        
        results = []
        completed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_job = {
                executor.submit(self._process_single_job, job): job
                for job in jobs
            }
            
            # Process completed jobs
            for future in as_completed(future_to_job):
                if self.should_stop:
                    logger.info("Batch processing stopped by user request")
                    break
                
                job = future_to_job[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        self.stats.successful_jobs += 1
                    else:
                        self.stats.failed_jobs += 1
                        
                        if fail_fast:
                            logger.error(f"Stopping batch due to failed job: {job.job_id}")
                            self.should_stop = True
                            break
                    
                except Exception as e:
                    # Create failed result for this job
                    failed_result = ConversionResult(
                        success=False,
                        input_path=job.input_path
                    )
                    failed_result.add_error(f"Job failed: {e}")
                    results.append(failed_result)
                    
                    self.stats.failed_jobs += 1
                    
                    if not continue_on_error:
                        logger.error(f"Stopping batch due to job error: {e}")
                        self.should_stop = True
                        break
                
                # Update progress
                completed_count += 1
                self.stats.completed_jobs = completed_count
                progress = (completed_count / len(jobs)) * 100
                
                self.progress_tracker.update_stage_progress(
                    progress,
                    f"Completed {completed_count}/{len(jobs)} jobs",
                    metadata={
                        "completed": completed_count,
                        "total": len(jobs),
                        "successful": self.stats.successful_jobs,
                        "failed": self.stats.failed_jobs
                    }
                )
            
            # Cancel remaining futures if stopped
            if self.should_stop:
                for future in future_to_job:
                    future.cancel()
        
        self.progress_tracker.complete_stage("Concurrent processing completed")
        return results
    
    def _process_single_job(self, job: BatchJob) -> ConversionResult:
        """
        Process a single job.
        
        Args:
            job: Batch job to process
            
        Returns:
            ConversionResult: Result of processing
        """
        try:
            # Create converter instance for this job
            converter = self.converter_factory()
            
            # Process the job
            result = converter.convert(
                input_path=job.input_path,
                output_dir=job.output_dir,
                formats=job.formats,
                overrides=job.overrides
            )
            
            # Add job metadata
            result.metadata["job_id"] = job.job_id
            result.metadata["batch_processing"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            
            # Create failed result
            failed_result = ConversionResult(
                success=False,
                input_path=job.input_path
            )
            failed_result.add_error(f"Job processing failed: {e}")
            failed_result.metadata["job_id"] = job.job_id
            failed_result.metadata["batch_processing"] = True
            
            return failed_result
    
    def _finalize_batch_results(
        self,
        results: List[ConversionResult],
        start_time: float
    ) -> BatchConversionResult:
        """Finalize and compile batch results."""
        self.progress_tracker.start_stage("finalization", "Finalizing batch results")
        
        batch_result = BatchConversionResult(
            total_files=self.stats.total_jobs,
            successful_files=self.stats.successful_jobs,
            failed_files=self.stats.failed_jobs,
            results=results,
            total_processing_time=time.time() - start_time
        )
        
        # Add summary metadata
        batch_result.summary = {
            "stats": self.get_batch_statistics(),
            "performance": {
                "total_time": batch_result.total_processing_time,
                "average_time_per_file": (
                    batch_result.total_processing_time / len(results) if results else 0
                ),
                "files_per_second": (
                    len(results) / batch_result.total_processing_time 
                    if batch_result.total_processing_time > 0 else 0
                ),
                "worker_efficiency": (
                    (len(results) / batch_result.total_processing_time) / self.max_workers
                    if batch_result.total_processing_time > 0 else 0
                )
            },
            "quality": {
                "success_rate": batch_result.success_rate,
                "error_rate": (batch_result.failed_files / batch_result.total_files * 100)
                            if batch_result.total_files > 0 else 0
            }
        }
        
        self.progress_tracker.complete_stage("Batch results finalized")
        return batch_result
    
    def stop_processing(self) -> None:
        """Signal to stop batch processing."""
        self.should_stop = True
        logger.info("Batch processing stop requested")
    
    def get_batch_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive batch processing statistics.
        
        Returns:
            Dictionary with batch statistics
        """
        return {
            "total_jobs": self.stats.total_jobs,
            "completed_jobs": self.stats.completed_jobs,
            "successful_jobs": self.stats.successful_jobs,
            "failed_jobs": self.stats.failed_jobs,
            "skipped_jobs": self.stats.skipped_jobs,
            "success_rate": (
                (self.stats.successful_jobs / self.stats.total_jobs * 100)
                if self.stats.total_jobs > 0 else 0
            ),
            "completion_rate": (
                (self.stats.completed_jobs / self.stats.total_jobs * 100)
                if self.stats.total_jobs > 0 else 0
            ),
            "processing_time": self.stats.total_processing_time,
            "average_job_time": self.stats.average_job_time,
            "throughput": self.stats.throughput,
            "start_time": self.stats.start_time.isoformat() if self.stats.start_time else None,
            "end_time": self.stats.end_time.isoformat() if self.stats.end_time else None
        }
    
    def is_processing_active(self) -> bool:
        """Check if batch processing is currently active."""
        return self.is_processing
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary."""
        return self.progress_tracker.get_progress_summary()