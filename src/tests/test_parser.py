"""
Comprehensive tests for the parser module.
"""

import pytest
from src.parser import MarkdownResumeParser, ATSRenderer, ResumeSection
from src.models import ResumeData, ContactInfo, Experience, Education, Skills
from src.custom_types import InvalidMarkdownError


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

    def test_heading_processing(self):
        """Test heading processing."""
        renderer = ATSRenderer()
        
        result = renderer.heading('Experience', 2)
        
        assert 'Experience' in result
        assert renderer.current_section == 'experience'
        assert renderer.current_level == 2
        assert renderer.current_section_content == []

    def test_paragraph_processing(self):
        """Test paragraph processing.""" 
        renderer = ATSRenderer()
        renderer.current_section = 'summary'
        
        result = renderer.paragraph('Software engineer with 5 years experience')
        
        assert 'Software engineer with 5 years experience' in result
        assert 'Software engineer with 5 years experience' in renderer.current_section_content

    def test_list_item_processing(self):
        """Test list item processing."""
        renderer = ATSRenderer()
        renderer.current_section = 'experience'
        
        result = renderer.list_item('Built scalable applications')
        
        assert 'Built scalable applications' in result
        assert 'Built scalable applications' in renderer.current_section_content

    def test_link_processing(self):
        """Test link processing."""
        renderer = ATSRenderer()
        renderer.current_section = 'contact'
        
        result = renderer.link('https://linkedin.com/in/user', 'LinkedIn')
        
        assert 'LinkedIn' in result
        assert 'LinkedIn: https://linkedin.com/in/user' in renderer.current_section_content

    def test_finalize_sections(self):
        """Test section finalization."""
        renderer = ATSRenderer()
        
        # Add some content
        renderer.current_section = 'experience'
        renderer.current_level = 2
        renderer.current_section_content = ['Senior Engineer', 'Led team of 5']
        
        sections = renderer.finalize_sections()
        
        assert 'experience' in sections
        assert sections['experience'].title == 'experience'
        assert sections['experience'].level == 2
        assert sections['experience'].content == ['Senior Engineer', 'Led team of 5']

    def test_multiple_sections(self):
        """Test processing multiple sections."""
        renderer = ATSRenderer()
        
        # First section
        renderer.heading('Experience', 2)
        renderer.paragraph('Software Engineer')
        
        # Second section  
        renderer.heading('Education', 2)
        renderer.paragraph('Computer Science Degree')
        
        sections = renderer.finalize_sections()
        
        assert len(sections) == 2
        assert 'experience' in sections
        assert 'education' in sections
        assert sections['experience'].content == ['Software Engineer']
        assert sections['education'].content == ['Computer Science Degree']


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

## Education

### Bachelor of Science in Computer Science
University of Technology
"""
        result = parser.parse(sample_markdown)
        
        # Check that we get a ResumeData object
        assert isinstance(result, ResumeData)
        assert hasattr(result, 'contact')
        assert hasattr(result, 'experience')
        assert hasattr(result, 'education')
        
        # Check basic contact info parsing
        assert result.contact.name == "John Smith"
        assert result.contact.email == "john.smith@email.com"
        assert result.contact.phone == "(555) 123-4567"

    def test_parse_complex_resume(self):
        """Test parsing a more complex resume with all sections."""
        parser = MarkdownResumeParser()
        complex_markdown = """
# Jane Doe
jane.doe@example.com | +1-555-123-4567
https://linkedin.com/in/janedoe | https://github.com/janedoe

## Summary

Experienced software engineer with expertise in full-stack development.

## Experience

### Senior Software Engineer at TechCorp
January 2020 - Present
- Led development of microservices architecture
- Mentored junior developers
- Improved system performance by 40%

### Software Engineer at StartupXYZ
June 2018 - December 2019
- Built React applications
- Implemented CI/CD pipelines

## Education

### Master of Science in Computer Science
Stanford University
2016-2018
GPA: 3.8

### Bachelor of Science in Computer Science  
MIT
2012-2016

## Skills

### Programming Languages:
Python, JavaScript, Java, Go

### Frameworks:
React, Django, Spring Boot

### Tools:
Docker, Kubernetes, AWS
"""
        result = parser.parse(complex_markdown)
        
        # Validate contact info
        assert result.contact.name == "Jane Doe"
        assert result.contact.email == "jane.doe@example.com"
        assert result.contact.phone == "+1-555-123-4567"
        assert "linkedin.com/in/janedoe" in str(result.contact.linkedin)
        assert "github.com/janedoe" in str(result.contact.github)
        
        # Validate summary
        assert result.summary is not None
        assert "Experienced software engineer" in result.summary
        
        # Validate experience
        assert len(result.experience) >= 1
        
        # Validate education  
        assert len(result.education) >= 1
        
        # Validate skills
        assert result.skills is not None

    def test_parse_with_warnings(self):
        """Test parsing with warnings enabled."""
        parser = MarkdownResumeParser()
        simple_markdown = """
