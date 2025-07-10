"""
Command-line interface for the resume automation tool.

This module provides a comprehensive CLI for the ResumeConverter with support
for single file conversion, batch processing, and configuration management.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

import click

from .converter import ResumeConverter
from .converter.batch_processor import BatchProcessor


def get_version() -> str:
    """
    Extract version from pyproject.toml dynamically.

    Returns:
        Version string from pyproject.toml or fallback version
    """
    try:
        # Try Python 3.11+ built-in tomllib first
        try:
            import tomllib
        except ImportError:
            # Fallback to tomli for older versions
            import tomli as tomllib

        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception as e:
        # Fallback to hardcoded version if anything goes wrong
        logger.warning(f"Could not extract version from pyproject.toml: {e}")
        return "0.1.0-alpha.3"


# Set up CLI-specific logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Report progress to CLI."""
        if self.quiet:
            return

        # Show stage transitions
        if stage != self.last_stage and not stage.startswith("batch"):
            if self.verbose:
                click.echo(f"\n🔄 {stage.upper()}: {message}")
            self.last_stage = stage

        # Show progress for long operations
        if stage in ["processing", "batch_progress"] or progress in [0.0, 100.0]:
            if self.verbose:
                progress_bar = self._create_progress_bar(progress)
                click.echo(f"\r{progress_bar} {progress:5.1f}% - {message}", nl=False)
            elif progress == 100.0 or stage == "complete":
                click.echo(f"✅ {message}")

        # Show batch-specific progress
        if stage == "batch_complete":
            click.echo(f"\n✅ {message}")

    def _create_progress_bar(self, progress: float, width: int = 30) -> str:
        """Create a text-based progress bar."""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"


