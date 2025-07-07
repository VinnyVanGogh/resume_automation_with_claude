# Phase 5: Templates & Styling System PRP

## Specification: Professional ATS-Compliant Template System

Design and implement a comprehensive template system with professional styling for HTML, PDF, and DOCX outputs, ensuring ATS compliance, accessibility, and visual appeal across all resume formats.

## Current State Assessment

```yaml
current_state:
  files:
    - src/templates/resume.html (basic Jinja2 template)
    - src/templates/styles.css (basic CSS styling)
    - src/generator/* (Phase 4 complete - output generators)
    - No DOCX template system implemented
    - No template tests or validation
  behavior:
    - Basic HTML template renders resume data
    - CSS provides minimal styling
    - Generators use templates but lack sophistication
    - No template inheritance or component reusability
    - No print-specific optimizations
  issues:
    - Templates lack professional polish and modern design
    - No semantic HTML structure for accessibility
    - Missing responsive design elements
    - No DOCX template/style configuration
    - No template validation or testing
    - Limited customization options
    - No theme support
```

## Desired State

```yaml
desired_state:
  files:
    - src/templates/
      ├── base.html (base template with inheritance)
      ├── resume.html (main resume template)
      ├── components/ (reusable template components)
      │   ├── header.html
      │   ├── summary.html
      │   ├── experience.html
      │   ├── education.html
      │   └── skills.html
      ├── styles/
      │   ├── base.css (core styles)
      │   ├── print.css (print-specific styles)
      │   ├── themes/ (theme variations)
      │   └── components.css (component styles)
      └── docx/
          ├── styles.yaml (DOCX style definitions)
          └── templates.yaml (DOCX template config)
    - src/templates/tests/ (comprehensive template tests)
  behavior:
    - Professional, modern template design
    - Semantic HTML5 with ARIA attributes
    - Responsive design for all screen sizes
    - Print-optimized CSS for PDF generation
    - DOCX templates with consistent styling
    - Theme support for customization
    - Component-based architecture
    - Comprehensive template testing
  benefits:
    - Professional-quality resume outputs
    - ATS-compliant across all formats
    - Accessible and semantic markup
    - Easy customization and theming
    - Consistent styling across formats
    - >95% test coverage for templates
    - Maintainable component architecture
```

## Hierarchical Objectives

### High-Level Goal

Complete Phase 5 template and styling system with professional, ATS-compliant, accessible templates that provide consistent, high-quality output across HTML, PDF, and DOCX formats.

### Mid-Level Milestones

1. **Enhanced HTML Template Architecture** - Build component-based, semantic HTML templates with inheritance
2. **Professional CSS Styling System** - Create comprehensive, print-optimized styling with theme support
3. **DOCX Template Configuration** - Implement style templates and configuration for Word documents
4. **Comprehensive Template Testing** - Achieve >95% test coverage with accessibility and ATS validation

### Low-Level Tasks

#### Task 1: Create Template Component Architecture

```yaml
task_name: create_template_architecture
action: CREATE
file: src/templates/base.html
changes: |
  - Create base template with HTML5 structure
  - Add proper DOCTYPE, lang attribute, and charset
  - Include meta viewport for responsive design
  - Add SEO and ATS-friendly meta tags
  - Create block structure for inheritance:
    - {% block title %} for dynamic titles
    - {% block styles %} for CSS inclusion
    - {% block content %} for main content
    - {% block scripts %} for JavaScript (if needed)
  - Add skip navigation links for accessibility
  - Include print-friendly meta tags
validation:
  - command: 'uv run python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader(''src/templates'')); env.get_template(''base.html'')"'
  - expect: "No template errors"
```

#### Task 2: Create Component Templates

