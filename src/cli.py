"""
Command-line interface for the resume automation tool.

This module provides a comprehensive CLI for the ResumeConverter with support
for single file conversion, batch processing, and configuration management.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from .converter import ResumeConverter, convert_resume
from .converter.batch_processor import BatchProcessor
from .converter.progress_tracker import ProgressTracker, ProcessingStage
from .converter.exceptions import ConversionError, ValidationError, ConfigurationError
from .converter.types import ProgressCallback


# Set up CLI-specific logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIProgressReporter:
    """Progress reporter for CLI interface."""
    
    def __init__(self, verbose: bool = False, quiet: bool = False) -> None:
        """
        Initialize CLI progress reporter.
        
        Args:
            verbose: Whether to show verbose output
            quiet: Whether to suppress all output except errors
        """
        self.verbose = verbose
        self.quiet = quiet
        self.last_stage = ""
    
    def __call__(
        self,
        stage: str,
        progress: float,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report progress to CLI."""
        if self.quiet:
            return
        
        # Show stage transitions
        if stage != self.last_stage and not stage.startswith("batch"):
            if self.verbose:
                print(f"\n🔄 {stage.upper()}: {message}")
            self.last_stage = stage
        
        # Show progress for long operations
        if stage in ["processing", "batch_progress"] or progress in [0.0, 100.0]:
            if self.verbose:
                progress_bar = self._create_progress_bar(progress)
                print(f"\r{progress_bar} {progress:5.1f}% - {message}", end="", flush=True)
            elif progress == 100.0 or stage == "complete":
                print(f"✅ {message}")
        
        # Show batch-specific progress
        if stage == "batch_complete":
            print(f"\n✅ {message}")
    
    def _create_progress_bar(self, progress: float, width: int = 30) -> str:
        """Create a text-based progress bar."""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"


