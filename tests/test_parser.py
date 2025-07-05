"""
Tests for the markdown resume parser module.
"""

import pytest
from src.parser import MarkdownResumeParser, ResumeSection, ATSRenderer
from src.models import ResumeData, ContactInfo
from src.custom_types import InvalidMarkdownError


class TestResumeSection:
    """Test cases for ResumeSection dataclass."""
    
    def test_resume_section_creation(self):
        """Test basic ResumeSection creation."""
        section = ResumeSection(
            title="Experience",
            content=["Senior Software Engineer", "Built scalable applications"],
            level=2
        )
        
        assert section.title == "Experience"
        assert len(section.content) == 2
        assert section.level == 2
        assert section.metadata is None
    
    def test_resume_section_with_metadata(self):
        """Test ResumeSection creation with metadata."""
        metadata = {"company": "TechCorp", "duration": "2 years"}
        section = ResumeSection(
            title="Experience",
            content=["Senior Software Engineer"],
            level=2,
            metadata=metadata
        )
        
        assert section.metadata == metadata


class TestATSRenderer:
    """Test cases for ATSRenderer class."""
    
    def test_ats_renderer_initialization(self):
        """Test ATSRenderer can be initialized."""
        renderer = ATSRenderer()
        assert renderer is not None
        assert renderer.sections == {}
        assert renderer.current_section is None
        assert renderer.current_section_content == []
        assert renderer.current_level == 0

    def test_ats_renderer_heading_processing(self):
        """Test heading processing in renderer."""
        renderer = ATSRenderer()
        
        result = renderer.heading('Experience', 2)
        
        assert 'Experience' in result
        assert renderer.current_section == 'experience'
        assert renderer.current_level == 2

    def test_ats_renderer_finalize_sections(self):
        """Test finalizing sections in renderer."""
        renderer = ATSRenderer()
        
        # Simulate processing content
        renderer.current_section = 'test'
        renderer.current_level = 2
        renderer.current_section_content = ['Test content']
        
        sections = renderer.finalize_sections()
        
        assert 'test' in sections
        assert sections['test'].title == 'test'
        assert sections['test'].content == ['Test content']
        assert sections['test'].level == 2