```yaml
task_name: create_component_templates
action: CREATE
file: src/templates/components/header.html
changes: |
  - Create header component with contact information
  - Use semantic <header> element with microdata
  - Add proper heading hierarchy (h1 for name)
  - Include contact info with semantic markup:
    - Email with mailto: links
    - Phone with tel: links
    - LinkedIn/GitHub with proper rel attributes
  - Make component reusable with template variables
  - Repeat for all components:
    - summary.html (article element)
    - experience.html (section with articles)
    - education.html (section with articles)
    - skills.html (section with ul/li structure)
validation:
  - command: "ls src/templates/components/ | wc -l"
  - expect: "5"
```

#### Task 3: Update Main Resume Template

```yaml
task_name: update_resume_template
action: MODIFY
file: src/templates/resume.html
changes: |
  - Extend base.html template
  - Include all component templates
  - Add proper semantic structure:
    - <main> element for resume content
    - Logical section ordering
    - Proper heading hierarchy (h2 for sections)
  - Add schema.org microdata for better parsing
  - Include print page-break hints
  - Add conditional rendering for optional sections
  - Support for multiple resume formats/layouts
  - Add accessibility landmarks and ARIA labels
validation:
  - command: "uv run python -m pytest src/generator/tests/test_html_generator.py::test_template_structure -v"
  - expect: "PASSED"
```

#### Task 4: Create Professional Base Styles

```yaml
task_name: create_base_styles
action: CREATE
file: src/templates/styles/base.css
changes: |
  - Define CSS custom properties for theming:
    - --color-primary, --color-secondary
    - --font-family-main, --font-family-headings
    - --spacing-unit, --line-height
  - Set professional typography:
    - System font stack for ATS compliance
    - Proper font sizes and line heights
    - Consistent spacing scale
  - Add CSS reset for consistency
  - Define base element styles
  - Create utility classes for common patterns
  - Ensure high contrast for readability
validation:
  - command: "npx stylelint src/templates/styles/base.css"
  - expect: "No errors"
```

#### Task 5: Create Print-Optimized Styles

```yaml
task_name: create_print_styles
action: CREATE
file: src/templates/styles/print.css
changes: |
  - Add @media print rules for PDF generation
  - Set page size and margins:
    - @page { size: letter; margin: 0.5in; }
  - Remove unnecessary elements (nav, links underlines)
  - Optimize typography for print:
    - Serif fonts for body text
    - Adjusted line heights
    - Proper widow/orphan control
  - Add page break controls:
    - page-break-inside: avoid for sections
    - page-break-before for major sections
  - Ensure links show URLs in print
  - Optimize colors for black & white printing
validation:
  - command: "grep -c '@media print' src/templates/styles/print.css"
  - expect: ">=1"
```

#### Task 6: Create Component Styles

```yaml
task_name: create_component_styles
action: CREATE
file: src/templates/styles/components.css
changes: |
  - Style header component:
    - Professional name display
    - Contact info layout (responsive)
    - Proper spacing and alignment
  - Style experience component:
    - Clear job title/company/date layout
    - Bullet point formatting
    - Consistent spacing
  - Style education component:
    - Degree/institution layout
    - Date alignment
  - Style skills component:
    - Multi-column layout for skills
    - Responsive skill grouping
  - Add hover states and transitions
  - Ensure all styles are ATS-friendly
validation:
  - command: "npx stylelint src/templates/styles/components.css"
  - expect: "No errors"
```

#### Task 7: Create Theme System

```yaml
task_name: create_theme_system
action: CREATE
file: src/templates/styles/themes/professional.css
changes: |
  - Create professional theme with:
    - Conservative color palette
    - Traditional typography
    - Classic layout spacing
  - Override CSS custom properties
  - Create additional themes:
    - modern.css (contemporary design)
    - minimal.css (clean, simple)
    - tech.css (developer-focused)
  - Each theme should maintain ATS compliance
  - Document theme variables
validation:
  - command: "ls src/templates/styles/themes/ | grep -c '.css'"
  - expect: ">=4"
```

#### Task 8: Create DOCX Style Configuration

