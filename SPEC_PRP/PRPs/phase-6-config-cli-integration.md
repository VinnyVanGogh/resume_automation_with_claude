# Phase 6: Configuration & CLI Integration PRP

## Specification: Complete Resume Automation System with CLI Interface

Design and implement the final integration layer that ties all components together through a comprehensive configuration system, main converter orchestration class, professional CLI interface, and end-to-end integration testing to deliver a complete, production-ready resume automation tool.

## Current State Assessment

```yaml
current_state:
  files:
    - src/parser.py (Phase 1 complete - markdown parsing)
    - src/formatter/ (Phase 2 complete - ATS formatting)
    - src/generator/ (Phase 4 complete - HTML/PDF/DOCX generation)
    - src/templates/ (Phase 5 complete - professional templates)
    - src/models.py (comprehensive data models)
    - src/validation.py (data validation)
    - pyproject.toml (project configuration with CLI entry point)
    - No configuration system implemented
    - No main converter orchestration class
    - No CLI interface implementation
    - No integration testing framework
  behavior:
    - Individual components work in isolation
    - Parser converts markdown to ResumeData models
    - Formatter applies ATS optimization rules
    - Generators create HTML/PDF/DOCX with templates
    - Templates render professional, styled outputs
    - Each component has >90% test coverage
    - No unified interface for end-users
    - No configuration customization options
  issues:
    - No way for users to interact with the system
    - No configuration system for ATS rules or output preferences
    - No orchestration layer to coordinate components
    - No batch processing capabilities
    - No error handling at system level
    - No progress tracking for long operations
    - No integration testing of complete pipeline
    - CLI entry point defined but not implemented
```

## Desired State

```yaml
desired_state:
  files:
    - src/config/
      ├── __init__.py
      ├── config_loader.py (YAML configuration loading)
      ├── config_validator.py (configuration validation)
      ├── default_config.yaml (default ATS rules and settings)
      └── tests/
          ├── __init__.py
          ├── test_config_loader.py
          ├── test_config_validator.py
          └── fixtures/
              ├── valid_config.yaml
              └── invalid_config.yaml
    - src/converter.py (main ResumeConverter orchestration class)
    - src/cli.py (comprehensive CLI interface)
    - src/tests/
      ├── test_converter.py (converter unit tests)
      ├── test_cli.py (CLI interface tests)
      ├── test_integration.py (enhanced end-to-end tests)
      └── fixtures/
          ├── sample_resume.md
          ├── sample_batch/
          └── expected_outputs/
    - examples/
      ├── config_examples.yaml
      ├── sample_resume.md
      └── batch_processing/
    - docs/
      ├── configuration.md
      ├── cli_usage.md
      └── integration_guide.md
  behavior:
    - Users can run `resume-convert input.md --output-dir outputs/`
    - YAML configuration system validates and applies settings
    - ResumeConverter orchestrates all components seamlessly
    - CLI supports single file and batch processing
    - Progress tracking and detailed error reporting
    - Customizable ATS rules and output preferences
    - Theme selection and styling options
    - Professional help documentation and examples
    - Complete end-to-end integration testing
    - Performance benchmarks for large batches
  benefits:
    - Production-ready resume automation tool
    - User-friendly CLI interface for all skill levels
    - Flexible configuration system for customization
    - Batch processing for multiple resumes
    - Professional error handling and logging
    - Comprehensive documentation and examples
    - >90% test coverage including integration tests
    - Scalable architecture for future enhancements
```

## Hierarchical Objectives

### High-Level Goal

Complete Phase 6 configuration and CLI integration to deliver a production-ready resume automation tool with comprehensive configuration system, main converter orchestration, professional CLI interface, and end-to-end integration testing.

### Mid-Level Milestones

