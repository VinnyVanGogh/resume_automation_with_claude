"""
Tests for the ATS formatter module.
"""

import pytest
from src.formatter import ATSFormatter
from src.parser import ResumeSection


class TestATSFormatter:
    """Test cases for ATSFormatter class."""
    
    def test_formatter_initialization(self):
        """Test ATSFormatter can be initialized."""
        formatter = ATSFormatter()
        assert formatter is not None
    
    def test_ats_rules_defined(self):
        """Test that ATS rules are properly defined."""
        assert "headers" in ATSFormatter.ATS_RULES
        assert "date_format" in ATSFormatter.ATS_RULES
        assert "bullet_prefix" in ATSFormatter.ATS_RULES
        assert "max_line_length" in ATSFormatter.ATS_RULES
        
        # Check rule values
        assert isinstance(ATSFormatter.ATS_RULES["headers"], list)
        assert "Experience" in ATSFormatter.ATS_RULES["headers"]
        assert "Education" in ATSFormatter.ATS_RULES["headers"]
        assert "Skills" in ATSFormatter.ATS_RULES["headers"]
    
    @pytest.mark.skip(reason="Implementation pending")
    def test_format_section(self):
        """Test formatting a single section."""
        formatter = ATSFormatter()
        section = ResumeSection(
            title="Work Experience",
            content=["Software Engineer at TechCorp"],
            level=2
        )
        
        formatted = formatter.format_section(section)
        # TODO: Add assertions once format_section is implemented
        assert formatted is not None
    
    @pytest.mark.skip(reason="Implementation pending")
    def test_format_all_sections(self):
        """Test formatting multiple sections."""
        formatter = ATSFormatter()
        sections = {
            "experience": ResumeSection(
                title="Work Experience",
                content=["Software Engineer"],
                level=2
            ),
            "education": ResumeSection(
                title="Education",
                content=["B.S. Computer Science"],
                level=2
            )
        }
        
        formatted = formatter.format_all(sections)
        # TODO: Add assertions once format_all is implemented
        assert formatted is not None
        assert len(formatted) == 2