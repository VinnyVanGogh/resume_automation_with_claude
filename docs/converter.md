# Main Resume Converter Documentation

## Overview

The Main Resume Converter is the central orchestration layer for the resume automation system. It provides a unified interface for converting markdown resumes to multiple formats (HTML, PDF, DOCX) with comprehensive configuration, error handling, progress tracking, and batch processing capabilities.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [API Reference](#api-reference)
- [CLI Usage](#cli-usage)
- [Configuration](#configuration)
- [Batch Processing](#batch-processing)
- [Error Handling](#error-handling)
- [Quality Validation](#quality-validation)
- [File Management](#file-management)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

```python
from src.converter import ResumeConverter

# Create converter with default configuration
converter = ResumeConverter()

# Convert a single resume
result = converter.convert("resume.md")

# Check result
if result.success:
    print(f"✅ Converted successfully! Generated {len(result.output_files)} files")
    for file in result.output_files:
        print(f"  • {file}")
else:
    print(f"❌ Conversion failed: {result.errors}")
```

### Command Line Usage

```bash
# Convert single resume with default settings
resume-convert resume.md

# Convert with custom configuration
resume-convert resume.md --config my_config.yaml

# Convert to specific formats only
resume-convert resume.md --formats html pdf

# Batch convert multiple resumes
resume-convert *.md --batch --output-dir outputs/
```

## Core Components

### ResumeConverter

The main converter class that orchestrates the complete conversion pipeline:

```
Markdown Input → Parser → ATS Formatter → Generator → Multiple Outputs
```

**Key Features:**
- Unified interface for all conversion operations
- Configuration integration with YAML files
- Progress tracking with callbacks
- Comprehensive error handling and recovery
- Batch processing with concurrent execution
- Quality validation of outputs

### Pipeline Stages

1. **Input Validation**: Validates markdown files and configuration
2. **Parsing**: Converts markdown to structured resume data
3. **ATS Formatting**: Applies ATS optimization rules
4. **Generation**: Creates output files in multiple formats
5. **Quality Validation**: Validates generated outputs

## API Reference

### ResumeConverter Class

#### Constructor

```python
ResumeConverter(
    config_path: Optional[Union[str, Path]] = None,
    progress_callback: Optional[ProgressCallback] = None
)
```

**Parameters:**
- `config_path`: Path to YAML configuration file (optional)
- `progress_callback`: Callback function for progress updates (optional)

#### Methods

##### convert()

```python
convert(
    input_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    formats: Optional[List[str]] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> ConversionResult
```

Convert a single resume file.

**Parameters:**
- `input_path`: Path to markdown resume file
- `output_dir`: Output directory (overrides config)
- `formats`: List of formats to generate (overrides config)
- `overrides`: Configuration overrides

**Returns:** `ConversionResult` with conversion details

##### convert_batch()

```python
convert_batch(
    input_paths: List[Union[str, Path]],
    output_dir: Optional[Union[str, Path]] = None,
    formats: Optional[List[str]] = None,
    max_workers: Optional[int] = None
) -> BatchConversionResult
```

Convert multiple resume files in batch.

**Parameters:**
- `input_paths`: List of input file paths
- `output_dir`: Output directory for all files
- `formats`: List of formats for all files
- `max_workers`: Number of worker threads

**Returns:** `BatchConversionResult` with batch processing details

#### Utility Methods

```python
get_supported_formats() -> List[str]
get_available_themes() -> Dict[str, List[str]]
get_config_summary() -> Dict[str, Any]
```

### Data Classes

#### ConversionResult

```python
@dataclass
class ConversionResult:
    success: bool
    input_path: Path
    output_files: List[Path]
    processing_time: float
    warnings: List[str]
    errors: List[str]
    metadata: Dict[str, Any]
```

#### BatchConversionResult

```python
@dataclass
class BatchConversionResult:
    total_files: int
    successful_files: int
    failed_files: int
    results: List[ConversionResult]
    total_processing_time: float
    summary: Dict[str, Any]
```

## CLI Usage

### Basic Commands

```bash
# Convert single file
resume-convert resume.md

# Specify output directory
resume-convert resume.md --output-dir /path/to/output

# Select specific formats
resume-convert resume.md --formats html pdf

# Use custom configuration
resume-convert resume.md --config custom_config.yaml
```

### Batch Processing

```bash
# Enable batch mode
resume-convert *.md --batch

# Batch with custom settings
resume-convert *.md --batch --workers 4 --output-dir outputs/

# Batch with format selection
resume-convert *.md --batch --formats pdf docx
```

### Configuration Overrides

```bash
# Override single values
resume-convert resume.md --config-override ats_rules.max_line_length=90

# Multiple overrides
resume-convert resume.md \
  --config-override ats_rules.max_line_length=90 \
  --config-override styling.theme=modern
```

### Utility Commands

```bash
# List available formats
resume-convert --list-formats

# List available themes
resume-convert --list-themes

# Validate configuration
resume-convert --validate-config my_config.yaml

# Show version
resume-convert --version
```

### Output Control

```bash
# Verbose output
resume-convert resume.md --verbose

# Quiet mode (errors only)
resume-convert resume.md --quiet

# JSON output
resume-convert resume.md --json-output
```

## Configuration

The converter integrates seamlessly with the existing YAML configuration system. See [Configuration Documentation](configuration.md) for detailed configuration options.

### Custom Configuration Example

```python
from src.converter import ResumeConverter

# Load with custom config
converter = ResumeConverter(config_path="my_config.yaml")

# Convert with runtime overrides
result = converter.convert(
    "resume.md",
    overrides={
        "ats_rules.max_line_length": 85,
        "styling.theme": "modern"
    }
)
```

## Batch Processing

### Concurrent Processing

The converter supports efficient batch processing with concurrent execution:

```python
from src.converter import ResumeConverter

converter = ResumeConverter()

# Process multiple files
input_files = ["resume1.md", "resume2.md", "resume3.md"]
batch_result = converter.convert_batch(
    input_paths=input_files,
    output_dir="batch_output/",
    max_workers=4
)

print(f"Processed {batch_result.total_files} files")
print(f"Success rate: {batch_result.success_rate:.1f}%")
```

### Batch Processing with Custom Factory

For advanced batch processing scenarios:

```python
from src.converter.batch_processor import BatchProcessor

def converter_factory():
    return ResumeConverter(config_path="batch_config.yaml")

processor = BatchProcessor(
    converter_factory=converter_factory,
    max_workers=6
)

result = processor.process_batch(
    input_paths=input_files,
    fail_fast=False,
    continue_on_error=True
)
```

### Progress Tracking

```python
def progress_callback(stage, progress, message, metadata=None):
    print(f"[{stage}] {progress:.1f}% - {message}")

converter = ResumeConverter(progress_callback=progress_callback)
result = converter.convert("resume.md")
```

## Error Handling

### Comprehensive Error Classification

The converter provides detailed error classification and user-friendly messages:

```python
from src.converter import ResumeConverter
from src.converter.exceptions import ConversionError, ValidationError

try:
    converter = ResumeConverter()
    result = converter.convert("invalid_resume.md")
    
    if not result.success:
        print("Conversion failed:")
        for error in result.errors:
            print(f"  ❌ {error}")
        
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")

except ValidationError as e:
    print(f"Input validation failed: {e}")
except ConversionError as e:
    print(f"Conversion error: {e}")
```

### Error Recovery

The converter includes automatic error recovery mechanisms:

- **Configuration Errors**: Falls back to default configuration
- **Processing Errors**: Attempts alternative processing methods
- **File Errors**: Provides detailed file operation error messages

## Quality Validation

### Automatic Quality Validation

```python
from src.converter.quality_validator import QualityValidator

# Enable quality validation
converter = ResumeConverter()
result = converter.convert("resume.md")

# Manual quality validation
validator = QualityValidator()
validation_report = validator.validate_output_files(result.output_files)

print(f"Validation: {'PASSED' if validation_report.is_valid else 'FAILED'}")
print(f"Average quality score: {validation_report.summary['average_scores']['overall']}")
```

### Quality Metrics

The quality validator provides comprehensive metrics:

- **Content Score**: Based on file size and structure
- **ATS Score**: ATS compliance rating
- **Formatting Score**: File format and structure quality
- **Overall Score**: Weighted average of all scores

## File Management

### Advanced File Organization

```python
from src.converter.file_manager import FileManager, FileOrganizationStrategy, NamingStrategy

# Custom organization strategy
organization = FileOrganizationStrategy(
    use_subdirectories=True,
    group_by_date=True,
    use_source_name=True
)

# Custom naming strategy
naming = NamingStrategy(
    prefix="resume",
    include_timestamp=True,
    replace_spaces=True
)

# Create file manager
file_manager = FileManager(
    base_output_dir="organized_output/",
    organization_strategy=organization,
    naming_strategy=naming
)

# Convert and organize
converter = ResumeConverter()
result = converter.convert("resume.md")

organized_files, report = file_manager.organize_output_files(
    output_files=result.output_files,
    source_file=Path("resume.md")
)
```

## Examples

### Example 1: Simple Conversion

```python
from src.converter import convert_resume

# Convenience function for simple usage
result = convert_resume(
    input_path="resume.md",
    output_dir="output/",
    config_path="config.yaml"
)

if result.success:
    print("✅ Conversion successful!")
else:
    print("❌ Conversion failed!")
```

### Example 2: Advanced Conversion with Callbacks

```python
from src.converter import ResumeConverter

class ProgressTracker:
    def __init__(self):
        self.stages = []
    
    def __call__(self, stage, progress, message, metadata=None):
        self.stages.append((stage, progress, message))
        print(f"[{stage.upper()}] {progress:5.1f}% - {message}")

tracker = ProgressTracker()
converter = ResumeConverter(progress_callback=tracker)

result = converter.convert(
    input_path="resume.md",
    output_dir="custom_output/",
    formats=["html", "pdf"],
    overrides={
        "styling.theme": "modern",
        "ats_rules.max_line_length": 100
    }
)

print(f"Completed {len(tracker.stages)} processing stages")
```

### Example 3: Batch Processing with Error Handling

```python
from src.converter import ResumeConverter
from pathlib import Path

def process_resume_directory(input_dir, output_dir):
    """Process all markdown files in a directory."""
    
    # Find all markdown files
    input_files = list(Path(input_dir).glob("*.md"))
    
    if not input_files:
        print("No markdown files found!")
        return
    
    print(f"Found {len(input_files)} resume files")
    
    # Progress tracking
    def progress_callback(stage, progress, message, metadata=None):
        if stage == "batch_progress":
            completed = metadata.get("completed", 0) if metadata else 0
            total = metadata.get("total", 0) if metadata else 0
            print(f"Progress: {completed}/{total} files completed")
    
    # Create converter and process batch
    converter = ResumeConverter(progress_callback=progress_callback)
    
    batch_result = converter.convert_batch(
        input_paths=input_files,
        output_dir=output_dir,
        max_workers=4
    )
    
    # Report results
    print(f"\n📊 Batch Processing Results:")
    print(f"  Total files: {batch_result.total_files}")
    print(f"  Successful: {batch_result.successful_files}")
    print(f"  Failed: {batch_result.failed_files}")
    print(f"  Success rate: {batch_result.success_rate:.1f}%")
    print(f"  Total time: {batch_result.total_processing_time:.2f}s")
    
    # Show failed files
    if batch_result.failed_files > 0:
        print(f"\n❌ Failed conversions:")
        for result in batch_result.results:
            if not result.success:
                print(f"  • {result.input_path.name}: {result.errors[0] if result.errors else 'Unknown error'}")

# Usage
process_resume_directory("resumes/", "converted_resumes/")
```

### Example 4: Custom Configuration and Validation

```python
from src.converter import ResumeConverter
from src.converter.config_manager import ConverterConfigManager
from src.converter.utilities import ConfigUtils

# Validate configuration first
config_validation = ConfigUtils.validate_config_file("my_config.yaml")

if not config_validation["is_valid"]:
    print("❌ Configuration validation failed:")
    for error in config_validation["errors"]:
        print(f"  • {error}")
    exit(1)

print("✅ Configuration is valid")

# Create converter with validated config
converter = ResumeConverter(config_path="my_config.yaml")

# Show configuration summary
config_summary = converter.get_config_summary()
print(f"Configuration summary:")
for key, value in config_summary.items():
    print(f"  {key}: {value}")

# Convert with quality validation
result = converter.convert("resume.md")

if result.success:
    print(f"✅ Conversion successful!")
    print(f"  Processing time: {result.processing_time:.2f}s")
    print(f"  Output files: {len(result.output_files)}")
    
    # Additional quality check
    from src.converter.quality_validator import QualityValidator
    validator = QualityValidator()
    quality_report = validator.validate_output_files(result.output_files)
    
    if quality_report.is_valid:
        print(f"✅ Quality validation passed")
        avg_score = quality_report.summary['average_scores']['overall']
        print(f"  Average quality score: {avg_score:.1f}/100")
    else:
        print(f"⚠️  Quality validation issues found")
        for issue in quality_report.file_metrics[0].issues if quality_report.file_metrics else []:
            print(f"    • {issue}")
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```python
# Error: ModuleNotFoundError: No module named 'src.converter'
# Solution: Ensure you're running from the project root and the package is installed

# Add project root to Python path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.converter import ResumeConverter
```

#### 2. Configuration Errors

```python
# Error: Configuration validation failed
# Solution: Use configuration validation utilities

from src.converter.utilities import ConfigUtils

# Validate configuration file
validation = ConfigUtils.validate_config_file("my_config.yaml")
if not validation["is_valid"]:
    print("Configuration errors:")
    for error in validation["errors"]:
        print(f"  • {error}")
```

#### 3. File Permission Errors

```python
# Error: Permission denied when writing files
# Solution: Check output directory permissions

from src.converter.file_manager import FileManager

file_manager = FileManager("output/")
issues = file_manager.validate_output_directory()

if issues:
    print("Output directory issues:")
    for issue in issues:
        print(f"  • {issue}")
```

#### 4. Memory Issues with Large Batches

```python
# Solution: Reduce batch size and worker count

converter = ResumeConverter()
batch_result = converter.convert_batch(
    input_paths=large_file_list,
    max_workers=2,  # Reduce from default
    # Process in smaller chunks
)
```

### Debugging

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all converter operations will show debug information
converter = ResumeConverter()
result = converter.convert("resume.md")
```

#### Use System Diagnostics

```python
from src.converter.utilities import get_system_diagnostics, validate_setup

# Check system setup
is_valid, issues = validate_setup()
if not is_valid:
    print("Setup issues:")
    for issue in issues:
        print(f"  • {issue}")

# Get comprehensive diagnostics
diagnostics = get_system_diagnostics()
print("System information:")
print(f"  Python version: {diagnostics['system_info']['python']['version']}")
print(f"  Dependencies: {diagnostics['dependencies']}")
```

#### Performance Profiling

```python
import time
from src.converter import ResumeConverter

def profile_conversion(input_file):
    """Profile conversion performance."""
    
    times = []
    def progress_callback(stage, progress, message, metadata=None):
        times.append((time.time(), stage, progress, message))
    
    converter = ResumeConverter(progress_callback=progress_callback)
    
    start_time = time.time()
    result = converter.convert(input_file)
    total_time = time.time() - start_time
    
    print(f"Total conversion time: {total_time:.2f}s")
    print("Stage breakdown:")
    
    for i, (timestamp, stage, progress, message) in enumerate(times):
        if i > 0:
            stage_time = timestamp - times[i-1][0]
            print(f"  {stage}: {stage_time:.2f}s - {message}")

profile_conversion("resume.md")
```

## API Migration Guide

### From Basic ResumeGenerator

If you're migrating from the basic `ResumeGenerator` class:

```python
# Old way
from src.resume_generator import ResumeGenerator
from src.parser import MarkdownResumeParser
from src.formatter.ats_formatter import ATSFormatter

parser = MarkdownResumeParser()
formatter = ATSFormatter()
generator = ResumeGenerator()

# Manual pipeline
resume_data = parser.parse(markdown_content)
formatted_data = formatter.format(resume_data)
output_files = generator.generate_all_formats(formatted_data)

# New way
from src.converter import ResumeConverter

converter = ResumeConverter()
result = converter.convert("resume.md")  # Complete pipeline in one call
```

### Configuration Migration

```python
# Old way - manual configuration
from src.generator.config import OutputConfig
from src.formatter.config import ATSConfig

output_config = OutputConfig(...)
ats_config = ATSConfig(...)

# New way - YAML configuration
converter = ResumeConverter(config_path="config.yaml")
```

## Best Practices

1. **Always validate configuration** before processing large batches
2. **Use progress callbacks** for long-running operations
3. **Handle errors gracefully** and provide user feedback
4. **Validate outputs** when quality is critical
5. **Use batch processing** for multiple files
6. **Monitor memory usage** with large files or batches
7. **Keep configuration files** in version control
8. **Test with sample data** before production use

## Performance Guidelines

- **Single File**: Expect <5 seconds for typical resumes
- **Batch Processing**: Use 1-4 workers for optimal performance
- **Memory Usage**: ~50MB per worker thread
- **Disk Space**: ~2-5MB per resume for all formats
- **Network**: No network required for basic functionality

## Support

For additional help:

1. Check the [main documentation](../README.md)
2. Review [configuration documentation](configuration.md)
3. Examine the [integration tests](../src/converter/tests/test_integration.py) for examples
4. Run system diagnostics with `get_system_diagnostics()`

---

**Main Resume Converter** - The unified interface for professional resume conversion with comprehensive features and enterprise-grade reliability.