"""
Comprehensive tests for the validation module.
"""

import pytest
from src.validation import ResumeValidator
from src.models import ResumeData, ContactInfo, Experience, Education, Skills, SkillCategory
from src.types import ValidationResult


class TestResumeValidator:
    """Test cases for ResumeValidator class."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = ResumeValidator()
        assert validator.strict_mode is False
        assert validator.min_experience_count == 0
        assert validator.min_education_count == 0
        
        strict_validator = ResumeValidator(strict_mode=True)
        assert strict_validator.strict_mode is True
        assert strict_validator.min_experience_count == 1
        assert strict_validator.min_education_count == 1

    def test_validate_valid_resume(self):
        """Test validation of a valid resume."""
        validator = ResumeValidator()
        
        contact = ContactInfo(
            name="John Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567"
        )
        
        experience = [Experience(
            title="Software Engineer",
            company="TechCorp",
            start_date="January 2020",
            end_date="Present",
            bullets=["Built scalable applications", "Led team of 3 developers"]
        )]
        
        education = [Education(
            degree="Bachelor of Science in Computer Science",
            school="University of Technology",
            end_date="2020"
        )]
        
        resume = ResumeData(
            contact=contact,
            experience=experience,
            education=education
        )
        
        result = validator.validate_resume(resume)
        
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_contact_info_errors(self):
        """Test contact info validation errors."""
        validator = ResumeValidator()
        
        # Test short name (1 character passes Pydantic but fails our validation)
        contact = ContactInfo(name="A", email="test@example.com")
        resume = ResumeData(contact=contact)
        
        result = validator.validate_resume(resume)
        assert not result.valid
        assert any("Name must be at least 2 characters" in error for error in result.errors)

    def test_validate_contact_info_warnings(self):
        """Test contact info validation warnings."""
        validator = ResumeValidator()
        
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="123456789012345",  # 15 digits - valid length but unusual format
            linkedin="https://badlink.com/profile",  # Wrong LinkedIn URL
            github="https://wrongsite.com/user"  # Wrong GitHub URL
        )
        
        resume = ResumeData(contact=contact)
        result = validator.validate_resume(resume)
        
        assert len(result.warnings) > 0
        warning_text = " ".join(result.warnings)
        # Check for URL warnings that should be present
        assert "linkedin url should start with" in warning_text.lower()
        assert "github url should start with" in warning_text.lower()
        assert "linkedin" in warning_text.lower()
        assert "github" in warning_text.lower()

    def test_validate_experience_strict_mode(self):
        """Test experience validation in strict mode."""
        validator = ResumeValidator(strict_mode=True)
        
        contact = ContactInfo(name="John Doe", email="john@example.com")
        resume = ResumeData(contact=contact, experience=[])
        
        result = validator.validate_resume(resume)
        
        assert not result.valid
        assert any("experience entry is required" in error.lower() for error in result.errors)

    def test_validate_experience_content(self):
        """Test experience content validation."""
        validator = ResumeValidator()
        
        contact = ContactInfo(name="John Doe", email="john@example.com")
        
        # Test invalid experience entries (single char to pass Pydantic but fail our validation)
        bad_experience = [Experience(
            title="A",  # Too short title
            company="B",  # Too short company
            start_date="2020",
            end_date="2021",
            bullets=["a"]  # Very short bullet
        )]
        
        resume = ResumeData(contact=contact, experience=bad_experience)
        result = validator.validate_resume(resume)
        
        assert not result.valid
        error_text = " ".join(result.errors)
        assert "job title" in error_text.lower()
        assert "company name" in error_text.lower()

    def test_validate_education_strict_mode(self):
        """Test education validation in strict mode."""
        validator = ResumeValidator(strict_mode=True)
        
        contact = ContactInfo(name="John Doe", email="john@example.com")
        resume = ResumeData(contact=contact, education=[])
        
        result = validator.validate_resume(resume)
        
        assert not result.valid
        assert any("education entry is required" in error.lower() for error in result.errors)

    def test_validate_education_content(self):
        """Test education content validation."""
        validator = ResumeValidator()
        
        contact = ContactInfo(name="John Doe", email="john@example.com")
        
        # Test invalid education entries (single char to pass Pydantic but fail our validation)
        bad_education = [Education(
            degree="A",  # Too short degree
            school="X",  # Too short school name
        )]
        
        resume = ResumeData(contact=contact, education=bad_education)
        result = validator.validate_resume(resume)
        
        assert not result.valid
        error_text = " ".join(result.errors)
        assert "degree name" in error_text.lower()
        assert "school name" in error_text.lower()

    def test_validate_structure_warnings(self):
        """Test overall structure validation warnings."""
        validator = ResumeValidator()
        
        # Minimal resume with only contact info
        contact = ContactInfo(name="John Doe", email="john@example.com")
        resume = ResumeData(contact=contact)
        
        result = validator.validate_resume(resume)
        
        assert result.valid  # No errors, just warnings
        assert len(result.warnings) > 0
        warning_text = " ".join(result.warnings)
        assert "3 main sections" in warning_text
        assert "summary" in warning_text.lower()
        assert "skills" in warning_text.lower()

    def test_validate_bullets_quality(self):
        """Test bullet point quality validation."""
        validator = ResumeValidator(strict_mode=True)
        
        contact = ContactInfo(name="John Doe", email="john@example.com")
        
        # Experience with poor quality bullets
        experience = [Experience(
            title="Developer",
            company="Company",
            start_date="2020",
            end_date="2021",
            bullets=[
                "x",  # Too short
                "Responsible for many things and other duties as assigned and various tasks that were needed" * 4  # Too long
            ]
        )]
        
        resume = ResumeData(contact=contact, experience=experience)
        result = validator.validate_resume(resume)
        
        warning_text = " ".join(result.warnings)
        assert "very short" in warning_text
        assert "very long" in warning_text

    def test_validate_date_formats(self):
        """Test date format validation."""
        validator = ResumeValidator()
        
        # Test various date formats
        valid_dates = [
            ("2020", "2021"),
            ("January 2020", "Present"),
            ("Jan 2020", "Dec 2021"),
            ("1/2020", "12/2021"),
            ("2020-01", "2021-12")
        ]
        
        for start, end in valid_dates:
            errors = validator._validate_date_range(start, end)
            # Should not have format errors for valid dates
            format_errors = [e for e in errors if "format" in e.lower()]
            assert len(format_errors) == 0

    def test_validate_invalid_date_formats(self):
        """Test invalid date format validation."""
        validator = ResumeValidator()
        
        invalid_dates = [
            ("tomorrow", "yesterday"),
            ("2020-13-45", "2021-02-30"),
            ("20", "21")
        ]
        
        for start, end in invalid_dates:
            errors = validator._validate_date_range(start, end)
            assert len(errors) > 0

    def test_validate_missing_dates(self):
        """Test validation with missing dates."""
        validator = ResumeValidator()
        
        errors = validator._validate_date_range(None, "2021")
        assert any("start date is missing" in error.lower() for error in errors)
        
        errors = validator._validate_date_range("2020", None)
        assert any("end date is missing" in error.lower() for error in errors)

    def test_phone_format_validation(self):
        """Test phone number format validation."""
        validator = ResumeValidator()
        
        valid_phones = [
            "(555) 123-4567",
            "+1-555-123-4567", 
            "555.123.4567",
            "15551234567",
            "+44 20 7946 0958"
        ]
        
        invalid_phones = [
            "123",
            "not-a-phone",
            "12345678901234578"  # Too long
        ]
        
        for phone in valid_phones:
            assert validator._validate_phone_format(phone)
            
        for phone in invalid_phones:
            assert not validator._validate_phone_format(phone)

    def test_validate_markdown_structure(self):
        """Test markdown structure validation."""
        validator = ResumeValidator()
        
        # Valid markdown
        valid_markdown = """