```yaml
task_name: create_docx_styles
action: CREATE
file: src/templates/docx/styles.yaml
changes: |
  - Define DOCX style configuration:
    - Document properties (margins, page size)
    - Paragraph styles:
      - Normal: font, size, spacing
      - Heading1: resume name style
      - Heading2: section headers
      - BulletList: experience bullets
    - Character styles:
      - Strong: bold emphasis
      - Emphasis: italic text
    - Table styles (if needed for layout)
  - Map styles to python-docx API
  - Ensure ATS compatibility
  - Add style inheritance rules
validation:
  - command: 'uv run python -c "import yaml; yaml.safe_load(open(''src/templates/docx/styles.yaml''))"'
  - expect: "Valid YAML"
```

#### Task 9: Create DOCX Template Configuration

```yaml
task_name: create_docx_templates
action: CREATE
file: src/templates/docx/templates.yaml
changes: |
  - Define DOCX template structure:
    - Section ordering and spacing
    - Content formatting rules
    - Bullet point prefixes
    - Date formatting patterns
  - Create template variations:
    - standard: traditional layout
    - modern: contemporary format
    - compact: space-optimized
  - Define section-specific rules
  - Add conditional formatting logic
  - Ensure cross-platform compatibility
validation:
  - command: 'uv run python -c "import yaml; yaml.safe_load(open(''src/templates/docx/templates.yaml''))"'
  - expect: "Valid YAML"
```

#### Task 10: Create HTML Template Tests

```yaml
task_name: create_html_template_tests
action: CREATE
file: src/templates/tests/test_html_templates.py
changes: |
  - Test template inheritance chain
  - Validate HTML5 structure and semantics
  - Test component rendering with data
  - Verify accessibility:
    - Heading hierarchy
    - ARIA attributes
    - Landmark elements
  - Test responsive meta tags
  - Validate microdata markup
  - Test conditional rendering
  - Check for XSS vulnerabilities
  - Validate against W3C standards
validation:
  - command: "uv run pytest src/templates/tests/test_html_templates.py -v"
  - expect: "All tests pass"
```

#### Task 11: Create CSS Testing Suite

```yaml
task_name: create_css_tests
action: CREATE
file: src/templates/tests/test_css_styles.py
changes: |
  - Test CSS validity and syntax
  - Validate color contrast ratios (WCAG AA)
  - Test responsive breakpoints
  - Verify print styles generate correctly
  - Test theme system overrides
  - Validate CSS custom properties
  - Check for unused styles
  - Test component isolation
  - Verify ATS-friendly styling
  - Benchmark CSS performance
validation:
  - command: "uv run pytest src/templates/tests/test_css_styles.py -v"
  - expect: "All tests pass"
```

#### Task 12: Create DOCX Template Tests

```yaml
task_name: create_docx_template_tests
action: CREATE
file: src/templates/tests/test_docx_templates.py
changes: |
  - Test YAML configuration validity
  - Validate style definitions
  - Test template structure logic
  - Verify python-docx compatibility
  - Test style application
  - Check formatting consistency
  - Validate ATS compliance
  - Test cross-platform compatibility
  - Verify template variations
validation:
  - command: "uv run pytest src/templates/tests/test_docx_templates.py -v"
  - expect: "All tests pass"
```

#### Task 13: Create Integration Tests

```yaml
task_name: create_template_integration_tests
action: CREATE
file: src/templates/tests/test_integration.py
changes: |
  - Test templates with real resume data
  - Verify consistent output across formats
  - Test theme switching functionality
  - Validate accessibility compliance
  - Test print/PDF generation quality
  - Verify ATS compliance across outputs
  - Test edge cases (long names, many skills)
  - Performance benchmarks
  - Visual regression testing setup
validation:
  - command: "uv run pytest src/templates/tests/test_integration.py -v"
  - expect: "All tests pass"
```

#### Task 14: Update Generator Integration

```yaml
task_name: update_generator_integration
action: MODIFY
file: src/generator/html_generator.py
changes: |
  - Update to use new template structure
  - Add theme support to generator
  - Implement component-based rendering
  - Add template caching for performance
  - Update CSS inclusion logic
  - Add accessibility metadata
validation:
  - command: "uv run pytest src/generator/tests/test_html_generator.py -v"
  - expect: "All tests pass"
```