class TestMarkdownResumeParser:
    """Test cases for MarkdownResumeParser class."""
    
    def test_parser_initialization(self):
        """Test parser can be initialized."""
        parser = MarkdownResumeParser()
        assert parser is not None
        assert hasattr(parser, 'renderer')
        assert hasattr(parser, 'markdown')
        assert hasattr(parser, 'validator')
        assert parser.validate_input is True

    def test_parser_initialization_with_options(self):
        """Test parser initialization with custom options."""
        parser = MarkdownResumeParser(validate_input=False, strict_validation=True)
        assert parser.validate_input is False
        assert parser.validator.strict_mode is True
    
    def test_parse_simple_resume(self):
        """Test parsing a simple markdown resume."""
        parser = MarkdownResumeParser()
        sample_markdown = """
# John Smith
john.smith@email.com | (555) 123-4567

## Experience

### Software Engineer
- Built web applications
- Worked with Python and JavaScript
"""
        result = parser.parse(sample_markdown)
        
        # Check that we get a ResumeData object
        assert result is not None
        assert hasattr(result, 'contact')
        assert hasattr(result, 'experience')
        assert hasattr(result, 'education')
        
        # Check basic contact info parsing
        assert result.contact.name == "John Smith"
        assert result.contact.email == "john.smith@email.com"
        assert result.contact.phone == "(555) 123-4567"

    def test_parse_with_warnings(self):
        """Test parsing with warnings functionality."""
        parser = MarkdownResumeParser()
        sample_markdown = """
# Test User
test@example.com

## Experience
### Developer
- Did some coding
"""
        
        result, warnings = parser.parse_with_warnings(sample_markdown)
        
        assert isinstance(result, ResumeData)
        assert isinstance(warnings, list)
        assert len(warnings) > 0

    def test_parse_invalid_input(self):
        """Test parsing with invalid input."""
        parser = MarkdownResumeParser()
        
        # Test empty input
        with pytest.raises(InvalidMarkdownError):
            parser.parse("")
        
        # Test input without email
        with pytest.raises(InvalidMarkdownError):
            parser.parse("# Name\nNo email here")

    def test_parse_without_validation(self):
        """Test parsing without input validation."""
        parser = MarkdownResumeParser(validate_input=False)
        minimal_markdown = """
# Test
test@example.com
"""
        
        result = parser.parse(minimal_markdown)
        assert result.contact.name == "Test"

    def test_contact_extraction_complex(self):
        """Test complex contact information extraction."""
        parser = MarkdownResumeParser(validate_input=False)
        contact_markdown = """
# Jane Doe, Ph.D.
jane.doe@company.com | +1-555-987-6543
https://linkedin.com/in/jane | https://github.com/jane
https://janedoe.com

## Summary
Professional summary here.
"""
        
        result = parser.parse(contact_markdown)
        
        assert result.contact.name == "Jane Doe, Ph.D."
        assert result.contact.email == "jane.doe@company.com"
        assert result.contact.phone == "+1-555-987-6543"
        assert "linkedin.com/in/jane" in str(result.contact.linkedin)
        assert "github.com/jane" in str(result.contact.github)
        assert "janedoe.com" in str(result.contact.website)

    def test_experience_parsing(self):
        """Test experience section parsing."""
        parser = MarkdownResumeParser(validate_input=False)
        experience_markdown = """
# Test User
test@example.com

## Experience

### Senior Developer at TechCorp
- Led development team
- Improved system performance
- Mentored junior developers

### Developer - StartupCo
- Built web applications
- Worked with React and Node.js
"""
        
        result = parser.parse(experience_markdown, validate_result=False)
        
        assert len(result.experience) >= 1
        # Should parse at least one experience entry

    def test_education_parsing(self):
        """Test education section parsing."""
        parser = MarkdownResumeParser(validate_input=False)
        education_markdown = """
# Test User
test@example.com

## Education

### Master of Science in Computer Science
Stanford University
2020-2022

### Bachelor of Science
MIT
2016-2020
"""
        
        result = parser.parse(education_markdown, validate_result=False)
        
        assert len(result.education) >= 1
        # Should parse at least one education entry

    def test_skills_parsing(self):
        """Test skills section parsing."""
        parser = MarkdownResumeParser(validate_input=False)
        skills_markdown = """
# Test User
test@example.com

## Skills

### Programming Languages:
Python, Java, JavaScript

### Tools:
Git, Docker, AWS
"""
        
        result = parser.parse(skills_markdown, validate_result=False)
        
        assert result.skills is not None
        # Should parse skills section

    def test_summary_parsing(self):
        """Test summary section parsing."""
        parser = MarkdownResumeParser(validate_input=False)
        summary_markdown = """
# Test User
test@example.com

## Summary
Experienced software engineer with strong technical skills.

## Experience
### Developer
Company
- Built applications
"""
        
        result = parser.parse(summary_markdown, validate_result=False)
        
        assert result.summary is not None
        assert "Experienced software engineer" in result.summary
    
    def test_fallback_parsing_methods(self):
        """Test parser fallback methods for content extraction."""
        parser = MarkdownResumeParser(validate_input=False)
        
        # Test experience content in main section (no subsections)
        flat_experience = """
# Test User
test@example.com

## Experience
Software Engineer at TechCorp
- Built applications
- Led team of developers
Developer - StartupCo
- Created web apps
"""
        result = parser.parse(flat_experience, validate_result=False)
        # The fallback method should handle content in the main experience section
        
        # Test education content in main section
        flat_education = """
# Test User  
test@example.com

## Education
Master of Science in Computer Science
Stanford University
Bachelor of Science
MIT
"""
        result = parser.parse(flat_education, validate_result=False)
        # The fallback method should handle content in the main education section
        
        # Test skills with inline categories (each on separate lines)
        inline_skills = """
# Test User
test@example.com

## Skills

Programming Languages: Python, Java, JavaScript

Frameworks: React, Django

Tools: Git, Docker
"""
        result = parser.parse(inline_skills, validate_result=False)
        assert result.skills is not None
        # Skills should be parsed (whether as categories or raw skills)
        assert result.skills.categories is not None or result.skills.raw_skills is not None