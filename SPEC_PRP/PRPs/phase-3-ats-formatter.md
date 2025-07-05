# Phase 3: ATS Formatting Engine PRP

## Specification: ATS Compliance Formatter Development

Transform parsed resume data into ATS-compliant format with standardized headers, dates, and formatting rules to ensure optimal compatibility with Applicant Tracking Systems.

## Current State Assessment

```yaml
current_state:
  files:
    - src/parser.py (Phase 2 complete - MarkdownResumeParser implemented)
    - src/models.py (Pydantic resume data models)
    - src/validation.py (input validation system)
    - tests/test_parser.py (comprehensive parser tests)
  behavior:
    - Parse markdown resumes into structured Pydantic models
    - Validate input structure and content
    - Extract all sections with proper hierarchy
    - Return typed data structures
  issues:
    - No ATS formatting rules applied to parsed data
    - No date standardization across sections
    - No header standardization for ATS compliance
    - No formatting validation for ATS requirements
```

## Desired State

```yaml
desired_state:
  files:
    - src/formatter.py (ATS formatting engine)
    - src/formatter/tests/* (comprehensive formatter test suite)
    - Updated integration with existing parser
  behavior:
    - Apply ATS compliance rules to parsed resume data
    - Standardize dates to "Month YYYY - Month YYYY" format
    - Map header variations to ATS-standard headers
    - Format content for optimal ATS parsing
    - Validate ATS compliance requirements
  benefits:
    - ATS-optimized resume formatting
    - Consistent date and header standardization
    - Configurable formatting rules
    - >90% test coverage for formatter
```

## Hierarchical Objectives

### High-Level Goal

Complete Phase 3 ATS formatting engine with comprehensive compliance rules, date/header standardization, and extensive testing to bridge parser output with Phase 4 generators.

### Mid-Level Milestones

1. **Core ATS Formatter** - Implement main formatting engine with compliance rules
2. **Date Standardization** - Handle various date formats and standardize output
3. **Header Standardization** - Map header variations to ATS-compliant standards
4. **Comprehensive Testing** - Achieve >90% test coverage with edge case validation

### Low-Level Tasks

#### Task 1: Implement Core ATS Formatter

```yaml
task_name: implement_ats_formatter
action: CREATE
file: src/formatter.py
changes: |
  - Create ATSFormatter class with core formatting methods
  - Implement format_resume() method accepting ResumeData from parser
  - Add ATS compliance rules (line length, bullet formatting, section order)
  - Implement configurable rule system for different ATS types
  - Add content optimization for keyword density and structure
  - Return formatted resume data ready for Phase 4 generators
validation:
  - command: "uv run mypy src/formatter.py"
  - expect: "Success: no issues found"
```

#### Task 2: Add Date Standardization System

```yaml
task_name: implement_date_standardization
action: ADD
file: src/formatter.py
changes: |
  - Create DateStandardizer class within formatter module
  - Add regex patterns for common date formats:
    - "January 2020 - Present", "Jan 2020 - Dec 2021"
    - "2020 - 2021", "Jan 2020 - Current"
  - Implement standardize_date() method returning "Month YYYY - Month YYYY"
  - Handle "Present", "Current", "Now" variations consistently
  - Add date validation (start date < end date)
  - Integrate with ATSFormatter for all date fields
validation:
  - command: "uv run pytest tests/test_formatter.py::TestDateStandardizer -v"
  - expect: "PASSED"
```

#### Task 3: Create Header Standardization System

```yaml
task_name: implement_header_standardization
action: ADD
file: src/formatter.py
changes: |
  - Create HeaderStandardizer class within formatter module
  - Define ATS-standard headers mapping:
    - Summary/Objective → Summary
    - Work Experience/Employment → Experience
    - Education/Academic Background → Education
    - Skills/Technical Skills → Skills
    - Certifications/Certificates → Certifications
  - Implement case-insensitive header matching
  - Handle pluralization and common variations
  - Add standardize_header() method
  - Integrate with ATSFormatter for section headers
validation:
  - command: "uv run pytest tests/test_formatter.py::TestHeaderStandardizer -v"
  - expect: "PASSED"
```

#### Task 4: Integrate Formatter Components

```yaml
task_name: integrate_formatter_components
action: MODIFY
file: src/formatter.py
changes: |
  - Update ATSFormatter to use DateStandardizer and HeaderStandardizer
  - Add format_section() method for individual section processing
  - Implement format_content() for bullet point and text optimization
  - Add ATS compliance validation methods
  - Ensure seamless integration with Phase 2 Pydantic models
  - Add comprehensive docstrings and type hints
validation:
  - command: "uv run mypy src/formatter.py --strict"
  - expect: "Success: no issues found"
```

#### Task 5: Create Formatter Unit Tests

