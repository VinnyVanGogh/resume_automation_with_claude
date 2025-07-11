# Resume Automation Tool

A Python-based resume conversion pipeline that transforms Markdown-formatted resumes into multiple ATS-optimized formats.

## Features

- Convert Markdown resumes to PDF, HTML, and DOCX formats
- ATS-optimized formatting and styling
- Batch processing capabilities
- Configurable themes and styling
- Command-line interface with comprehensive options

## Installation

```bash
# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

## Usage

```bash
# Convert single resume
resume-convert resume.md

# Convert with specific format
resume-convert resume.md --format pdf

# Batch convert multiple resumes
resume-convert *.md --batch --output-dir outputs/
```

## Development

This project uses:
- Python 3.12+
- Click for CLI interface
- Pydantic for data validation
- WeasyPrint for PDF generation
- pytest for testing

## License

MIT License