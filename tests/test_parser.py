"""
Tests for the markdown resume parser module.
"""

import pytest
from src.parser import MarkdownResumeParser, ResumeSection, ATSRenderer


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


class TestMarkdownResumeParser:
    """Test cases for MarkdownResumeParser class."""
    
    def test_parser_initialization(self):
        """Test parser can be initialized."""
        parser = MarkdownResumeParser()
        assert parser is not None
        assert hasattr(parser, 'renderer')
        assert hasattr(parser, 'markdown')
    
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