1. **YAML Configuration System** - Implement flexible configuration loading and validation for ATS rules, output preferences, and styling options
2. **Main Converter Orchestration** - Create ResumeConverter class that coordinates all components with error handling and progress tracking
3. **Professional CLI Interface** - Build comprehensive command-line interface with single file and batch processing capabilities
4. **End-to-End Integration Testing** - Establish complete pipeline validation with sample resumes and performance benchmarks

### Low-Level Tasks

#### Task 1: Create Configuration Module Structure

```yaml
task_name: create_config_module
action: CREATE
file: src/config/__init__.py
changes: |
  - Create config package initialization
  - Export main configuration classes:
    - ConfigLoader for YAML loading
    - ConfigValidator for validation
    - Config for configuration data model
  - Set up module imports and __all__ list
  - Add module-level docstring
validation:
  - command: 'uv run python -c "from src.config import ConfigLoader, ConfigValidator, Config; print(\"Config module imported successfully\")"'
  - expect: "Config module imported successfully"
```

#### Task 2: Create Configuration Data Model

```yaml
task_name: create_config_model
action: CREATE
file: src/config/config_model.py
changes: |
  - Create Config pydantic model with sections:
    - ats_rules: ATS optimization settings
    - output_formats: PDF/HTML/DOCX preferences
    - styling: Theme and font preferences
    - processing: Batch processing settings
    - logging: Logging configuration
  - Add validation for all configuration fields
  - Include default values for all settings
  - Add configuration schema documentation
validation:
  - command: 'uv run python -c "from src.config.config_model import Config; c = Config(); print(f\"Config model created with {len(c.model_fields)} fields\")"'
  - expect: "Config model created with 5 fields"
```

#### Task 3: Create Configuration Loader

```yaml
task_name: create_config_loader
action: CREATE
file: src/config/config_loader.py
changes: |
  - Create ConfigLoader class with methods:
    - load_config(path): Load YAML configuration
    - load_default_config(): Load default settings
    - merge_configs(): Merge user and default configs
    - validate_config(): Validate configuration
  - Handle file not found gracefully
  - Support both absolute and relative paths
  - Add comprehensive error handling
  - Include logging for configuration loading
validation:
  - command: 'uv run python -c "from src.config.config_loader import ConfigLoader; cl = ConfigLoader(); print(\"ConfigLoader created successfully\")"'
  - expect: "ConfigLoader created successfully"
```

#### Task 4: Create Default Configuration

```yaml
task_name: create_default_config
action: CREATE
file: src/config/default_config.yaml
changes: |
  - Define comprehensive default configuration:
    - ats_rules: Standard ATS optimization settings
    - output_formats: Default PDF/HTML/DOCX settings
    - styling: Professional theme as default
    - processing: Single-threaded processing
    - logging: INFO level logging
  - Add extensive comments explaining each setting
  - Ensure all settings are ATS-compliant
  - Include theme and styling options
validation:
  - command: 'uv run python -c "import yaml; config = yaml.safe_load(open(\"src/config/default_config.yaml\")); print(f\"Default config loaded with {len(config)} sections\")"'
  - expect: "Default config loaded with 5 sections"
```

#### Task 5: Create Configuration Validator

```yaml
task_name: create_config_validator
action: CREATE
file: src/config/config_validator.py
changes: |
  - Create ConfigValidator class with methods:
    - validate_ats_rules(): Validate ATS settings
    - validate_output_formats(): Validate format settings
    - validate_styling(): Validate theme/font settings
    - validate_processing(): Validate batch settings
    - validate_full_config(): Complete validation
  - Return detailed validation results
  - Provide helpful error messages
  - Support partial validation
validation:
  - command: 'uv run python -c "from src.config.config_validator import ConfigValidator; cv = ConfigValidator(); print(\"ConfigValidator created successfully\")"'
  - expect: "ConfigValidator created successfully"
```

#### Task 6: Create Main Converter Class

