"""
Main Resume Converter Class.

This module provides the ResumeConverter class that orchestrates the complete
resume conversion pipeline from markdown input to multiple output formats.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

# Import existing components
from src.parser import MarkdownResumeParser
from src.formatter.ats_formatter import ATSFormatter
from src.formatter.config import ATSConfig
from src.resume_generator import ResumeGenerator
from src.generator.config import OutputConfig
from src.validation import ResumeValidator

# Import converter components
from .config_manager import ConverterConfigManager
from .types import (
    ConversionResult, 
    BatchConversionResult, 
    ConversionOptions,
    ProgressCallback
)
from .exceptions import (
    ConversionError,
    ValidationError, 
    ProcessingError,
    FileError
)


logger = logging.getLogger(__name__)


class ResumeConverter:
    """
    Main resume converter class that orchestrates the complete conversion pipeline.
    
    Provides a unified interface for converting markdown resumes to multiple formats
    with comprehensive configuration, error handling, and progress tracking.
    """
    
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        progress_callback: Optional[ProgressCallback] = None
    ) -> None:
        """
        Initialize the resume converter.
        
        Args:
            config_path: Optional path to configuration file
            progress_callback: Optional callback for progress tracking
        """
        self.progress_callback = progress_callback
        self._processing_start_time: Optional[float] = None
        
        # Initialize configuration manager
        self.config_manager = ConverterConfigManager(config_path)
        
        # Initialize components
        self._initialize_components()
        
        logger.info("ResumeConverter initialized successfully")
    
    def _initialize_components(self) -> None:
        """Initialize all pipeline components with configuration."""
        try:
            config = self.config_manager.config
            
            # Initialize parser
            self.parser = MarkdownResumeParser()
            
            # Initialize ATS formatter with configuration
            ats_config = ATSConfig(
                max_line_length=config.ats_rules.max_line_length,
                bullet_style=config.ats_rules.bullet_style,
                section_order=config.ats_rules.section_order,
                optimize_keywords=config.ats_rules.optimize_keywords,
                remove_special_chars=config.ats_rules.remove_special_chars,
                keyword_emphasis=config.ats_rules.keyword_emphasis,
                formatting_rules=config.ats_rules.formatting_rules
            )
            self.formatter = ATSFormatter(ats_config)
            
            # Initialize output generator with configuration
            output_config = OutputConfig(
                output_dir=Path(config.output_formats.output_directory),
                enabled_formats=config.output_formats.enabled_formats,
                html_theme=config.output_formats.html_theme,
                pdf_page_size=config.output_formats.pdf_page_size,
                pdf_margins=config.output_formats.pdf_margins,
                docx_template=config.output_formats.docx_template,
                filename_prefix=config.output_formats.filename_prefix,
                overwrite_existing=config.output_formats.overwrite_existing
            )
            self.generator = ResumeGenerator(output_config)
            
            # Initialize validator
            self.validator = ResumeValidator()
            
            logger.debug("All pipeline components initialized")
            
        except Exception as e:
            raise ConversionError(
                f"Failed to initialize pipeline components: {e}",
                stage="initialization"
            )
    
    def convert(
        self,
        input_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        formats: Optional[List[str]] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> ConversionResult:
        """
        Convert a single resume file to specified formats.
        
        Args:
            input_path: Path to markdown resume file
            output_dir: Optional output directory (overrides config)
            formats: Optional list of formats to generate (overrides config)
            overrides: Optional configuration overrides
            
        Returns:
            ConversionResult: Result of the conversion operation
            
        Raises:
            ConversionError: If conversion fails
            ValidationError: If input validation fails
            FileError: If file operations fail
        """
        start_time = time.time()
        input_path = Path(input_path)
        
        result = ConversionResult(
            success=True,
            input_path=input_path,
            processing_time=0.0
        )
        
        try:
            self._report_progress("validation", 0.0, "Starting conversion")
            
            # Apply any configuration overrides
            if overrides:
                self.config_manager.update_config_overrides(overrides)
            
            # Validate input
            self._validate_input(input_path, result)
            self._report_progress("validation", 20.0, "Input validation complete")
            
            # Parse markdown
            resume_data = self._parse_markdown(input_path, result)
            self._report_progress("parsing", 40.0, "Markdown parsing complete")
            
            # Apply ATS formatting
            formatted_data = self._apply_ats_formatting(resume_data, result)
            self._report_progress("formatting", 60.0, "ATS formatting complete")
            
            # Generate outputs
            output_files = self._generate_outputs(
                formatted_data, result, output_dir, formats
            )
            result.output_files = output_files
            self._report_progress("generation", 80.0, "Output generation complete")
            
            # Validate outputs if enabled
            if self.config_manager.should_validate_output():
                self._validate_outputs(output_files, result)
            
            self._report_progress("complete", 100.0, "Conversion completed successfully")
            
        except Exception as e:
            result.success = False
            if isinstance(e, (ConversionError, ValidationError, FileError)):
                result.add_error(str(e))
            else:
                result.add_error(f"Unexpected error: {e}")
            logger.error(f"Conversion failed: {e}")
        
        finally:
            result.processing_time = time.time() - start_time
            
        return result
    
    def convert_batch(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        formats: Optional[List[str]] = None,
        max_workers: Optional[int] = None
    ) -> BatchConversionResult:
        """
        Convert multiple resume files in batch.
        
        Args:
            input_paths: List of paths to markdown resume files
            output_dir: Optional output directory for all files
            formats: Optional list of formats to generate for all files
            max_workers: Optional number of worker threads
            
        Returns:
            BatchConversionResult: Result of the batch conversion operation
        """
        start_time = time.time()
        
        batch_result = BatchConversionResult(
            total_files=len(input_paths)
        )
        
        try:
            self._report_progress(
                "batch_start", 0.0, 
                f"Starting batch conversion of {len(input_paths)} files"
            )
            
            # Convert each file individually for now
            # TODO: Implement concurrent processing in Phase 3
            for i, input_path in enumerate(input_paths):
                self._report_progress(
                    "batch_progress", 
                    (i / len(input_paths)) * 100,
                    f"Processing file {i+1}/{len(input_paths)}: {Path(input_path).name}"
                )
                
                try:
                    result = self.convert(input_path, output_dir, formats)
                    batch_result.add_result(result)
                    
                except Exception as e:
                    # Create failed result for this file
                    failed_result = ConversionResult(
                        success=False,
                        input_path=Path(input_path)
                    )
                    failed_result.add_error(f"Failed to convert {input_path}: {e}")
                    batch_result.add_result(failed_result)
            
            self._report_progress(
                "batch_complete", 100.0,
                f"Batch conversion complete: {batch_result.successful_files}/{batch_result.total_files} successful"
            )
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {e}")
            
        finally:
            batch_result.total_processing_time = time.time() - start_time
            
        return batch_result
    
    def _validate_input(self, input_path: Path, result: ConversionResult) -> None:
        """Validate input file."""
        if not input_path.exists():
            raise FileError(
                f"Input file does not exist: {input_path}",
                file_path=str(input_path),
                operation="read"
            )
        
        if not input_path.is_file():
            raise FileError(
                f"Input path is not a file: {input_path}",
                file_path=str(input_path),
                operation="read"
            )
        
        if input_path.suffix.lower() not in ['.md', '.markdown']:
            result.add_warning(
                f"Input file has unexpected extension: {input_path.suffix}. "
                "Expected .md or .markdown"
            )
    
    def _parse_markdown(self, input_path: Path, result: ConversionResult):
        """Parse markdown file to resume data."""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            resume_data = self.parser.parse(markdown_content)
            
            if self.config_manager.should_validate_input():
                validation_result = self.validator.validate(resume_data)
                if not validation_result.is_valid:
                    for error in validation_result.errors:
                        result.add_error(f"Validation error: {error}")
                    raise ValidationError("Resume data validation failed")
                
                for warning in validation_result.warnings:
                    result.add_warning(f"Validation warning: {warning}")
            
            return resume_data
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ProcessingError(
                f"Failed to parse markdown: {e}",
                stage="parsing",
                component="MarkdownResumeParser",
                original_error=e
            )
    
    def _apply_ats_formatting(self, resume_data, result: ConversionResult):
        """Apply ATS formatting to resume data."""
        try:
            formatted_data = self.formatter.format(resume_data)
            return formatted_data
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to apply ATS formatting: {e}",
                stage="formatting", 
                component="ATSFormatter",
                original_error=e
            )
    
    def _generate_outputs(
        self, 
        resume_data, 
        result: ConversionResult,
        output_dir: Optional[Union[str, Path]] = None,
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        """Generate output files."""
        try:
            output_results = self.generator.generate_all_formats(
                resume_data=resume_data,
                output_dir=Path(output_dir) if output_dir else None,
                custom_filename=None,
                template_vars=None
            )
            
            return [Path(path) for path in output_results.values()]
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to generate outputs: {e}",
                stage="generation",
                component="ResumeGenerator", 
                original_error=e
            )
    
    def _validate_outputs(self, output_files: List[Path], result: ConversionResult) -> None:
        """Validate generated output files."""
        for output_file in output_files:
            if not output_file.exists():
                result.add_error(f"Expected output file not created: {output_file}")
            elif output_file.stat().st_size == 0:
                result.add_error(f"Output file is empty: {output_file}")
    
    def _report_progress(
        self, 
        stage: str, 
        progress: float, 
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report progress if callback is set."""
        if self.progress_callback:
            try:
                self.progress_callback(stage, progress, message, metadata)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        return ["html", "pdf", "docx"]
    
    def get_available_themes(self) -> Dict[str, List[str]]:
        """Get available themes for each output format."""
        return {
            "html": ["professional", "modern", "minimal", "tech"],
            "docx": ["professional", "modern", "minimal"],
            "pdf": ["professional", "modern", "minimal", "tech"]
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return self.config_manager.get_config_summary()