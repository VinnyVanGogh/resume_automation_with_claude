"""
Tests for Header Standardizer module.

Comprehensive test suite for the HeaderStandardizer class ensuring proper
section header standardization for ATS compliance.
"""

import pytest
from typing import List

from src.formatter import HeaderStandardizer


class TestHeaderStandardizer:
    """Test suite for HeaderStandardizer class."""
    
    @pytest.fixture
    def header_standardizer(self) -> HeaderStandardizer:
        """Create HeaderStandardizer instance for testing."""
        return HeaderStandardizer()
    
    def test_standardize_experience_headers(self, header_standardizer) -> None:
        """Test standardization of experience section headers."""
        test_cases = [
            ("Work Experience", "Experience"),
            ("Professional Experience", "Experience"),
            ("Employment", "Experience"),
            ("Employment History", "Experience"),
            ("Work History", "Experience"),
            ("Career History", "Experience"),
            ("Professional Background", "Experience"),
            ("Positions Held", "Experience"),
            ("Relevant Experience", "Experience"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_summary_headers(self, header_standardizer) -> None:
        """Test standardization of summary section headers."""
        test_cases = [
            ("Professional Summary", "Summary"),
            ("Executive Summary", "Summary"),
            ("Profile", "Summary"),
            ("Professional Profile", "Summary"),
            ("Career Summary", "Summary"),
            ("Overview", "Summary"),
            ("Objective", "Summary"),
            ("Career Objective", "Summary"),
            ("Professional Objective", "Summary"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_education_headers(self, header_standardizer) -> None:
        """Test standardization of education section headers."""
        test_cases = [
            ("Academic Background", "Education"),
            ("Academic History", "Education"),
            ("Educational Background", "Education"),
            ("Academic Qualifications", "Education"),
            ("Qualifications", "Education"),
            ("Academic Credentials", "Education"),
            ("Degrees", "Education"),
            ("Education and Training", "Education"),
            ("Formal Education", "Education"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_skills_headers(self, header_standardizer) -> None:
        """Test standardization of skills section headers."""
        test_cases = [
            ("Technical Skills", "Skills"),
            ("Core Competencies", "Skills"),
            ("Competencies", "Skills"),
            ("Areas of Expertise", "Skills"),
            ("Expertise", "Skills"),
            ("Capabilities", "Skills"),
            ("Proficiencies", "Skills"),
            ("Technical Proficiencies", "Skills"),
            ("Key Skills", "Skills"),
            ("Skill Set", "Skills"),
            ("Technologies", "Skills"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_certifications_headers(self, header_standardizer) -> None:
        """Test standardization of certifications section headers."""
        test_cases = [
            ("Certificates", "Certifications"),
            ("Professional Certifications", "Certifications"),
            ("Licenses", "Certifications"),
            ("Licenses and Certifications", "Certifications"),
            ("Credentials", "Certifications"),
            ("Professional Credentials", "Certifications"),
            ("Accreditations", "Certifications"),
            ("Professional Development", "Certifications"),
            ("Training", "Certifications"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_projects_headers(self, header_standardizer) -> None:
        """Test standardization of projects section headers."""
        test_cases = [
            ("Key Projects", "Projects"),
            ("Notable Projects", "Projects"),
            ("Project Experience", "Projects"),
            ("Selected Projects", "Projects"),
            ("Project Portfolio", "Projects"),
            ("Accomplishments", "Projects"),
            ("Key Accomplishments", "Projects"),
            ("Achievements", "Projects"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_contact_headers(self, header_standardizer) -> None:
        """Test standardization of contact section headers."""
        test_cases = [
            ("Contact", "Contact Information"),
            ("Contact Information", "Contact Information"),
            ("Contact Details", "Contact Information"),
            ("Personal Information", "Contact Information"),
            ("Personal Details", "Contact Information"),
            ("Contact Info", "Contact Information"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_already_standard_headers(self, header_standardizer) -> None:
        """Test that already standard headers remain unchanged."""
        standard_headers = [
            "Summary",
            "Experience", 
            "Education",
            "Skills",
            "Certifications",
            "Projects",
            "Contact Information"
        ]
        
        for header in standard_headers:
            result = header_standardizer.standardize_header(header)
            assert result == header
    
    def test_standardize_unknown_headers(self, header_standardizer) -> None:
        """Test standardization of unknown/custom headers."""
        test_cases = [
            ("Custom Section", "Custom Section"),
            ("volunteer work", "Volunteer Work"),  # Should be title cased
            ("AWARDS", "Awards"),  # Should be title cased
            ("publications", "Publications"),  # Should be title cased
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_empty_or_none_headers(self, header_standardizer) -> None:
        """Test standardization with empty or None headers."""
        assert header_standardizer.standardize_header("") == ""
        assert header_standardizer.standardize_header("   ") == ""
        assert header_standardizer.standardize_header(None) is None
    
    def test_standardize_headers_with_punctuation(self, header_standardizer) -> None:
        """Test standardization of headers with punctuation."""
        test_cases = [
            ("Work Experience:", "Experience"),
            ("Technical Skills.", "Skills"),
            ("Education-", "Education"),
            ("...Summary...", "Summary"),
            ("__Projects__", "Projects"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_standardize_headers_case_insensitive(self, header_standardizer) -> None:
        """Test that header standardization is case insensitive."""
        test_cases = [
            ("WORK EXPERIENCE", "Experience"),
            ("work experience", "Experience"),
            ("Work Experience", "Experience"),
            ("WoRk ExPeRiEnCe", "Experience"),
        ]
        
        for input_header, expected in test_cases:
            result = header_standardizer.standardize_header(input_header)
            assert result == expected
    
    def test_is_standard_header(self, header_standardizer) -> None:
        """Test the is_standard_header method."""
        standard_headers = [
            "Summary", "Experience", "Education", "Skills", 
            "Certifications", "Projects", "Contact Information"
        ]
        
        for header in standard_headers:
            assert header_standardizer.is_standard_header(header) is True
        
        non_standard_headers = [
            "Work Experience", "Technical Skills", "Custom Section"
        ]
        
        for header in non_standard_headers:
            assert header_standardizer.is_standard_header(header) is False
    
    def test_get_header_category(self, header_standardizer) -> None:
        """Test the get_header_category method."""
        test_cases = [
            ("Work Experience", "experience"),
            ("Technical Skills", "skills"),
            ("Academic Background", "education"),
            ("Professional Summary", "summary"),
            ("Licenses and Certifications", "certifications"),
            ("Key Projects", "projects"),
            ("Contact Details", "contact"),
            ("Unknown Header", None),
        ]
        
        for input_header, expected_category in test_cases:
            result = header_standardizer.get_header_category(input_header)
            assert result == expected_category
    
    def test_standardize_all_headers(self, header_standardizer) -> None:
        """Test the standardize_all_headers method."""
        input_headers = [
            "Work Experience",
            "Technical Skills", 
            "Academic Background",
            "Professional Summary"
        ]
        
        expected_headers = [
            "Experience",
            "Skills",
            "Education", 
            "Summary"
        ]
        
        result = header_standardizer.standardize_all_headers(input_headers)
        assert result == expected_headers
    
    def test_suggest_header_order(self, header_standardizer) -> None:
        """Test the suggest_header_order method."""
        # Headers in random order
        random_headers = [
            "Skills",
            "Projects", 
            "Summary",
            "Education",
            "Experience",
            "Contact Information",
            "Certifications"
        ]
        
        # Expected ATS-preferred order
        expected_order = [
            "Contact Information",
            "Summary",
            "Experience",
            "Education", 
            "Skills",
            "Projects",
            "Certifications"
        ]
        
        result = header_standardizer.suggest_header_order(random_headers)
        assert result == expected_order
    
    def test_suggest_header_order_with_unknown_headers(self, header_standardizer) -> None:
        """Test header order suggestion with unknown headers."""
        input_headers = [
            "Skills",
            "Custom Section",  # Unknown header
            "Summary",
            "Awards",  # Unknown header
            "Experience"
        ]
        
        result = header_standardizer.suggest_header_order(input_headers)
        
        # Known headers should be in preferred order
        known_headers = [h for h in result if h in ["Summary", "Experience", "Skills"]]
        assert known_headers == ["Summary", "Experience", "Skills"]
        
        # Unknown headers should be at the end
        unknown_headers = [h for h in result if h not in ["Summary", "Experience", "Skills"]]
        assert len(unknown_headers) == 2
        assert "Awards" in unknown_headers
        assert "Custom Section" in unknown_headers
    
    def test_header_cleaning(self, header_standardizer) -> None:
        """Test the internal header cleaning functionality."""
        test_cases = [
            ("  Work   Experience  ", "Work Experience"),
            ("Work\tExperience", "Work Experience"),
            ("Work\nExperience", "Work Experience"),
            ("Work:Experience.", "Work:Experience"),  # Punctuation at end should be removed
        ]
        
        for input_header, expected_cleaned in test_cases:
            result = header_standardizer._clean_header(input_header)
            # The cleaned header should have normalized whitespace
            assert " ".join(result.split()) == " ".join(expected_cleaned.split())