```yaml
task_name: create_converter_class
action: CREATE
file: src/converter.py
changes: |
  - Create ResumeConverter class with methods:
    - __init__(config_path): Initialize with configuration
    - convert_single(input_path, output_dir): Single file conversion
    - convert_batch(input_dir, output_dir): Batch processing
    - _parse_resume(): Parse markdown to ResumeData
    - _format_resume(): Apply ATS formatting
    - _generate_outputs(): Generate all output formats
    - _validate_inputs(): Input validation
    - _handle_errors(): Error handling and logging
  - Add progress tracking with callbacks
  - Include comprehensive error handling
  - Support all output formats (HTML, PDF, DOCX)
  - Add logging throughout conversion process
validation:
  - command: 'uv run python -c "from src.converter import ResumeConverter; rc = ResumeConverter(); print(\"ResumeConverter created successfully\")"'
  - expect: "ResumeConverter created successfully"
```

#### Task 7: Create CLI Interface

```yaml
task_name: create_cli_interface
action: CREATE
file: src/cli.py
changes: |
  - Create main CLI function with argparse
  - Add commands:
    - convert: Single file conversion
    - batch: Batch processing
    - validate: Validate configuration
    - version: Show version information
  - Add options:
    - --config: Custom configuration file
    - --output-dir: Output directory
    - --format: Output format selection
    - --theme: Theme selection
    - --verbose: Verbose logging
    - --debug: Debug mode
  - Add comprehensive help documentation
  - Include usage examples
  - Handle CLI errors gracefully
validation:
  - command: 'uv run python -c "from src.cli import main; print(\"CLI module created successfully\")"'
  - expect: "CLI module created successfully"
```

#### Task 8: Create CLI Command Handlers

```yaml
task_name: create_cli_handlers
action: MODIFY
file: src/cli.py
changes: |
  - Add command handler functions:
    - handle_convert(): Single file conversion
    - handle_batch(): Batch processing
    - handle_validate(): Configuration validation
    - handle_version(): Version information
  - Add error handling for each command
  - Include progress reporting
  - Add file validation
  - Support output format selection
  - Add theme customization
validation:
  - command: 'uv run resume-convert --help'
  - expect: "usage: resume-convert"
```

#### Task 9: Create Configuration Tests

```yaml
task_name: create_config_tests
action: CREATE
file: src/config/tests/test_config_loader.py
changes: |
  - Test ConfigLoader functionality:
    - test_load_default_config(): Test default configuration loading
    - test_load_custom_config(): Test custom YAML loading
    - test_merge_configs(): Test configuration merging
    - test_invalid_config(): Test error handling
    - test_missing_file(): Test file not found handling
  - Create test fixtures with valid/invalid configurations
  - Test all error scenarios
  - Ensure >95% test coverage
validation:
  - command: "uv run pytest src/config/tests/test_config_loader.py -v"
  - expect: "All tests pass"
```

#### Task 10: Create Converter Tests

```yaml
task_name: create_converter_tests
action: CREATE
file: src/tests/test_converter.py
changes: |
  - Test ResumeConverter functionality:
    - test_single_conversion(): Test single file conversion
    - test_batch_conversion(): Test batch processing
    - test_error_handling(): Test error scenarios
    - test_progress_tracking(): Test progress callbacks
    - test_output_formats(): Test all format generation
  - Create test fixtures with sample resumes
  - Test configuration integration
  - Mock external dependencies
  - Ensure comprehensive error testing
validation:
  - command: "uv run pytest src/tests/test_converter.py -v"
  - expect: "All tests pass"
```

#### Task 11: Create CLI Tests

```yaml
task_name: create_cli_tests
action: CREATE
file: src/tests/test_cli.py
changes: |
  - Test CLI functionality:
    - test_convert_command(): Test single file conversion
    - test_batch_command(): Test batch processing
    - test_validate_command(): Test configuration validation
    - test_version_command(): Test version display
    - test_help_output(): Test help documentation
    - test_error_handling(): Test CLI error scenarios
  - Use subprocess to test actual CLI calls
  - Test all command-line options
  - Verify output file generation
  - Test error message formatting
validation:
  - command: "uv run pytest src/tests/test_cli.py -v"
  - expect: "All tests pass"
```

