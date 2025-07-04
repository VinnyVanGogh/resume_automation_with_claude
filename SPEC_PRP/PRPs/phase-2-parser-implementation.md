# Phase 2: Parser Implementation PRP

## Specification: Core Parser Development

Transform the skeleton parser structure into a fully functional Markdown resume parser with ATS-compliant rendering capabilities.

## Current State Assessment

```yaml
current_state:
  files:
    - src/parser.py (skeleton with NotImplementedError)
    - src/types.py (basic exceptions and ValidationResult)
    - tests/test_parser.py (basic tests, most skipped)
  behavior:
    - Parser classes exist but have no implementation
    - ATSRenderer is empty shell
    - MarkdownResumeParser.parse() raises NotImplementedError
  issues:
    - No actual parsing functionality
    - No section detection logic
    - No validation implementation
    - No data models for resume structure
```

## Desired State

```yaml
desired_state:
  files:
    - src/parser.py (fully implemented parser)
    - src/models.py (Pydantic data models)
    - src/validation.py (input validation)
    - src/parser/tests/* (comprehensive test suite)
  behavior:
    - Parse markdown resumes into structured data
    - Extract all sections with proper hierarchy
    - Validate input structure and content
    - Return typed Pydantic models
  benefits:
    - Reliable markdown parsing
    - Type-safe data structures
    - Comprehensive validation
    - >90% test coverage
```

## Hierarchical Objectives

### High-Level Goal

Complete Phase 2 parser implementation with full validation and testing to enable structured resume data extraction.

### Mid-Level Milestones

1. **Core Parser Infrastructure** - Implement basic parsing functionality
2. **Data Models** - Create Pydantic models for resume structure
3. **Validation System** - Add comprehensive input validation
4. **Test Coverage** - Achieve >90% test coverage

### Low-Level Tasks

#### Task 1: Create Pydantic Resume Models

```yaml
task_name: create_pydantic_models
action: CREATE
file: src/models.py
changes: |
  - Create ContactInfo model (name, email, phone, linkedin, github)
  - Create Experience model (title, company, dates, bullets)
  - Create Education model (degree, school, dates, details)
  - Create Skills model (categories, items)
  - Create ResumeData root model containing all sections
validation:
  - command: "uv run mypy src/models.py"
  - expect: "Success: no issues found"
```

#### Task 2: Implement Markdown Parser Base

```yaml
task_name: implement_markdown_parser
action: MODIFY
file: src/parser.py
changes: |
  - Implement parse() method in MarkdownResumeParser
  - Add section detection logic using regex patterns
  - Parse contact info from header
  - Extract sections by ## headers
  - Handle nested content (### subsections)
validation:
  - command: "uv run pytest tests/test_parser.py::TestMarkdownResumeParser::test_parse_simple_resume -v"
  - expect: "PASSED"
```

#### Task 3: Implement ATS Renderer

```yaml
task_name: implement_ats_renderer
action: MODIFY
file: src/parser.py
changes: |
  - Extend mistune.renderers.BaseRenderer in ATSRenderer
  - Override heading() method for section detection
  - Override list_item() for bullet extraction
  - Override paragraph() for content parsing
  - Add section boundary tracking
validation:
  - command: "uv run pytest tests/test_parser.py::TestATSRenderer -v"
  - expect: "PASSED"
```

#### Task 4: Create Resume Validator

```yaml
task_name: create_validator
action: CREATE
file: src/validation.py
changes: |
  - Create ResumeValidator class
  - Add validate_structure() method
  - Check required sections (Contact, Experience, Education)
  - Validate date formats
  - Check content quality (min lengths)
  - Return ValidationResult with errors/warnings
validation:
  - command: "uv run mypy src/validation.py"
  - expect: "Success: no issues found"
```

#### Task 5: Update Parser Integration

```yaml
task_name: integrate_validation_models
action: MODIFY
file: src/parser.py
changes: |
  - Import Pydantic models and validator
  - Update parse() to return ResumeData model
  - Add validation step before returning
  - Handle InvalidMarkdownError appropriately
  - Add comprehensive docstrings
validation:
  - command: "uv run pytest tests/test_parser.py -v"
  - expect: "All tests pass"
```

