"""
Tests for data models.

Basic tests to improve coverage on model validation and methods.
"""

import pytest
from src.models import ContactInfo, ResumeData, Skills, SkillCategory


class TestModels:
    """Test model functionality."""
    
    def test_contact_info_validation(self) -> None:
        """Test ContactInfo validation."""
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone=None,
            linkedin=None,
            github=None,
            website=None,
            location=None
        )
        assert contact.name == "John Doe"
        assert contact.email == "john@example.com"
    
    def test_contact_info_phone_validation_error(self) -> None:
        """Test ContactInfo phone validation error."""
        with pytest.raises(ValueError, match="Phone number must be between 10-15 digits"):
            ContactInfo(
                name="John Doe",
                email="john@example.com",
                phone="123"  # Too short
            )
    
    def test_skills_has_skills_method(self) -> None:
        """Test Skills.has_skills method."""
        # Skills with categories
        skills_with_categories = Skills(
            categories=[
                SkillCategory(name="Programming", skills=["Python", "Java"])
            ],
            raw_skills=None
        )
        assert skills_with_categories.has_skills() is True
        
        # Skills with raw skills
        skills_with_raw = Skills(
            categories=None,
            raw_skills=["Python", "Java"]
        )
        assert skills_with_raw.has_skills() is True
        
        # Empty skills
        empty_skills = Skills(categories=None, raw_skills=None)
        assert empty_skills.has_skills() is False
        
        # Skills with empty lists
        empty_lists = Skills(categories=[], raw_skills=[])
        assert empty_lists.has_skills() is False
    
    def test_resume_data_get_all_sections(self) -> None:
        """Test ResumeData.get_all_sections method."""
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone=None,
            linkedin=None,
            github=None,
            website=None,
            location=None
        )
        
        resume = ResumeData(
            contact=contact,
            summary="Test summary",
            experience=[],
            education=[],
            skills=Skills(categories=None, raw_skills=["Python"]),
            projects=None,
            certifications=None,
            additional_sections={"awards": ["Best Employee"]}
        )
        
        sections = resume.get_all_sections()
        expected_sections = ["contact", "summary", "skills", "awards"]
        
        for section in expected_sections:
            assert section in sections