#### Task 12: Create Integration Test Framework

```yaml
task_name: create_integration_tests
action: MODIFY
file: src/tests/test_integration.py
changes: |
  - Enhance existing integration tests:
    - test_complete_pipeline(): Test full conversion pipeline
    - test_cli_integration(): Test CLI with real files
    - test_batch_processing(): Test batch conversion
    - test_configuration_override(): Test config customization
    - test_theme_selection(): Test theme switching
    - test_error_scenarios(): Test error handling
    - test_performance_benchmarks(): Test processing speed
  - Create comprehensive test fixtures
  - Add sample resume files
  - Test all output formats
  - Validate ATS compliance
validation:
  - command: "uv run pytest src/tests/test_integration.py -v"
  - expect: "All tests pass"
```

#### Task 13: Create Sample Files and Documentation

```yaml
task_name: create_examples_docs
action: CREATE
file: examples/sample_resume.md
changes: |
  - Create comprehensive sample resume:
    - All sections (contact, summary, experience, education, skills)
    - Multiple experience entries with bullets
    - Education with honors and coursework
    - Categorized skills
    - Professional summary
    - Complete contact information
  - Add sample configuration files
  - Create batch processing examples
  - Add documentation files:
    - configuration.md: Configuration guide
    - cli_usage.md: CLI usage examples
    - integration_guide.md: Integration guide
validation:
  - command: "ls examples/ | grep -c '.md'"
  - expect: ">=3"
```

#### Task 14: Update Package Configuration

```yaml
task_name: update_package_config
action: MODIFY
file: pyproject.toml
changes: |
  - Update project version to 0.2.0
  - Add new dependencies if needed
  - Ensure CLI entry point is correct
  - Update project description
  - Add new classifiers for CLI tool
  - Update development dependencies
validation:
  - command: 'uv run python -c "import toml; config = toml.load(\"pyproject.toml\"); print(f\"Version: {config[\"project\"][\"version\"]}\")"'
  - expect: "Version: 0.2.0"
```

#### Task 15: Create End-to-End Validation

```yaml
task_name: create_e2e_validation
action: CREATE
file: src/tests/test_e2e.py
changes: |
  - Create end-to-end validation suite:
    - test_cli_single_conversion(): Test CLI single file conversion
    - test_cli_batch_conversion(): Test CLI batch processing
    - test_configuration_loading(): Test custom configuration
    - test_all_output_formats(): Test HTML, PDF, DOCX generation
    - test_theme_customization(): Test theme switching
    - test_error_recovery(): Test error handling and recovery
  - Use temporary directories for testing
  - Validate actual file outputs
  - Test performance with large resumes
  - Ensure professional quality outputs
validation:
  - command: "uv run pytest src/tests/test_e2e.py -v"
  - expect: "All tests pass"
```

#### Task 16: Verify Complete System

```yaml
task_name: verify_system_completion
action: RUN
changes: |
  - Run complete test suite
  - Verify CLI functionality
  - Test sample resume conversion
  - Validate all output formats
  - Check test coverage >90%
  - Verify documentation completeness
  - Test error handling scenarios
  - Validate ATS compliance
validation:
  - command: "uv run pytest --cov=src --cov-fail-under=90"
  - expect: "Coverage >= 90%"
```

## Implementation Strategy

1. **Configuration Foundation** - Start with configuration system (Tasks 1-5)
   - Build YAML loading and validation infrastructure
   - Create default configuration and validation
   - Establish foundation for all other components

2. **Core Converter** - Implement main orchestration (Task 6)
   - Create ResumeConverter class that uses existing components
   - Integrate parser, formatter, and generators
   - Add error handling and progress tracking

3. **CLI Interface** - Build user interface (Tasks 7-8)
   - Create CLI with comprehensive options
   - Add command handlers for all operations
   - Implement user-friendly error messages