#### Task 6: Create Parser Tests

```yaml
task_name: create_parser_tests
action: CREATE
file: src/parser/tests/test_parser.py
changes: |
  - Test parsing complete resume samples
  - Test section extraction accuracy
  - Test contact info parsing
  - Test experience/education parsing
  - Test error handling for malformed input
  - Test edge cases (missing sections, empty content)
validation:
  - command: "uv run pytest src/parser/tests/test_parser.py -v"
  - expect: "All tests pass"
```

#### Task 7: Create Validation Tests

```yaml
task_name: create_validation_tests
action: CREATE
file: src/parser/tests/test_validation.py
changes: |
  - Test required section validation
  - Test date format validation
  - Test content quality checks
  - Test error message clarity
  - Test configurable rules
validation:
  - command: "uv run pytest src/parser/tests/test_validation.py -v"
  - expect: "All tests pass"
```

#### Task 8: Create Integration Tests

```yaml
task_name: create_integration_tests
action: CREATE
file: src/parser/tests/test_integration.py
changes: |
  - Test end-to-end parsing with sample resumes
  - Test parser + validator integration
  - Test real-world resume formats
  - Test performance benchmarks
  - Add fixtures for test data
validation:
  - command: "uv run pytest src/parser/tests/test_integration.py -v"
  - expect: "All tests pass"
```

#### Task 9: Update Module Tests

```yaml
task_name: update_root_tests
action: MODIFY
file: tests/test_parser.py
changes: |
  - Remove skip decorators
  - Update tests to work with new implementation
  - Add more comprehensive test cases
  - Ensure proper imports
validation:
  - command: "uv run pytest tests/test_parser.py -v"
  - expect: "All tests pass"
```

#### Task 10: Verify Test Coverage

```yaml
task_name: verify_coverage
action: RUN
changes: |
  - Run full test suite with coverage
  - Ensure >90% coverage for parser module
  - Generate coverage report
validation:
  - command: "uv run pytest --cov=src.parser --cov-report=term-missing"
  - expect: "Coverage >= 90%"
```

#### Task 11: Close GitHub Issues

```yaml
task_name: close_phase2_issues
action: CLOSE
changes: |
  - Close issue #5 (Implement Markdown Parser)
  - Close issue #6 (Create ATS Renderer)
  - Close issue #7 (Add Input Validation)
  - Close issue #8 (Create Parser Tests)
validation:
  - command: "gh issue list --label phase-2 --state closed"
  - expect: "All phase-2 issues closed"
```

## Implementation Strategy

1. **Start with Data Models** - Define clear data structures first
2. **Build Parser Core** - Implement basic parsing functionality
3. **Add Validation** - Layer validation on top of parsing
4. **Test Thoroughly** - Build tests alongside implementation
5. **Iterate and Refine** - Use tests to drive improvements

## Risk Mitigation

- **Risk**: Complex markdown variations
  - **Mitigation**: Start with simple format, add complexity gradually
- **Risk**: Performance with large resumes

  - **Mitigation**: Add benchmarks early, optimize if needed

- **Risk**: Breaking existing structure
  - **Mitigation**: Maintain backward compatibility, update imports carefully

## Rollback Strategy

If issues arise:

1. Git reset to last stable commit
2. Revert individual files if needed
3. Keep original skeleton as fallback
4. Document any API changes

## Integration Points

- Parser integrates with formatter (Phase 3)
- Models used throughout pipeline
- Validation reused in other modules
- Tests establish patterns for project

## Success Criteria

- [ ] All Phase 2 GitHub issues closed
- [ ] Parser successfully extracts all resume sections
- [ ] Validation catches malformed input
- [ ] > 90% test coverage achieved
- [ ] All tests pass consistently
- [ ] Code follows project conventions
- [ ] Type checking passes with mypy --strict