# Test User
test@example.com

## Experience
### Developer
- Did some coding
"""
        
        result, warnings = parser.parse_with_warnings(simple_markdown)
        
        assert isinstance(result, ResumeData)
        assert isinstance(warnings, list)
        assert len(warnings) > 0
        assert any("education" in warning.lower() for warning in warnings)

    def test_parse_invalid_markdown_no_email(self):
        """Test parsing markdown without required email."""
        parser = MarkdownResumeParser()
        invalid_markdown = """
# John Smith

## Experience
### Developer
- Coded things
"""
        
        with pytest.raises(InvalidMarkdownError) as exc_info:
            parser.parse(invalid_markdown)
        
        assert "Email address not found" in str(exc_info.value) or "Email address is required" in str(exc_info.value)

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = MarkdownResumeParser()
        
        with pytest.raises(InvalidMarkdownError) as exc_info:
            parser.parse("")
        
        assert "empty" in str(exc_info.value).lower()

    def test_parse_without_validation(self):
        """Test parsing without input validation."""
        parser = MarkdownResumeParser(validate_input=False)
        minimal_markdown = """
# Test
test@example.com
"""
        
        # Should parse without validation errors
        result = parser.parse(minimal_markdown)
        assert result.contact.name == "Test"

    def test_contact_info_extraction(self):
        """Test contact information extraction."""
        parser = MarkdownResumeParser(validate_input=False)
        contact_markdown = """
# Dr. Alice Johnson
alice.johnson@company.com | (555) 987-6543
https://www.linkedin.com/in/alice | https://github.com/alice
https://alicejohnson.dev
"""
        
        result = parser.parse(contact_markdown)
        
        assert result.contact.name == "Dr. Alice Johnson"
        assert result.contact.email == "alice.johnson@company.com"
        assert result.contact.phone == "(555) 987-6543"
        assert "linkedin.com/in/alice" in str(result.contact.linkedin)
        assert "github.com/alice" in str(result.contact.github)
        assert "alicejohnson.dev" in str(result.contact.website)

    def test_experience_extraction_various_formats(self):
        """Test experience extraction with various formats."""
        parser = MarkdownResumeParser(validate_input=False)
        experience_markdown = """
# Test User
test@example.com

## Experience

### Software Engineer at Google
- Built search algorithms
- Improved performance

### Data Scientist - Facebook
- Analyzed user behavior
- Created ML models

### Consultant
Microsoft
- Provided technical guidance
"""
        
        result = parser.parse(experience_markdown)
        
        assert len(result.experience) >= 1
        # Check that different format styles are parsed

    def test_education_extraction(self):
        """Test education section extraction."""
        parser = MarkdownResumeParser(validate_input=False)
        education_markdown = """
# Test User
test@example.com

## Education

### Ph.D. in Computer Science
Stanford University
2018-2022

### Master of Science in Data Science
UC Berkeley
2016-2018
GPA: 3.9

### Bachelor of Engineering
MIT
"""
        
        result = parser.parse(education_markdown)
        
        assert len(result.education) >= 1

    def test_skills_extraction_categorized(self):
        """Test skills extraction with categories."""
        parser = MarkdownResumeParser(validate_input=False)
        skills_markdown = """
# Test User
test@example.com

## Skills

### Programming Languages:
Python, Java, JavaScript, C++

### Frameworks:
React, Django, Spring

### Tools:
Git, Docker, AWS
"""
        
        result = parser.parse(skills_markdown)
        
        assert result.skills is not None
        assert result.skills.categories is not None
        assert len(result.skills.categories) >= 1

    def test_skills_extraction_flat_list(self):
        """Test skills extraction as flat list."""
        parser = MarkdownResumeParser(validate_input=False)
        skills_markdown = """
# Test User
test@example.com

## Skills

- Python programming
- Web development
- Database design
- Project management
"""
        
        result = parser.parse(skills_markdown)
        
        assert result.skills is not None
        assert result.skills.raw_skills is not None or result.skills.categories is not None

    def test_parser_error_handling(self):
        """Test parser error handling for malformed input."""
        parser = MarkdownResumeParser()
        
        # Test with malformed markdown that should cause parsing errors
        malformed_content = "# \n\n@invalid-email\n"
        
        with pytest.raises(InvalidMarkdownError):
            parser.parse(malformed_content)

    def test_strict_validation_mode(self):
        """Test parser in strict validation mode."""
        parser = MarkdownResumeParser(strict_validation=True)
        
        minimal_resume = """
# Test User
test@example.com

## Experience
### Intern
Company
- Did some work
"""
        
        # In strict mode, this should fail validation due to missing required sections
        with pytest.raises(InvalidMarkdownError) as exc_info:
            parser.parse_with_warnings(minimal_resume)
        
        # Should mention education requirement
        assert "education" in str(exc_info.value).lower()


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
        assert section.metadata["company"] == "TechCorp"