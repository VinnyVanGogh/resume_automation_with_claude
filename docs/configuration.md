# Configuration System Documentation

## Overview

The resume automation system uses a comprehensive YAML-based configuration system that allows you to customize every aspect of resume generation, from ATS optimization rules to output formats and styling preferences.

## Architecture

The configuration system is built using **Pydantic v2** models for type safety and validation, with the following key components:

- **Config Models** (`src/config/config_model.py`) - Type-safe Pydantic models defining configuration structure
- **Config Loader** (`src/config/config_loader.py`) - YAML loading, merging, and caching functionality  
- **Config Validator** (`src/config/config_validator.py`) - Business rule validation with detailed error reporting
- **Default Configuration** (`src/config/default_config.yaml`) - Production-ready default settings

## Configuration Sections

### 1. ATS Rules (`ats_rules`)

Controls Applicant Tracking System (ATS) optimization features:

```yaml
ats_rules:
  max_line_length: 80                    # Maximum line length (1-200)
  bullet_style: "•"                      # Bullet style: "•", "-", "*"
  section_order:                         # Preferred section order
    - "contact"
    - "summary" 
    - "experience"
    - "education"
    - "skills"
    - "projects"
    - "certifications"
  optimize_keywords: true                # Enable keyword optimization
  remove_special_chars: true             # Remove ATS-unfriendly characters
  keyword_emphasis:                      # Keyword emphasis weights
    technical_skills: 1.5
    soft_skills: 1.2
    industry_terms: 1.3
    certifications: 1.4
  formatting_rules:                      # ATS formatting rules
    use_standard_fonts: true
    avoid_tables: true
    use_simple_bullets: true
    standard_date_format: true
```

**Validation Rules:**
- `max_line_length`: Must be between 1-200 characters
- `bullet_style`: Must be one of: "•", "-", "*"
- Section order should start with "contact" for ATS compatibility
- Keyword emphasis weights should be between 0.5-3.0

### 2. Output Formats (`output_formats`)

Configure multiple output format generation:

```yaml
output_formats:
  enabled_formats: ["html", "pdf", "docx"]   # Formats to generate
  
  # HTML Configuration
  html_theme: "professional"                 # Theme: professional, modern, minimal, tech
  html_include_styles: true                  # Include CSS inline
  html_meta_description: "Professional resume"
  
  # PDF Configuration
  pdf_page_size: "Letter"                   # Page size: Letter, A4, Legal
  pdf_margins:                              # Margins in inches
    top: 0.75
    bottom: 0.75
    left: 0.75
    right: 0.75
  pdf_optimize_size: true                   # Optimize file size
  
  # DOCX Configuration
  docx_template: "professional"             # Template theme
  docx_margins:                             # Margins in inches
    top: 0.75
    bottom: 0.75
    left: 0.75
    right: 0.75
  docx_line_spacing: 1.15                   # Line spacing multiplier
  
  # General Settings
  output_directory: "output"                # Output directory
  filename_prefix: "resume"                 # Filename prefix
  overwrite_existing: true                  # Overwrite existing files
```

**Validation Rules:**
- `enabled_formats`: Must contain at least one of: "html", "pdf", "docx"
- `pdf_page_size`: Must be one of: "Letter", "A4", "Legal"
- Margins should be between 0.25-2.0 inches for optimal results
- DOCX line spacing should be between 0.8-2.5

### 3. Styling (`styling`)

Control fonts, themes, colors, and layout:

```yaml
styling:
  # Font Configuration
  font_family: "Arial"                      # Primary font family
  font_size: 11                            # Base font size (6-24 points)
  font_weight: "normal"                     # Font weight: normal, bold, light
  
  # Theme Configuration
  theme: "professional"                     # Overall theme
  color_scheme:                             # Color scheme (hex colors)
    primary: "#000000"
    secondary: "#333333"
    accent: "#0066cc"
    background: "#ffffff"
  
  # Spacing Configuration
  section_spacing: 12                       # Section spacing (points)
  line_height: 1.15                        # Line height multiplier
  paragraph_spacing: 6                      # Paragraph spacing (points)
  
  # Layout Configuration
  layout_style: "single_column"             # Layout: single_column, two_column
  header_style: "centered"                  # Header: centered, left_aligned, right_aligned
```

