"""
Tests for ATS Formatter module.

Comprehensive test suite for the ATSFormatter class ensuring proper
ATS compliance formatting functionality.
"""

import pytest
from typing import List

from src.models import (
    ResumeData, ContactInfo, Experience, Education, Skills, 
    SkillCategory, Project, Certification
)
from src.formatter import ATSFormatter, ATSConfig


class TestATSFormatter:
    """Test suite for ATSFormatter class."""
    
    @pytest.fixture
    def sample_contact(self) -> ContactInfo:
        """Create sample contact info for testing."""
        return ContactInfo(
            name="John Doe",
            email="john.doe@email.com",
            phone="(555) 123-4567",
            linkedin="https://linkedin.com/in/johndoe",
            github="https://github.com/johndoe",
            website="https://johndoe.dev",
            location="San Francisco, CA"
        )
    
    @pytest.fixture
    def sample_experience(self) -> List[Experience]:
        """Create sample experience for testing."""
        return [
            Experience(
                title="Senior Software Engineer",
                company="Tech Corp",
                start_date="Jan 2020",
                end_date="Present",
                location="San Francisco, CA",
                bullets=[
                    "Developed high-performance web applications",
                    "Led team of 5 engineers in agile development"
                ]
            ),
            Experience(
                title="Software Engineer",
                company="StartupCo",
                start_date="June 2018",
                end_date="Dec 2019",
                location="New York, NY",
                bullets=[
                    "Built scalable microservices architecture",
                    "Improved system performance by 40%"
                ]
            )
        ]
    
    @pytest.fixture
    def sample_education(self) -> List[Education]:
        """Create sample education for testing."""
        return [
            Education(
                degree="Bachelor of Science in Computer Science",
                school="University of California",
                start_date="2014",
                end_date="2018",
                location="Berkeley, CA",
                gpa="3.8",
                honors=["Magna Cum Laude"],
                coursework=["Data Structures", "Algorithms", "Software Engineering"]
            )
        ]
    
    @pytest.fixture
    def sample_skills(self) -> Skills:
        """Create sample skills for testing."""
        return Skills(
            categories=[
                SkillCategory(
                    name="Programming Languages",
                    skills=["Python", "JavaScript", "Java", "Go"]
                ),
                SkillCategory(
                    name="Frameworks",
                    skills=["React", "Django", "Flask", "Express.js"]
                )
            ],
            raw_skills=None
        )
    
    @pytest.fixture
    def sample_resume(self, sample_contact, sample_experience, sample_education, sample_skills) -> ResumeData:
        """Create complete sample resume for testing."""
        return ResumeData(
            contact=sample_contact,
            summary="Experienced software engineer with 5+ years developing scalable applications",
            experience=sample_experience,
            education=sample_education,
            skills=sample_skills,
            projects=None,
            certifications=None,
            additional_sections=None
        )
    
    def test_formatter_initialization_default_config(self) -> None:
        """Test ATSFormatter initialization with default config."""
        formatter = ATSFormatter()
        
        assert formatter.config is not None
        assert formatter.config.max_line_length == 80
        assert formatter.config.bullet_style == "•"
        assert formatter.config.optimize_keywords is True
        assert formatter.config.remove_special_chars is True
        assert formatter.date_standardizer is not None
        assert formatter.header_standardizer is not None
    
    def test_formatter_initialization_custom_config(self) -> None:
        """Test ATSFormatter initialization with custom config."""
        config = ATSConfig(
            max_line_length=100,
            bullet_style="-",
            optimize_keywords=False,
            remove_special_chars=False
        )
        formatter = ATSFormatter(config)
        
        assert formatter.config.max_line_length == 100
        assert formatter.config.bullet_style == "-"
        assert formatter.config.optimize_keywords is False
        assert formatter.config.remove_special_chars is False
    
    def test_format_resume_basic(self, sample_resume) -> None:
        """Test basic resume formatting functionality."""
        formatter = ATSFormatter()
        formatted_resume = formatter.format_resume(sample_resume)
        
        # Should return ResumeData object
        assert isinstance(formatted_resume, ResumeData)
        
        # Should preserve all sections
        assert formatted_resume.contact is not None
        assert formatted_resume.summary is not None
        assert formatted_resume.experience is not None
        assert len(formatted_resume.experience) == 2
        assert formatted_resume.education is not None
        assert len(formatted_resume.education) == 1
        assert formatted_resume.skills is not None
    
    def test_format_resume_invalid_input(self) -> None:
        """Test formatter with invalid input."""
        formatter = ATSFormatter()
        
        with pytest.raises(ValueError, match="Resume data cannot be None"):
            formatter.format_resume(None)
    
    def test_contact_formatting(self, sample_contact) -> None:
        """Test contact information formatting."""
        formatter = ATSFormatter()
        formatted_contact = formatter._format_contact(sample_contact)
        
        assert formatted_contact.name == "John Doe"
        assert formatted_contact.email == "john.doe@email.com"
        assert formatted_contact.phone == "(555) 123-4567"
        assert formatted_contact.location == "San Francisco, CA"
    
    def test_contact_special_chars_removal(self) -> None:
        """Test contact formatting with special character removal."""
        contact = ContactInfo(
            name='John "Smart" Doe',
            email="john.doe@email.com",
            phone="(555) 123-4567",
            linkedin=None,
            github=None,
            website=None,
            location="San Francisco, CA"
        )
        
        formatter = ATSFormatter()
        formatted_contact = formatter._format_contact(contact)
        
        # Should remove smart quotes
        assert formatted_contact.name == 'John Smart Doe'
    
    def test_experience_date_standardization(self) -> None:
        """Test experience date standardization."""
        experience = Experience(
            title="Software Engineer",
            company="Tech Corp",
            start_date="Jan 2020",
            end_date="Dec 2021",
            location="San Francisco, CA",
            bullets=["Built applications"]
        )
        
        formatter = ATSFormatter()
        formatted_exp = formatter._format_experience(experience)
        
        # Dates should be standardized
        assert formatted_exp.start_date == "January 2020"
        assert formatted_exp.end_date == "December 2021"
    
    def test_bullet_point_optimization(self) -> None:
        """Test bullet point optimization."""
        bullets = [
            "developed web applications using python",
            "  led team of engineers  ",
            "improved performance by 40%",
            ""  # Empty bullet should be removed
        ]
        
        formatter = ATSFormatter()
        optimized_bullets = formatter.optimize_bullet_points(bullets)
        
        # Should have proper capitalization and no empty bullets
        assert len(optimized_bullets) == 3
        assert optimized_bullets[0] == "Developed web applications using python"
        assert optimized_bullets[1] == "Led team of engineers"
        assert optimized_bullets[2] == "Improved performance by 40"
    
    def test_text_wrapping(self) -> None:
        """Test text wrapping functionality."""
        formatter = ATSFormatter()
        long_text = "This is a very long line of text that should be wrapped to respect the maximum line length configuration setting"
        
        wrapped_text = formatter._wrap_text(long_text)
        lines = wrapped_text.split('\n')
        
        # All lines should be within max length
        for line in lines:
            assert len(line) <= formatter.config.max_line_length
    
    def test_special_chars_cleaning(self) -> None:
        """Test special character cleaning."""
        formatter = ATSFormatter()
        text_with_specials = 'Text with "smart quotes" and — em dashes and … ellipsis'
        
        cleaned_text = formatter._clean_special_chars(text_with_specials)
        
        # Should replace special chars with ATS-friendly alternatives
        assert 'smart quotes' in cleaned_text  # quotes removed/replaced
        assert " - " in cleaned_text  # em dash replaced
        assert "..." in cleaned_text  # ellipsis replaced
    
    def test_header_standardization(self) -> None:
        """Test section header standardization."""
        formatter = ATSFormatter()
        headers = {
            "work_experience": "Work Experience",
            "technical_skills": "Technical Skills",
            "education": "Education"
        }
        
        standardized = formatter.standardize_section_headers(headers)
        
        assert standardized["work_experience"] == "Experience"
        assert standardized["technical_skills"] == "Skills"
        assert standardized["education"] == "Education"
    
    def test_ats_compliance_validation(self, sample_resume) -> None:
        """Test ATS compliance validation."""
        formatter = ATSFormatter()
        
        # Valid resume should pass validation
        assert formatter.validate_ats_compliance(sample_resume) is True
        
        # Test with valid contact but missing email (ATS compliance should fail)
        incomplete_contact = ContactInfo(
            name="John Doe",
            email="test@example.com",  # Valid email but we'll modify the validation logic
            phone=None,
            linkedin=None,
            github=None,
            website=None,
            location=None
        )
        # Manually set email to None to test ATS validation logic
        incomplete_contact.email = None  # type: ignore
        
        incomplete_resume = ResumeData(
            contact=incomplete_contact,
            summary=None,
            experience=[],
            education=[],
            skills=None,
            projects=None,
            certifications=None,
            additional_sections=None
        )
        assert formatter.validate_ats_compliance(incomplete_resume) is False
    
    def test_format_with_projects(self) -> None:
        """Test formatting with projects section."""
        project = Project(
            name="Web Application",
            description="Full-stack web application",
            technologies=["Python", "React", "PostgreSQL"],
            date="2023",
            bullets=["Built responsive frontend", "Implemented REST API"]
        )
        
        formatter = ATSFormatter()
        formatted_project = formatter._format_project(project)
        
        assert formatted_project.name == "Web Application"
        assert formatted_project.date == "2023"
        assert len(formatted_project.bullets) == 2
    
    def test_format_with_certifications(self) -> None:
        """Test formatting with certifications section."""
        cert = Certification(
            name="AWS Solutions Architect",
            issuer="Amazon Web Services",
            date="Jan 2023",
            expiry="Jan 2026"
        )
        
        formatter = ATSFormatter()
        formatted_cert = formatter._format_certification(cert)
        
        assert formatted_cert.name == "AWS Solutions Architect"
        assert formatted_cert.issuer == "Amazon Web Services"
        assert formatted_cert.date == "January 2023"
        assert formatted_cert.expiry == "January 2026"
    
    def test_skills_formatting(self, sample_skills) -> None:
        """Test skills section formatting."""
        formatter = ATSFormatter()
        formatted_skills = formatter._format_skills(sample_skills)
        
        assert formatted_skills.categories is not None
        assert len(formatted_skills.categories) == 2
        assert formatted_skills.categories[0].name == "Programming Languages"
        assert "Python" in formatted_skills.categories[0].skills
    
    def test_summary_formatting(self) -> None:
        """Test summary formatting."""
        formatter = ATSFormatter()
        summary = "Experienced software engineer with expertise in web development and system architecture"
        
        formatted_summary = formatter._format_summary(summary)
        
        assert isinstance(formatted_summary, str)
        assert len(formatted_summary) > 0
    
    def test_education_formatting(self, sample_education) -> None:
        """Test education formatting."""
        formatter = ATSFormatter()
        formatted_education = formatter._format_education(sample_education[0])
        
        assert formatted_education.degree == "Bachelor of Science in Computer Science"
        assert formatted_education.school == "University of California"
        assert formatted_education.start_date == "2014"
        assert formatted_education.end_date == "2018"
    
    def test_format_resume_with_none_input(self) -> None:
        """Test formatter handles None input gracefully."""
        formatter = ATSFormatter()
        
        with pytest.raises(ValueError, match="Resume data cannot be None"):
            formatter.format_resume(None)
    
    def test_format_section_content_empty(self) -> None:
        """Test formatting empty section content."""
        formatter = ATSFormatter()
        
        result = formatter.format_section_content("")
        assert result == ""
        
        result = formatter.format_section_content(None)
        assert result is None
    
    def test_clean_special_chars_empty(self) -> None:
        """Test cleaning empty or None text."""
        formatter = ATSFormatter()
        
        assert formatter._clean_special_chars("") == ""
        assert formatter._clean_special_chars(None) is None
    
    def test_wrap_text_short_text(self) -> None:
        """Test text wrapping with short text."""
        formatter = ATSFormatter()
        short_text = "Short text"
        
        result = formatter._wrap_text(short_text)
        assert result == short_text
    
    def test_config_section_order_default(self) -> None:
        """Test that default section order is set correctly."""
        config = ATSConfig()
        
        expected_order = [
            "contact", "summary", "experience", "education", 
            "skills", "projects", "certifications"
        ]
        assert config.section_order == expected_order
    
    def test_optimize_bullet_points_empty(self) -> None:
        """Test bullet point optimization with empty input."""
        formatter = ATSFormatter()
        
        result = formatter.optimize_bullet_points([])
        assert result == []
        
        result = formatter.optimize_bullet_points(None)
        assert result is None