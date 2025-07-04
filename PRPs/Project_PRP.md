# Resume Formatting and Automation PRP (Product Requirement Prompt)

## Product Overview

**Goal**: Create a Python-based resume conversion pipeline that transforms Markdown-formatted resumes into multiple ATS-optimized formats (PDF, DOCX, HTML) with consistent styling and structure.

**Justification**: Technical professionals often maintain resumes in Markdown for version control and simplicity, but need polished, ATS-compliant outputs for job applications. This tool bridges that gap with automation.

## Context

### Input Format Example

```markdown
# John Smith

**Email**: john.smith@email.com | **Phone**: (555) 123-4567  
**LinkedIn**: linkedin.com/in/johnsmith | **GitHub**: github.com/johnsmith

## Summary

Experienced software engineer with 8+ years developing scalable web applications...

## Experience

### Senior Software Engineer | TechCorp Inc.

_January 2020 - Present_

- Led migration of monolithic application to microservices architecture
- Implemented CI/CD pipeline reducing deployment time by 60%
- Mentored team of 5 junior developers

### Software Engineer | StartupXYZ

_June 2017 - December 2019_

- Built RESTful APIs serving 1M+ daily requests
- Optimized database queries improving response time by 40%

## Education

### B.S. Computer Science | State University

_2013 - 2017_

## Skills

**Languages**: Python, JavaScript, Java, SQL  
**Frameworks**: Django, React, Spring Boot  
**Tools**: Docker, Kubernetes, AWS, Git
```

### Directory Structure

```
resume-automation/
├── src/
│   ├── __init__.py
│   ├── parser.py          # Markdown parsing logic
│   ├── formatter.py       # ATS formatting rules
│   ├── generator.py       # Output generation
│   └── templates/         # Template files
│       ├── resume.html
│       └── styles.css
├── tests/
│   ├── test_parser.py
│   ├── test_formatter.py
│   └── test_generator.py
├── examples/
│   ├── sample_resume.md
│   └── output/
├── ai_docs/
│   ├── markdown_parsing.md
│   └── ats_guidelines.md
├── requirements.txt
└── README.md
```

### Dependencies

```txt
# requirements.txt
mistune==3.0.2          # Markdown parsing
python-docx==1.1.0      # DOCX generation
weasyprint==60.2        # PDF generation
jinja2==3.1.3          # Template engine
pyyaml==6.0.1          # Config handling
black==24.1.1          # Code formatting
pytest==8.0.0          # Testing
pytest-cov==4.1.0      # Coverage
mypy==1.8.0            # Type checking
```

## Implementation Details and Strategy

### Architecture Pattern

```python
# src/parser.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import mistune

@dataclass
class ResumeSection:
    """Represents a parsed resume section"""
    title: str
    content: List[str]
    level: int
    metadata: Optional[Dict[str, str]] = None

class MarkdownResumeParser:
    """Parse Markdown resume into structured data"""

    def __init__(self):
        self.renderer = ATSRenderer()
        self.markdown = mistune.create_markdown(renderer=self.renderer)

    def parse(self, markdown_content: str) -> Dict[str, ResumeSection]:
        """Parse markdown into structured resume sections"""
        # Implementation details...
        pass

# src/formatter.py
class ATSFormatter:
    """Apply ATS-compliant formatting rules"""

    ATS_RULES = {
        "headers": ["Summary", "Experience", "Education", "Skills"],
        "date_format": r"\w+ \d{4} - (Present|\w+ \d{4})",
        "bullet_prefix": "•",
        "max_line_length": 80
    }

    def format_section(self, section: ResumeSection) -> ResumeSection:
        """Apply ATS formatting to a section"""
        # Standardize headers
        # Format dates consistently
        # Ensure bullet points
        pass
```

### Key Implementation Steps

1. **Parsing Pipeline**

   ```python
   # Parse Markdown → Extract sections → Validate structure → Apply ATS rules
   parser = MarkdownResumeParser()
   formatter = ATSFormatter()
   generator = ResumeGenerator()

   sections = parser.parse(markdown_content)
   formatted = formatter.format_all(sections)
   outputs = generator.generate_all_formats(formatted)
   ```

2. **ATS Optimization Rules**

   - Use standard section headers (Experience, Education, Skills)
   - Consistent date formatting (Month YYYY - Month YYYY)
   - Bullet points with action verbs
   - No tables, images, or complex formatting
   - Keywords extracted and emphasized