4. **Comprehensive Testing** - Validate complete system (Tasks 9-12, 15)
   - Test each component thoroughly
   - Create integration tests for full pipeline
   - Ensure end-to-end functionality

5. **Documentation and Examples** - Finalize user experience (Tasks 13-14)
   - Create sample files and documentation
   - Update package configuration
   - Provide comprehensive usage examples

6. **Final Validation** - Verify system completion (Task 16)
   - Run complete test suite
   - Validate all requirements
   - Ensure production readiness

## Dependencies

- **Phase 1-5 Complete**: Requires all previous phases (parser, formatter, generators, templates)
- **External Dependencies**:
  - PyYAML 6.0.1 (YAML configuration loading)
  - argparse (built-in Python CLI framework)
  - pytest 8.0.0 (testing framework)
  - pytest-cov 4.1.0 (test coverage)
- **Integration Points**: 
  - Configuration system must work with all existing components
  - CLI must provide access to all functionality
  - ResumeConverter must orchestrate existing pipeline

## Risk Mitigation

- **Risk**: Configuration complexity affecting usability
  - **Mitigation**: Provide comprehensive defaults and clear documentation
- **Risk**: CLI interface being difficult to use
  - **Mitigation**: Extensive help documentation and intuitive command structure
- **Risk**: Integration breaking existing functionality
  - **Mitigation**: Maintain backward compatibility, comprehensive test coverage
- **Risk**: Performance issues with batch processing
  - **Mitigation**: Implement progress tracking, optimize for large files

## Rollback Strategy

If issues arise:

1. Git reset to last stable commit on feature branch
2. Maintain existing component functionality
3. Incremental rollback by component (CLI, converter, config)
4. Document all breaking changes and migrations needed

## Integration Points

- **Input**: Configuration files (YAML) and markdown resumes
- **Configuration**: YAML-based system for all customization
- **Orchestration**: ResumeConverter coordinates all existing components
- **Interface**: CLI provides user access to all functionality
- **Output**: Complete pipeline from markdown to styled outputs
- **Testing**: End-to-end validation of complete system

## Success Criteria

- [ ] All Phase 6 GitHub issues (#21-25, #32) closed with documentation
- [ ] Configuration system loads and validates YAML settings
- [ ] ResumeConverter orchestrates all components successfully
- [ ] CLI interface supports single file and batch processing
- [ ] CLI provides comprehensive help and error messages
- [ ] Integration tests validate complete pipeline functionality
- [ ] >90% test coverage for all new components
- [ ] Sample files and documentation created
- [ ] End-to-end validation passes all scenarios
- [ ] Performance benchmarks maintained for batch processing

## Quality Gates

- [ ] YAML configuration validates correctly with pydantic
- [ ] ResumeConverter handles all error scenarios gracefully
- [ ] CLI follows argparse best practices and conventions
- [ ] All unit tests pass consistently (pytest)
- [ ] Integration tests cover all conversion scenarios
- [ ] Test coverage meets 90% threshold
- [ ] Sample resume converts to all formats (HTML, PDF, DOCX)
- [ ] CLI help documentation is comprehensive and clear
- [ ] Error messages are user-friendly and actionable
- [ ] Performance tests show acceptable processing speed

## Phase 6 Completion Definition

Phase 6 will be considered complete when:

1. **Configuration Requirements Met**
   - YAML configuration system operational
   - Default configuration works out-of-box
   - Custom configuration loading validated
   - Configuration validation comprehensive

2. **Integration Requirements Met**
   - ResumeConverter orchestrates all components
   - CLI provides full system access
   - Batch processing functional
   - Error handling comprehensive

3. **Quality Standards Achieved**
   - >90% test coverage across all new components
   - Integration tests validate complete pipeline
   - Performance benchmarks maintained
   - Documentation complete with examples

4. **User Experience Validated**
   - CLI is intuitive and well-documented
   - Sample files demonstrate functionality
   - Error messages guide users effectively
   - Production-ready tool delivered