# Common validation functions for click commands
def validate_input_file(input_file: str) -> Path:
    """
    Validate input file exists and is a markdown file.

    Args:
        input_file: Path to input file

    Returns:
        Path object for the validated file

    Raises:
        click.ClickException: If file is invalid
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise click.ClickException(f"Input file does not exist: {input_file}")

    if not input_path.is_file():
        raise click.ClickException(f"Input path is not a file: {input_file}")

    if input_path.suffix.lower() not in [".md", ".markdown"]:
        click.echo(
            f"⚠️  Warning: File does not have .md extension: {input_file}", err=True
        )

    return input_path


def validate_config_file(config_file: str) -> Path:
    """
    Validate configuration file exists.

    Args:
        config_file: Path to configuration file

    Returns:
        Path object for the validated file

    Raises:
        click.ClickException: If file is invalid
    """
    config_path = Path(config_file)
    if not config_path.exists():
        raise click.ClickException(f"Configuration file does not exist: {config_file}")

    return config_path


def parse_config_overrides(overrides: list[str]) -> dict[str, Any]:
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


# Utility functions that will be used by click commands
def get_converter() -> ResumeConverter:
    """Get a ResumeConverter instance for utility commands."""
    return ResumeConverter()


def validate_config_content(config_file: str) -> None:
    """
    Validate configuration file content.

    Args:
        config_file: Path to configuration file

    Raises:
        click.ClickException: If configuration is invalid
    """
    try:
        from .converter.config_manager import ConverterConfigManager

        config_manager = ConverterConfigManager(config_file)
        click.echo(f"✅ Configuration file is valid: {config_file}")

        summary = config_manager.get_config_summary()
        click.echo("Configuration summary:")
        for key, value in summary.items():
            click.echo(f"  {key}: {value}")

    except Exception as e:
        raise click.ClickException(f"Configuration validation failed: {e}") from e


def convert_single_file(
    input_file: str,
    output_dir: str | None = None,
    formats: list[str] | None = None,
    config_path: str | None = None,
    config_overrides: list[str] | None = None,
    no_validation: bool = False,
    progress_reporter: CLIProgressReporter | None = None,
) -> dict[str, Any]:
    """
    Convert a single resume file.

    Args:
        input_file: Path to input file
        output_dir: Output directory for generated files
        formats: List of output formats to generate
        config_path: Path to configuration file
        config_overrides: List of configuration overrides
        no_validation: Skip output validation
        progress_reporter: Progress reporter instance

    Returns:
        Dictionary with conversion results
    """
    try:
        # Create converter
        converter = ResumeConverter(
            config_path=config_path, progress_callback=progress_reporter
        )

        # Parse overrides
        overrides = {}
        if config_overrides:
            overrides = parse_config_overrides(config_overrides)

        # Perform conversion
        result = converter.convert(
            input_path=input_file,
            output_dir=output_dir,
            formats=formats,
            overrides=overrides,
        )

        # Return result summary
        return {
            "file": input_file,
            "success": result.success,
            "output_files": [str(f) for f in result.output_files],
            "processing_time": result.processing_time,
            "warnings": result.warnings,
            "errors": result.errors,
        }

    except Exception as e:
        return {
            "file": input_file,
            "success": False,
            "output_files": [],
            "processing_time": 0.0,
            "warnings": [],
            "errors": [str(e)],
        }


def convert_batch(
    input_files: list[str],
    output_dir: str | None = None,
    formats: list[str] | None = None,
    config_path: str | None = None,
    config_overrides: list[str] | None = None,
    no_validation: bool = False,
    workers: int | None = None,
    progress_reporter: CLIProgressReporter | None = None,
) -> dict[str, Any]:
    """
    Convert multiple files in batch.

    Args:
        input_files: List of input file paths
        output_dir: Output directory for generated files
        formats: List of output formats to generate
        config_path: Path to configuration file
        config_overrides: List of configuration overrides
        no_validation: Skip output validation
        workers: Number of worker threads for batch processing
        progress_reporter: Progress reporter instance

    Returns:
        Dictionary with batch conversion results
    """
    try:
        # Create converter factory
        def converter_factory():
            return ResumeConverter(config_path=config_path)

        # Create batch processor
        batch_processor = BatchProcessor(
            converter_factory=converter_factory,
            max_workers=workers,
            progress_callback=progress_reporter,
        )

        # Process batch
        batch_result = batch_processor.process_batch(
            input_paths=input_files, output_dir=output_dir, formats=formats
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
                    "errors": r.errors,
                }
                for r in batch_result.results
            ],
        }

    except Exception as e:
        return {
            "total_files": len(input_files),
            "successful_files": 0,
            "failed_files": len(input_files),
            "success_rate": 0.0,
            "total_processing_time": 0.0,
            "error": str(e),
            "results": [],
        }


def print_results(
    results: dict[str, Any], json_output: bool = False, verbose: bool = False
) -> None:
    """
    Print conversion results to console.

    Args:
        results: Conversion results
        json_output: Output results in JSON format
        verbose: Enable verbose output
    """
    if json_output:
        click.echo(json.dumps(results, indent=2))
        return

    # Print results based on type
    if "total_files" in results:
        # Batch results
        click.echo("\n📊 Batch Conversion Summary:")
        click.echo(f"  Total files: {results['total_files']}")
        click.echo(f"  Successful: {results['successful_files']}")
        click.echo(f"  Failed: {results['failed_files']}")
        click.echo(f"  Success rate: {results['success_rate']:.1f}%")
        click.echo(f"  Total time: {results['total_processing_time']:.2f}s")

        if results["failed_files"] > 0 and verbose:
            click.echo("\n❌ Failed conversions:")
            for result in results["results"]:
                if not result["success"]:
                    error_msg = (
                        result["errors"][0] if result["errors"] else "Unknown error"
                    )
                    click.echo(f"  • {result['file']}: {error_msg}")

    else:
        # Single file results
        if results["success"]:
            click.echo("\n✅ Conversion successful!")
            click.echo(f"  Input: {results['file']}")
            click.echo(f"  Outputs: {len(results['output_files'])} files")
            if verbose:
                for output_file in results["output_files"]:
                    click.echo(f"    • {output_file}")
            click.echo(f"  Processing time: {results['processing_time']:.2f}s")
        else:
            click.echo("\n❌ Conversion failed!")
            click.echo(f"  Input: {results['file']}")
            for error in results["errors"]:
                click.echo(f"  Error: {error}")

        # Show warnings if any
        if results["warnings"] and verbose:
            click.echo("  Warnings:")
            for warning in results["warnings"]:
                click.echo(f"    ⚠️  {warning}")


@click.group()
@click.version_option(version=get_version(), prog_name="Resume Automation Tool")
def cli():
    """Resume Automation Tool - Convert markdown resumes to multiple formats.

    This tool provides a comprehensive CLI for converting markdown resumes
    to PDF, HTML, and DOCX formats with ATS optimization.

    Examples:
        # Convert single resume with default PDF format
        resume-convert convert resume.md

        # Convert to specific formats
        resume-convert convert resume.md --format html --format pdf

        # Batch convert multiple resumes
        resume-convert batch *.md --output-dir outputs/

        # List available formats
        resume-convert list-formats
    """
    pass


@cli.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    type=click.Choice(["pdf", "html", "docx"], case_sensitive=False),
    default=["pdf"],
    show_default=True,
    help="Output format(s) to generate. PDF is prioritized as default.",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated files (default: ./output)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration file (YAML format)",
)
@click.option(
    "--config-override",
    multiple=True,
    help="Override config values (e.g., --config-override ats_rules.max_length=85)",
)
@click.option("--no-validation", is_flag=True, help="Skip output validation")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
@click.option("--json-output", is_flag=True, help="Output results in JSON format")
def convert(
    input_file: Path,
    formats: list[str],
    output_dir: Path | None,
    config: Path | None,
    config_override: list[str],
    no_validation: bool,
    verbose: bool,
    quiet: bool,
    json_output: bool,
):
    """Convert a single resume file to specified format(s).

    This command converts a single markdown resume file to one or more output formats.
    By default, PDF format is generated as it is the most commonly requested format
    for ATS systems.

    Examples:
        # Convert to default PDF format
        resume-convert convert resume.md

        # Convert to multiple formats
        resume-convert convert resume.md --format pdf --format html

        # Convert with custom configuration
        resume-convert convert resume.md --config my_config.yaml

        # Convert with output directory
        resume-convert convert resume.md --output-dir /path/to/output
    """
    # Validate mutually exclusive options
    if verbose and quiet:
        raise click.ClickException("Cannot use --verbose and --quiet together")

    # Set up progress reporter
    progress_reporter = CLIProgressReporter(verbose=verbose, quiet=quiet)

    try:
        # Convert the file
        result = convert_single_file(
            input_file=str(input_file),
            output_dir=str(output_dir) if output_dir else None,
            formats=list(formats),
            config_path=str(config) if config else None,
            config_overrides=list(config_override) if config_override else None,
            no_validation=no_validation,
            progress_reporter=progress_reporter,
        )

        # Print results
        if not quiet:
            print_results(result, json_output=json_output, verbose=verbose)

        # Exit with appropriate code
        if result.get("success", False):
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        if json_output:
            error_result = {
                "success": False,
                "file": str(input_file),
                "errors": [str(e)],
                "output_files": [],
                "processing_time": 0.0,
            }
            print(json.dumps(error_result, indent=2))
        else:
            click.echo(f"❌ Conversion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument(
    "input_files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    type=click.Choice(["pdf", "html", "docx"], case_sensitive=False),
    default=["pdf"],
    show_default=True,
    help="Output format(s) to generate. PDF is prioritized as default.",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated files (default: ./output)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration file (YAML format)",
)
@click.option(
    "--config-override",
    multiple=True,
    help="Override config values (e.g., --config-override ats_rules.max_length=85)",
)
@click.option(
    "--workers",
    "-w",
    type=int,
    default=None,
    help="Number of worker threads for batch processing (default: auto-detect)",
)
@click.option("--no-validation", is_flag=True, help="Skip output validation")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
@click.option("--json-output", is_flag=True, help="Output results in JSON format")
def batch(
    input_files: tuple[Path, ...],
    formats: list[str],
    output_dir: Path | None,
    config: Path | None,
    config_override: list[str],
    workers: int | None,
    no_validation: bool,
    verbose: bool,
    quiet: bool,
    json_output: bool,
):
    """Convert multiple resume files in batch.

    This command processes multiple markdown resume files simultaneously using
    parallel processing for improved performance. It's ideal for converting
    multiple resumes at once with consistent settings.

    Examples:
        # Batch convert all markdown files in current directory
        resume-convert batch *.md

        # Batch convert with specific output directory
        resume-convert batch *.md --output-dir outputs/

        # Batch convert with custom worker count
        resume-convert batch *.md --workers 4

        # Batch convert multiple specific files
        resume-convert batch resume1.md resume2.md resume3.md
    """
    # Validate mutually exclusive options
    if verbose and quiet:
        raise click.ClickException("Cannot use --verbose and --quiet together")

    if len(input_files) == 0:
        raise click.ClickException("No input files specified")

    # Convert tuple to list and validate files
    file_list = []
    for file_path in input_files:
        if file_path.suffix.lower() not in [".md", ".markdown"]:
            click.echo(
                f"⚠️  Warning: File does not have .md extension: {file_path}", err=True
            )
        file_list.append(str(file_path))

    # Set up progress reporter
    progress_reporter = CLIProgressReporter(verbose=verbose, quiet=quiet)

    try:
        # Convert files in batch
        result = convert_batch(
            input_files=file_list,
            output_dir=str(output_dir) if output_dir else None,
            formats=list(formats),
            config_path=str(config) if config else None,
            config_overrides=list(config_override) if config_override else None,
            no_validation=no_validation,
            workers=workers,
            progress_reporter=progress_reporter,
        )

        # Print results
        if not quiet:
            print_results(result, json_output=json_output, verbose=verbose)

        # Exit with appropriate code - successful if any files were processed
        if result.get("successful_files", 0) > 0:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        if json_output:
            error_result = {
                "success": False,
                "total_files": len(file_list),
                "successful_files": 0,
                "failed_files": len(file_list),
                "errors": [str(e)],
                "results": [],
            }
            print(json.dumps(error_result, indent=2))
        else:
            click.echo(f"❌ Batch conversion failed: {e}", err=True)
        sys.exit(1)


@cli.command(name="list-formats")
def list_formats():
    """List all available output formats.

    This command displays all supported output formats that can be used
    with the convert and batch commands.
    """
    try:
        converter = get_converter()
        formats = converter.get_supported_formats()

        click.echo("Available output formats:")
        for fmt in formats:
            click.echo(f"  • {fmt}")

    except Exception as e:
        click.echo(f"❌ Error listing formats: {e}", err=True)
        sys.exit(1)


@cli.command(name="list-themes")
def list_themes():
    """List all available themes for output formatting.

    This command displays all available themes that can be used
    to customize the appearance of generated resumes.
    """
    try:
        converter = get_converter()
        themes = converter.get_available_themes()

        click.echo("Available themes:")
        if isinstance(themes, dict):
            for format_type, theme_list in themes.items():
                click.echo(f"  {format_type.upper()}:")
                for theme in theme_list:
                    click.echo(f"    • {theme}")
        else:
            for theme in themes:
                click.echo(f"  • {theme}")

    except Exception as e:
        click.echo(f"❌ Error listing themes: {e}", err=True)
        sys.exit(1)


@cli.command(name="validate-config")
@click.argument(
    "config_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed configuration summary"
)
def validate_config(config_file: Path, verbose: bool):
    """Validate a configuration file.

    This command validates the syntax and content of a YAML configuration file
    to ensure it can be used with the convert and batch commands.

    Examples:
        # Validate configuration file
        resume-convert validate-config config.yaml

        # Validate with detailed output
        resume-convert validate-config config.yaml --verbose
    """
    try:
        validate_config_content(str(config_file))

        if verbose:
            # Show additional details if verbose
            from .converter.config_manager import ConverterConfigManager

            config_manager = ConverterConfigManager(str(config_file))
            summary = config_manager.get_config_summary()

            click.echo("\nDetailed configuration summary:")
            for key, value in summary.items():
                click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\n⏹️  Conversion cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