# John Doe
john@example.com

## Experience
### Developer
- Built things

## Education  
### Degree
School
"""
        
        result = validator.validate_markdown_structure(valid_markdown)
        assert result.valid

    def test_validate_invalid_markdown_structure(self):
        """Test invalid markdown structure validation."""
        validator = ResumeValidator()
        
        # Empty content
        result = validator.validate_markdown_structure("")
        assert not result.valid
        assert any("empty" in error.lower() for error in result.errors)
        
        # No email
        no_email_markdown = """
# John Doe

## Experience
### Developer
"""
        
        result = validator.validate_markdown_structure(no_email_markdown)
        assert not result.valid
        assert any("email" in error.lower() for error in result.errors)

    def test_validate_markdown_warnings(self):
        """Test markdown structure warnings."""
        validator = ResumeValidator()
        
        # Minimal content
        minimal_markdown = """
# John
john@example.com
"""
        
        result = validator.validate_markdown_structure(minimal_markdown)
        assert result.valid  # Valid but with warnings
        assert len(result.warnings) > 0
        
        warning_text = " ".join(result.warnings)
        assert "sections" in warning_text.lower()

    def test_action_words_validation_strict_mode(self):
        """Test action words validation in strict mode."""
        validator = ResumeValidator(strict_mode=True)
        
        contact = ContactInfo(name="John Doe", email="john@example.com")
        
        # Experience with weak bullets (no action words)
        experience = [Experience(
            title="Developer",
            company="Company", 
            start_date="2020",
            end_date="2021",
            bullets=[
                "Was responsible for coding",  # Passive language
                "Participated in meetings"     # Weak action
            ]
        )]
        
        resume = ResumeData(contact=contact, experience=experience)
        result = validator.validate_resume(resume)
        
        # Should have warnings about weak action verbs
        warning_text = " ".join(result.warnings)
        assert "action verb" in warning_text.lower()

    def test_comprehensive_validation_flow(self):
        """Test complete validation flow with mixed issues."""
        validator = ResumeValidator(strict_mode=True)
        
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="123456789012345",  # 15 digits - valid length but unusual format
        )
        
        # No experience or education (strict mode requirement)
        resume = ResumeData(contact=contact)
        
        result = validator.validate_resume(resume)
        
        # Should have errors (missing required sections)
        assert not result.valid
        assert len(result.errors) >= 2  # Experience and education required
        
        # Should have warnings (phone format, missing sections, etc.)
        assert len(result.warnings) > 0


class TestValidationResult:
    """Test cases for ValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=["Consider adding more content"]
        )
        
        assert result.valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Consider adding more content"

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        result = ValidationResult(
            valid=False,
            errors=["Email is required", "Name is too short"],
            warnings=[]
        )
        
        assert result.valid is False
        assert len(result.errors) == 2
        assert "Email is required" in result.errors
        assert "Name is too short" in result.errors