def create_parser() -> argparse.ArgumentParser:
    """
    Create the CLI argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Resume Automation Tool - Convert markdown resumes to multiple formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single resume with default settings
  resume-convert resume.md
  
  # Convert with custom configuration
  resume-convert resume.md --config my_config.yaml
  
  # Convert to specific formats only
  resume-convert resume.md --formats html pdf
  
  # Batch convert multiple resumes
  resume-convert *.md --batch --output-dir outputs/
  
  # Convert with custom output directory
  resume-convert resume.md --output-dir /path/to/output
        """
    )
    
    # Input arguments
    parser.add_argument(
        "input_files",
        nargs="+",
        help="Resume file(s) to convert (markdown format)"
    )
    
    # Output configuration
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="Output directory for generated files (default: ./output)"
    )
    
    parser.add_argument(
        "--formats", "-f",
        nargs="+",
        choices=["html", "pdf", "docx"],
        help="Output formats to generate (default: all formats)"
    )
    
    # Configuration
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (YAML format)"
    )
    
    parser.add_argument(
        "--config-override",
        action="append",
        help="Override configuration values (e.g., --config-override ats_rules.max_line_length=85)"
    )
    
    # Processing options
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="Enable batch processing mode for multiple files"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        help="Number of worker threads for batch processing"
    )
    
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip output validation"
    )
    
    # Output control
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format"
    )
    
    # Utility commands
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List available output formats and exit"
    )
    
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit"
    )
    
    parser.add_argument(
        "--validate-config",
        type=str,
        help="Validate configuration file and exit"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit"
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Raises:
        SystemExit: If arguments are invalid
    """
    # Check input files exist
    for input_file in args.input_files:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"❌ Error: Input file does not exist: {input_file}", file=sys.stderr)
            sys.exit(1)
        
        if not input_path.is_file():
            print(f"❌ Error: Input path is not a file: {input_file}", file=sys.stderr)
            sys.exit(1)
        
        if input_path.suffix.lower() not in ['.md', '.markdown']:
            print(f"⚠️  Warning: File does not have .md extension: {input_file}", file=sys.stderr)
    
    # Check configuration file exists
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ Error: Configuration file does not exist: {args.config}", file=sys.stderr)
            sys.exit(1)
    
    # Validate conflicting options
    if args.verbose and args.quiet:
        print("❌ Error: Cannot use --verbose and --quiet together", file=sys.stderr)
        sys.exit(1)
    
    # Batch processing validation
    if len(args.input_files) > 1 and not args.batch:
        print("⚠️  Warning: Multiple input files detected. Consider using --batch flag for better performance")


def parse_config_overrides(overrides: List[str]) -> Dict[str, Any]:
    """
    Parse configuration override strings.
    
    Args:
        overrides: List of override strings in format "key=value"
        
    Returns:
        Dictionary of configuration overrides
    """
    parsed_overrides = {}
    
    for override in overrides:
        try:
            key, value = override.split("=", 1)
            
            # Try to parse value as appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif "." in value and all(part.isdigit() for part in value.split(".")):
                value = float(value)
            
            parsed_overrides[key] = value
            
        except ValueError:
            print(f"⚠️  Warning: Invalid override format: {override}", file=sys.stderr)
    
    return parsed_overrides


def handle_utility_commands(args: argparse.Namespace) -> bool:
    """
    Handle utility commands that don't require conversion.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        True if a utility command was handled, False otherwise
    """
    if args.version:
        print("Resume Automation Tool v0.1.0-alpha.3")
        print("Built with Python 3.12+")
        return True
    
    if args.list_formats:
        converter = ResumeConverter()
        formats = converter.get_supported_formats()
        print("Available output formats:")
        for fmt in formats:
            print(f"  • {fmt}")
        return True
    
    if args.list_themes:
        converter = ResumeConverter()
        themes = converter.get_available_themes()
        print("Available themes:")
        for format_type, theme_list in themes.items():
            print(f"  {format_type.upper()}:")
            for theme in theme_list:
                print(f"    • {theme}")
        return True
    
    if args.validate_config:
        try:
            from .converter.config_manager import ConverterConfigManager
            config_manager = ConverterConfigManager(args.validate_config)
            print(f"✅ Configuration file is valid: {args.validate_config}")
            
            if args.verbose:
                summary = config_manager.get_config_summary()
                print("Configuration summary:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}", file=sys.stderr)
            sys.exit(1)
        
        return True
    
    return False


def convert_single_file(
    input_file: str,
    args: argparse.Namespace,
    progress_reporter: CLIProgressReporter
) -> Dict[str, Any]:
    """
    Convert a single resume file.
    
    Args:
        input_file: Path to input file
        args: Command-line arguments
        progress_reporter: Progress reporter instance
        
    Returns:
        Dictionary with conversion results
    """
    try:
        # Create converter
        converter = ResumeConverter(
            config_path=args.config,
            progress_callback=progress_reporter
        )
        
        # Parse overrides
        overrides = {}
        if args.config_override:
            overrides = parse_config_overrides(args.config_override)
        
        # Perform conversion
        result = converter.convert(
            input_path=input_file,
            output_dir=args.output_dir,
            formats=args.formats,
            overrides=overrides
        )
        
        # Return result summary
        return {
            "file": input_file,
            "success": result.success,
            "output_files": [str(f) for f in result.output_files],
            "processing_time": result.processing_time,
            "warnings": result.warnings,
            "errors": result.errors
        }
        
    except Exception as e:
        return {
            "file": input_file,
            "success": False,
            "output_files": [],
            "processing_time": 0.0,
            "warnings": [],
            "errors": [str(e)]
        }


def convert_batch(
    input_files: List[str],
    args: argparse.Namespace,
    progress_reporter: CLIProgressReporter
) -> Dict[str, Any]:
    """
    Convert multiple files in batch.
    
    Args:
        input_files: List of input file paths
        args: Command-line arguments
        progress_reporter: Progress reporter instance
        
    Returns:
        Dictionary with batch conversion results
    """
    try:
        # Create converter factory
        def converter_factory():
            return ResumeConverter(config_path=args.config)
        
        # Create batch processor
        batch_processor = BatchProcessor(
            converter_factory=converter_factory,
            max_workers=args.workers,
            progress_callback=progress_reporter
        )
        
        # Process batch
        batch_result = batch_processor.process_batch(
            input_paths=input_files,
            output_dir=args.output_dir,
            formats=args.formats
        )
        
        # Compile results
        return {
            "total_files": batch_result.total_files,
            "successful_files": batch_result.successful_files,
            "failed_files": batch_result.failed_files,
            "success_rate": batch_result.success_rate,
            "total_processing_time": batch_result.total_processing_time,
            "results": [
                {
                    "file": str(r.input_path),
                    "success": r.success,
                    "output_files": [str(f) for f in r.output_files],
                    "processing_time": r.processing_time,
                    "warnings": r.warnings,
                    "errors": r.errors
                }
                for r in batch_result.results
            ]
        }
        
    except Exception as e:
        return {
            "total_files": len(input_files),
            "successful_files": 0,
            "failed_files": len(input_files),
            "success_rate": 0.0,
            "total_processing_time": 0.0,
            "error": str(e),
            "results": []
        }


def print_results(results: Dict[str, Any], args: argparse.Namespace) -> None:
    """
    Print conversion results to console.
    
    Args:
        results: Conversion results
        args: Command-line arguments
    """
    if args.json_output:
        print(json.dumps(results, indent=2))
        return
    
    if args.quiet:
        return
    
    # Print results based on type
    if "total_files" in results:
        # Batch results
        print(f"\n📊 Batch Conversion Summary:")
        print(f"  Total files: {results['total_files']}")
        print(f"  Successful: {results['successful_files']}")
        print(f"  Failed: {results['failed_files']}")
        print(f"  Success rate: {results['success_rate']:.1f}%")
        print(f"  Total time: {results['total_processing_time']:.2f}s")
        
        if results['failed_files'] > 0 and args.verbose:
            print(f"\n❌ Failed conversions:")
            for result in results['results']:
                if not result['success']:
                    print(f"  • {result['file']}: {result['errors'][0] if result['errors'] else 'Unknown error'}")
    
    else:
        # Single file results
        if results['success']:
            print(f"\n✅ Conversion successful!")
            print(f"  Input: {results['file']}")
            print(f"  Outputs: {len(results['output_files'])} files")
            if args.verbose:
                for output_file in results['output_files']:
                    print(f"    • {output_file}")
            print(f"  Processing time: {results['processing_time']:.2f}s")
        else:
            print(f"\n❌ Conversion failed!")
            print(f"  Input: {results['file']}")
            for error in results['errors']:
                print(f"  Error: {error}")
        
        # Show warnings if any
        if results['warnings'] and args.verbose:
            print(f"  Warnings:")
            for warning in results['warnings']:
                print(f"    ⚠️  {warning}")


def main() -> None:
    """Main CLI entry point."""
    try:
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Handle utility commands
        if handle_utility_commands(args):
            return
        
        # Validate arguments
        validate_arguments(args)
        
        # Set up progress reporter
        progress_reporter = CLIProgressReporter(
            verbose=args.verbose,
            quiet=args.quiet
        )
        
        # Convert files
        if args.batch or len(args.input_files) > 1:
            results = convert_batch(args.input_files, args, progress_reporter)
        else:
            results = convert_single_file(args.input_files[0], args, progress_reporter)
        
        # Print results
        print_results(results, args)
        
        # Exit with appropriate code
        if results.get('success', True) or results.get('successful_files', 0) > 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Conversion cancelled by user", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()