**Validation Rules:**
- `font_size`: Must be between 6-24 points
- `font_weight`: Must be one of: "normal", "bold", "light"
- `theme`: Must be one of: "professional", "modern", "minimal", "tech"
- Color scheme values must be valid hex colors (#RRGGBB)
- `section_spacing`: Recommended range 0-50 points
- `line_height`: Recommended range 0.8-3.0

**ATS-Friendly Fonts:**
- Arial
- Helvetica
- Times New Roman
- Calibri
- Georgia
- Verdana
- Trebuchet MS

### 4. Processing (`processing`)

Configure batch processing and performance:

```yaml
processing:
  # Processing Settings
  batch_size: 1                            # Resumes to process in parallel (1-1000)
  max_workers: 1                           # Maximum worker threads (1-32)
  timeout_seconds: 300                     # Processing timeout
  
  # Validation Settings
  validate_input: true                     # Validate input markdown
  validate_output: true                    # Validate generated output
  strict_validation: false                 # Use strict validation mode
  
  # Performance Settings
  cache_templates: true                    # Cache compiled templates
  optimize_images: true                    # Optimize images in output
```

**Validation Rules:**
- `batch_size`: Must be at least 1 (warning if >100)
- `max_workers`: Must be at least 1 (warning if >16)
- `timeout_seconds`: Warning if <30 or >1800 seconds

### 5. Logging (`logging`)

Configure logging behavior:

```yaml
logging:
  level: "INFO"                            # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: null                          # Log file path (null for console only)
  max_file_size: 10485760                  # Max file size in bytes (10MB)
  backup_count: 3                          # Number of backup files
```

**Validation Rules:**
- `level`: Must be one of: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- `max_file_size`: Warning if <1KB or >1GB
- Log file path must be valid if specified

## Configuration File Structure

### Default Configuration

The system includes a comprehensive default configuration (`src/config/default_config.yaml`) that works out-of-the-box:

```yaml
version: "1.0"
created_by: "resume-automation"

ats_rules:
  max_line_length: 80
  bullet_style: "•"
  # ... (see above for complete structure)

output_formats:
  enabled_formats: ["html", "pdf", "docx"]
  # ... (see above for complete structure)

# ... (complete configuration)
```

### Custom Configuration

Create your own configuration file and load it:

```python
from src.config import ConfigLoader

# Load custom configuration
loader = ConfigLoader()
config = loader.load_config("path/to/your/config.yaml")

# Use with resume generator
from src.resume_generator import ResumeGenerator
generator = ResumeGenerator(config=config)
```

### Configuration Merging

The system supports configuration merging, where custom configurations are merged with defaults:

1. **Default Configuration** - Provides base settings
2. **Custom Configuration** - Overrides specific settings
3. **Merged Configuration** - Final configuration used by the system

Example custom config (only override what you need):

```yaml
# custom_config.yaml
ats_rules:
  max_line_length: 85
  bullet_style: "-"

styling:
  theme: "modern"
  font_size: 12
  
# All other settings inherit from defaults
```

## Validation

The configuration system includes comprehensive validation:

### Automatic Validation

- **Type Safety**: Pydantic models ensure correct data types
- **Field Validation**: Built-in validators for specific fields
- **Range Validation**: Numeric fields have appropriate ranges
- **Format Validation**: Special formats (hex colors, file paths) are validated

### Business Rule Validation

Use the `ConfigValidator` for additional business logic validation:

```python
from src.config import ConfigValidator

validator = ConfigValidator()
result = validator.validate_full_config(config)

if not result.is_valid:
    print("Configuration errors:")
    for error in result.errors:
        print(f"  ERROR: {error}")

if result.warnings:
    print("Configuration warnings:")
    for warning in result.warnings:
        print(f"  WARNING: {warning}")
```

### Validation Results

The validator provides detailed feedback:

- **Errors**: Critical issues that must be fixed
- **Warnings**: Recommendations for optimal results
- **Cross-section Validation**: Checks consistency between configuration sections

## Usage Examples

### Basic Usage

```python
from src.config import load_default_config
from src.resume_generator import ResumeGenerator

# Load default configuration
config = load_default_config()

# Generate resume with default settings
generator = ResumeGenerator(config=config)
generator.generate_from_markdown("resume.md")
```

### Custom Configuration

```python
from src.config import ConfigLoader

# Load custom configuration
loader = ConfigLoader()
config = loader.load_config("my_config.yaml")

# Generate resume with custom settings
generator = ResumeGenerator(config=config)
generator.generate_from_markdown("resume.md")
```

### Configuration Validation

```python
from src.config import ConfigLoader, ConfigValidator

# Load and validate configuration
loader = ConfigLoader()
config = loader.load_config("config.yaml")

validator = ConfigValidator()
result = validator.validate_full_config(config)

if result.is_valid:
    print("Configuration is valid!")
    # Proceed with resume generation
else:
    print("Configuration has errors:")
    for error in result.errors:
        print(f"  {error}")
```

### Creating Configuration Programmatically

```python
from src.config import Config, ATSRulesConfig, StylingConfig

# Create configuration programmatically
config = Config(
    ats_rules=ATSRulesConfig(
        max_line_length=85,
        bullet_style="-"
    ),
    styling=StylingConfig(
        theme="modern",
        font_size=12,
        font_family="Calibri"
    )
)

# Use with resume generator
generator = ResumeGenerator(config=config)
```

## Configuration Caching

The configuration system includes intelligent caching:

- **Default Config Caching**: Default configuration is cached after first load
- **File-based Caching**: Configurations are cached by file path
- **Automatic Invalidation**: Cache is invalidated when files change

## Best Practices

### 1. Start with Defaults

Always start with the default configuration and override only what you need:

```yaml
# Good: Minimal custom config
styling:
  theme: "modern"
  font_size: 12

# Avoid: Complete config copy-paste
```

### 2. Validate Your Configuration

Always validate custom configurations:

```python
# Validate before using
result = validator.validate_full_config(config)
if not result.is_valid:
    raise ValueError(f"Invalid configuration: {result.errors}")
```

### 3. Use ATS-Friendly Settings

For maximum ATS compatibility:

```yaml
ats_rules:
  max_line_length: 80
  bullet_style: "•"
  section_order: ["contact", "summary", "experience", "education", "skills"]

styling:
  font_family: "Arial"  # ATS-friendly font
  theme: "professional"  # ATS-optimized theme
```

### 4. Test Different Output Formats

Configure multiple formats for different use cases:

```yaml
output_formats:
  enabled_formats: ["html", "pdf", "docx"]
  html_theme: "modern"      # For online portfolios
  pdf_optimize_size: true   # For email attachments
  docx_template: "professional"  # For ATS systems
```

### 5. Environment-Specific Configurations

Use different configurations for different environments:

```
configs/
├── default.yaml          # Base configuration
├── development.yaml      # Development overrides
├── production.yaml       # Production overrides
└── ats_optimized.yaml    # ATS-specific settings
```

## Troubleshooting

### Common Issues

#### 1. Validation Errors

```
ValidationError: Bullet style must be one of: ['•', '-', '*']
```
**Solution**: Use only supported bullet styles.

#### 2. File Path Issues

```
Invalid output directory path: [Errno 2] No such file or directory
```
**Solution**: Ensure output directory exists or can be created.

#### 3. Theme Inconsistency

```
WARNING: Theme settings are inconsistent across sections
```
**Solution**: Use the same theme across all configuration sections.

#### 4. ATS Compatibility Warnings

```
WARNING: Font 'Comic Sans MS' may not be ATS-friendly
```
**Solution**: Use ATS-friendly fonts like Arial, Helvetica, or Calibri.

### Debug Configuration Issues

Enable debug logging to troubleshoot configuration problems:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Configuration loading will now show detailed debug information
config = loader.load_config("config.yaml")
```

### Validate Configuration File

Use the validator to check configuration files:

```python
from src.config import ConfigValidator

validator = ConfigValidator()
result = validator.validate_config_file("my_config.yaml")

print(result)  # Shows detailed validation results
```

## API Reference

### Classes

- **`Config`**: Main configuration model
- **`ConfigLoader`**: YAML loading and merging
- **`ConfigValidator`**: Business rule validation
- **`ValidationResult`**: Validation result container

### Functions

- **`load_default_config()`**: Load default configuration
- **`load_config_from_path(path)`**: Load configuration from file

### Configuration Models

- **`ATSRulesConfig`**: ATS optimization settings
- **`OutputFormatsConfig`**: Output format preferences
- **`StylingConfig`**: Font and styling settings
- **`ProcessingConfig`**: Processing and performance settings
- **`LoggingConfig`**: Logging configuration

## Migration Guide

### From Previous Versions

If migrating from a previous configuration system:

1. **Review New Structure**: Compare your old config with the new schema
2. **Update Field Names**: Some fields may have been renamed
3. **Add New Sections**: New configuration sections may be available
4. **Validate**: Always validate after migration

### Schema Changes

The configuration schema follows semantic versioning. Check the `version` field in your configuration and the changelog for breaking changes.

## Contributing

When contributing to the configuration system:

1. **Add Tests**: Include comprehensive tests for new configuration options
2. **Update Documentation**: Update this documentation for any changes
3. **Validate**: Ensure all configurations validate correctly
4. **Maintain Compatibility**: Avoid breaking changes when possible

## Support

For configuration-related issues:

1. Check this documentation first
2. Validate your configuration using the validator
3. Enable debug logging for detailed error information
4. Report issues with configuration examples and error messages