#### Task 15: Verify Test Coverage

```yaml
task_name: verify_template_coverage
action: RUN
changes: |
  - Run full test suite for templates
  - Ensure >95% coverage for template code
  - Generate coverage report
  - Test all template paths
  - Validate CSS coverage
validation:
  - command: "uv run pytest src/templates/tests/ --cov=src.templates --cov-report=term-missing --cov-fail-under=95"
  - expect: "Coverage >= 95%"
```

#### Task 16: Close GitHub Issues

```yaml
task_name: close_phase5_issues
action: CLOSE
changes: |
  - Close issue #17 (Create HTML Templates)
  - Close issue #18 (Create CSS Styles)
  - Close issue #19 (Create DOCX Templates)
  - Close issue #20 (Add Template Tests)
validation:
  - command: "gh issue list --label phase-5 --state closed"
  - expect: "All phase-5 issues closed"
```

## Implementation Strategy

1. **Start with Architecture** - Build template component system foundation
2. **HTML/CSS First** - Create and test web templates thoroughly
3. **Add DOCX Configuration** - Layer in Word document styling
4. **Test Comprehensively** - Build tests alongside each component
5. **Polish and Optimize** - Refine for professional quality

## Dependencies

- **Phase 4 Complete**: Requires working generators that use templates
- **External Tools**:
  - Jinja2 3.1.3 (template engine)
  - stylelint (CSS validation)
  - axe-core (accessibility testing)
- **Integration Points**: Must work with existing generator architecture

## Risk Mitigation

- **Risk**: CSS complexity affecting ATS parsing
  - **Mitigation**: Keep styles simple, test with multiple ATS systems
- **Risk**: Template changes breaking existing functionality
  - **Mitigation**: Comprehensive test coverage, gradual migration
- **Risk**: Accessibility compliance challenges
  - **Mitigation**: Use automated testing tools, follow WCAG guidelines
- **Risk**: Cross-browser/platform compatibility
  - **Mitigation**: Use standard CSS, test across environments

## Rollback Strategy

If issues arise:

1. Git reset to last stable commit on feature branch
2. Revert to previous template versions
3. Maintain backward compatibility during transition
4. Document all breaking changes

## Integration Points

- **Input**: ResumeData models from generator layer
- **Templates**: Enhanced Jinja2 template system
- **Styles**: Comprehensive CSS architecture
- **Output**: Professional, styled resume outputs
- **Configuration**: Theme and customization system

## Success Criteria

- [ ] All Phase 5 GitHub issues (#17-20) closed with documentation
- [ ] Professional HTML templates with semantic markup
- [ ] Comprehensive CSS system with print optimization
- [ ] DOCX template configuration implemented
- [ ] > 95% test coverage for all template code
- [ ] Accessibility tests pass WCAG AA standards
- [ ] ATS compliance validated across formats
- [ ] Theme system functional with multiple options
- [ ] Performance benchmarks maintained
- [ ] Visual quality meets professional standards

## Quality Gates

- [ ] HTML validates against W3C standards
- [ ] CSS passes stylelint validation
- [ ] Accessibility tests pass (axe-core)
- [ ] Color contrast meets WCAG AA
- [ ] All unit tests pass consistently
- [ ] Integration tests validate full pipeline
- [ ] Visual regression tests pass
- [ ] Documentation complete with examples

## Phase 5 Completion Definition

Phase 5 will be considered complete when:

1. **Template Requirements Met**

   - Component-based architecture implemented
   - Professional styling across all formats
   - Theme system operational
   - DOCX templates configured

2. **Quality Standards Achieved**

   - > 95% test coverage across templates
   - Accessibility compliance verified
   - ATS compliance validated
   - Professional visual quality confirmed

3. **Integration Validated**
   - Templates work seamlessly with generators
   - Performance targets maintained
   - All formats produce consistent output
   - Real-world resumes render beautifully