```yaml
task_name: create_formatter_unit_tests
action: CREATE
file: src/tests/test_formatter.py
changes: |
  - Test ATSFormatter core functionality
  - Test DateStandardizer with various input formats
  - Test HeaderStandardizer mapping and edge cases
  - Test ATS compliance rule validation
  - Test error handling for invalid inputs
  - Test configuration system for different ATS types
validation:
  - command: "uv run pytest src/tests/test_formatter.py -v"
  - expect: "All tests pass"
```

#### Task 6: Create Integration Tests

```yaml
task_name: create_formatter_integration_tests
action: ADD
file: src/tests/test_formatter.py
changes: |
  - Test end-to-end formatter with Phase 2 parser output
  - Test complete resume formatting workflow
  - Test with real-world resume samples
  - Test performance benchmarks (<100ms processing)
  - Test edge cases and error recovery
  - Validate ATS compliance of formatted output
validation:
  - command: "uv run pytest src/tests/test_formatter.py::TestIntegration -v"
  - expect: "All tests pass"
```

#### Task 7: Add Formatter to Main Tests

```yaml
task_name: update_main_tests
action: MODIFY
file: tests/test_formatter.py
changes: |
  - Create main test file for formatter module
  - Add import tests for formatter classes
  - Add basic functionality tests
  - Ensure proper module structure
validation:
  - command: "uv run pytest tests/test_formatter.py -v"
  - expect: "All tests pass"
```

#### Task 8: Verify Test Coverage

```yaml
task_name: verify_formatter_coverage
action: RUN
changes: |
  - Run full test suite with coverage for formatter module
  - Ensure >90% coverage for all formatter components
  - Generate detailed coverage report
  - Identify and test any uncovered code paths
validation:
  - command: "uv run pytest --cov=src.formatter --cov-report=term-missing --cov-fail-under=90"
  - expect: "Coverage >= 90%"
```

#### Task 9: Close GitHub Issues

```yaml
task_name: close_phase3_issues
action: CLOSE
changes: |
  - Close issue #9 (Implement ATS Formatter)
  - Close issue #10 (Add Date Standardization)
  - Close issue #11 (Create Header Standardization)
  - Close issue #12 (Add Formatter Tests)
validation:
  - command: "gh issue list --label phase-3 --state closed"
  - expect: "All phase-3 issues closed"
```

## Implementation Strategy

1. **Start with Core Infrastructure** - Build ATSFormatter foundation
2. **Add Specialized Components** - Layer date and header standardization
3. **Integrate and Validate** - Ensure seamless component interaction
4. **Test Comprehensively** - Build tests alongside implementation
5. **Optimize and Polish** - Performance tuning and edge case handling

## Dependencies

- **Phase 2 Complete**: Requires working parser with Pydantic models
- **External Libraries**: No new dependencies, uses existing mistune/pydantic
- **Integration Points**: Must work with parser output and prepare for Phase 4

## Risk Mitigation

- **Risk**: ATS requirements vary by system
  - **Mitigation**: Configurable rule sets, conservative default approach
- **Risk**: Date parsing edge cases
  - **Mitigation**: Comprehensive regex patterns, graceful fallback handling
- **Risk**: Performance impact on parsing pipeline
  - **Mitigation**: Benchmark early, optimize critical paths, maintain <100ms target
- **Risk**: Breaking Phase 2 integration
  - **Mitigation**: Maintain strict Pydantic model compatibility, comprehensive integration tests

## Rollback Strategy

If issues arise:

1. Git reset to last stable commit on feature branch
2. Revert individual formatter components if needed
3. Maintain Phase 2 functionality as fallback
4. Document any model changes for compatibility

## Integration Points

- **Input**: Pydantic ResumeData models from Phase 2 parser
- **Output**: ATS-formatted resume data for Phase 4 generators
- **Configuration**: Extensible rule system for different ATS requirements
- **Testing**: Builds on Phase 2 test patterns and infrastructure

## Success Criteria

- [ ] All Phase 3 GitHub issues (#9-12) closed with detailed documentation
- [ ] ATSFormatter successfully processes parsed resume data
- [ ] Date standardization handles all common input formats
- [ ] Header standardization maps variations to ATS-compliant headers
- [ ] >90% test coverage for formatter module achieved
- [ ] Integration tests pass with Phase 2 parser output
- [ ] Performance benchmarks meet <100ms processing target
- [ ] Code follows project conventions with type safety
- [ ] Formatter ready for Phase 4 generator integration

## Quality Gates

- [ ] Type checking passes with mypy --strict
- [ ] Code quality passes ruff linting
- [ ] All unit tests pass consistently
- [ ] Integration tests validate end-to-end workflow
- [ ] Performance benchmarks within target
- [ ] ATS compliance validation passes
- [ ] Documentation complete with examples