3. **Output Generation**
   - HTML: Jinja2 templates with semantic markup
   - PDF: WeasyPrint with print-optimized CSS
   - DOCX: python-docx with standard styles

## Validation Gates

### 1. Input Validation

```python
def validate_markdown_structure(content: str) -> ValidationResult:
    """Ensure markdown has required sections"""
    required_sections = ["Experience", "Education", "Skills"]
    errors = []

    for section in required_sections:
        if f"## {section}" not in content:
            errors.append(f"Missing required section: {section}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)
```

### 2. ATS Compliance Checks

```python
# tests/test_ats_compliance.py
def test_ats_formatting():
    """Validate ATS compliance of output"""
    output = generator.generate_docx(sample_resume)

    # Check for tables (ATS unfriendly)
    assert not contains_tables(output)

    # Verify standard headers
    assert all(header in output for header in ATS_HEADERS)

    # Validate date formats
    assert validate_date_formats(output)
```

### 3. Output Quality Gates

- **Type Safety**: `mypy src/ --strict`
- **Code Quality**: `black src/ --check && ruff check src/`
- **Test Coverage**: `pytest --cov=src --cov-report=term-missing --cov-fail-under=90`
- **Integration Tests**: End-to-end conversion of sample resumes

### 4. Performance Benchmarks

- Parse time < 100ms for typical resume
- Total conversion time < 1 second
- Memory usage < 50MB

## Usage Example

```python
# example_usage.py
from resume_automation import ResumeConverter

# Initialize converter with config
converter = ResumeConverter(config_path="config.yaml")

# Convert single resume
markdown_content = open("resume.md").read()
results = converter.convert(
    markdown_content,
    outputs=["pdf", "docx", "html"],
    theme="professional"
)

# Batch processing
for resume_path in Path("resumes/").glob("*.md"):
    converter.convert_file(resume_path, output_dir="output/")
```

## Configuration

```yaml
# config.yaml
ats:
  standard_headers:
    - Summary
    - Experience
    - Education
    - Skills
    - Certifications

  keyword_emphasis:
    min_occurrences: 2
    highlight_method: "bold"

output:
  pdf:
    page_size: "Letter"
    margins: "0.5in"
    font_family: "Arial"
    font_size: 11

  docx:
    style_template: "professional"
    line_spacing: 1.15
```

## Error Handling

```python
class ResumeConversionError(Exception):
    """Base exception for resume conversion errors"""
    pass

class InvalidMarkdownError(ResumeConversionError):
    """Raised when markdown structure is invalid"""
    pass

class ATSComplianceError(ResumeConversionError):
    """Raised when output fails ATS compliance checks"""
    pass
```

## Success Criteria

1. **Functional Requirements**

   - ✓ Parses standard Markdown resume format
   - ✓ Generates PDF, DOCX, and HTML outputs
   - ✓ Maintains consistent formatting across outputs
   - ✓ Passes ATS scanning tests

2. **Non-Functional Requirements**

   - ✓ Processes resume in < 1 second
   - ✓ Handles edge cases gracefully
   - ✓ 90%+ test coverage
   - ✓ Type-safe implementation

3. **Extensibility**
   - ✓ Easy to add new output formats
   - ✓ Configurable styling options
   - ✓ Plugin architecture for custom processors

## AI Implementation Notes

When implementing this PRP:

1. Start with the parser module using the mistune examples in `ai_docs/`
2. Implement validation gates early to catch issues
3. Use type hints throughout for better code generation
4. Follow the test-driven approach with provided test examples
5. Reference ATS guidelines in `ai_docs/ats_guidelines.md` for formatting rules

## Appendix: Sample Outputs

### Expected HTML Output Structure

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>John Smith - Resume</title>
    <style>
      /* ATS-friendly CSS */
      body {
        font-family: Arial, sans-serif;
      }
      h1 {
        font-size: 24px;
      }
      h2 {
        font-size: 18px;
        border-bottom: 1px solid #000;
      }
      /* ... */
    </style>
  </head>
  <body>
    <header>
      <h1>John Smith</h1>
      <p>Email: john.smith@email.com | Phone: (555) 123-4567</p>
    </header>
    <!-- Sections follow -->
  </body>
</html>
```
