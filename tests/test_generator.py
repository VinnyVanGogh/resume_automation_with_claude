"""
Tests for the resume output generator module.
"""
import os
import pytest
from pathlib import Path
from src.resume_generator import ResumeGenerator
from src.generator.config import OutputConfig
from src.models import ResumeData, ContactInfo, Experience, Education, Skills, Project, Certification, SkillCategory
from src.parser import ResumeSection
from pydantic import HttpUrl


class TestResumeGenerator:
    """Test cases for ResumeGenerator class."""
    
    def test_generator_initialization(self):
        """Test ResumeGenerator can be initialized."""
        generator = ResumeGenerator()
        assert generator is not None
        assert isinstance(generator, ResumeGenerator)
    
    def test_generator_with_config(self):
        """Test ResumeGenerator initialization with config path."""
        config = OutputConfig(
            output_dir=Path("test_output"),
            filename_prefix="test_resume",
            overwrite_existing=True,
            validate_output=True
        )
        generator = ResumeGenerator(config=config)
        assert generator is not None
        assert isinstance(generator.config, OutputConfig)
        assert generator.config.output_dir == Path("test_output")
        assert generator.config.filename_prefix == "test_resume"
        assert generator.config.overwrite_existing is True
        assert generator.config.validate_output is True

    def test_generate_html_basic(self):
        """Test basic HTML generation."""
        generator = ResumeGenerator()
        
        # Create sample resume data
        resume_data = ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="john.doe@example.com"
            )
        )
        
        html_content = generator.generate_html(resume_data)
        assert isinstance(html_content, str)
        assert "html" in html_content.lower()
        assert "John Doe" in html_content
    
    def test_generate_pdf(self):
        """Test PDF generation."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="jd@example.com",
                phone="+1234567890",
                location="123 Main St, City, Country",
                website=HttpUrl("https://johndoe.com"),
                linkedin=HttpUrl("https://linkedin.com/in/johndoe"),
                github=HttpUrl("https://github.com/johndoe")
            ),
            summary="Experienced software engineer",
            skills=Skills(
                categories=[
                    SkillCategory(name="Programming Languages", skills=["Python", "Java"]),
                    SkillCategory(name="Frameworks", skills=["Django", "Flask"])
                ],
                raw_skills=["Python", "Java", "Django", "Flask"]
            ),
            projects=[
                Project(
                    name="Project A",
                    description="Description of Project A",
                    technologies=["Python", "Django"],
                    bullets=[],
                    url=None,
                    date=""
                ),
                Project(
                    name="Project B",
                    description="Description of Project B",
                    technologies=["JavaScript", "React"],
                    bullets=[],
                    url=HttpUrl("https://project-b.com"),
                    date=""
                )
            ],
            certifications=[
                Certification(
                    name="Certification A",
                    issuer="Certification Authority",
                    date="2020",
                    expiry=None,
                    credential_id=None
                )
            ],
            additional_sections={
                "Hobbies": ["Reading", "Traveling"]
            }
        )


        output_path = Path("test_resume.pdf")
        generator.generate_pdf(resume_data, output_path)
        assert output_path.exists()
        assert output_path.suffix == ".pdf" 
        
        os.remove(output_path)  # Cleanup after test
    
    def test_generate_docx(self):
        """Test DOCX generation."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="jd@example.com",
                phone="+1234567890",
                location="123 Main St, City, Country",
                website=HttpUrl("https://johndoe.com"),
                linkedin=HttpUrl("https://linkedin.com/in/johndoe"),
                github=HttpUrl("https://github.com/johndoe")
            ),
            summary="Experienced software engineer",
            skills=Skills(
                categories=[
                    SkillCategory(name="Programming Languages", skills=["Python", "Java"]),
                    SkillCategory(name="Frameworks", skills=["Django", "Flask"])
                ],
                raw_skills=["Python", "Java", "Django", "Flask"]
            ),
            projects=[
                Project(
                    name="Project A",
                    description="Description of Project A",
                    technologies=["Python", "Django"],
                    bullets=[],
                    url=None,
                    date=""
                ),
                Project(
                    name="Project B",
                    description="Description of Project B",
                    technologies=["JavaScript", "React"],
                    bullets=[],
                    url=HttpUrl("https://project-b.com"),
                    date=""
                )
            ],
            certifications=[
                Certification(
                    name="Certification A",
                    issuer="Certification Authority",
                    date="2020",
                    expiry=None,
                    credential_id=None
                )
            ],
            additional_sections={
                "Hobbies": ["Reading", "Traveling"]
            }
        )

        output_path = Path("test_resume.docx")
        docx_bytes = generator.generate_docx(resume_data, output_path)
        
        # Check that file was created and contains DOCX data
        assert output_path.exists()
        assert output_path.suffix == ".docx"
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000  # DOCX files should be reasonably sized
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
    
    def test_generate_all_formats(self):
        """Test generating all formats."""
        generator = ResumeGenerator()
        
        # Create sample resume data
        resume_data = ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="jd@example.com",
                phone="+1234567890",
                location="123 Main St, City, Country",
                website=HttpUrl("https://johndoe.com"),
                linkedin=HttpUrl("https://linkedin.com/in/johndoe"),
                github=HttpUrl("https://github.com/johndoe")
            ),
            summary="Experienced software engineer",
            skills=Skills(
                categories=[
                    SkillCategory(name="Programming Languages", skills=["Python", "Java"]),
                    SkillCategory(name="Frameworks", skills=["Django", "Flask"])
                ],
                raw_skills=["Python", "Java", "Django", "Flask"]
            ),
            projects=[
                Project(
                    name="Project A",
                    description="Description of Project A",
                    technologies=["Python", "Django"],
                    bullets=[],
                    url=None,
                    date=""
                ),
                Project(
                    name="Project B",
                    description="Description of Project B",
                    technologies=["JavaScript", "React"],
                    bullets=[],
                    url=HttpUrl("https://project-b.com"),
                    date=""
                )
            ],
            certifications=[
                Certification(
                    name="Certification A",
                    issuer="Certification Authority",
                    date="2020",
                    expiry=None,
                    credential_id=None
                )
            ],
            additional_sections={
                "Hobbies": ["Reading", "Traveling"]
            }
        )
        
        # Use a temporary directory for testing
        output_dir = Path("test_output")
        results = generator.generate_all_formats(resume_data, output_dir)
        
        assert isinstance(results, dict)
        assert "html" in results
        assert "pdf" in results
        assert "docx" in results
        
        # Check that HTML file was created
        html_path = Path(results["html"])
        assert html_path.exists()
        assert html_path.suffix == ".html"
        
        # Cleanup all generated files
        import shutil
        for format_type, file_path in results.items():
            path = Path(file_path)
            if path.exists():
                path.unlink()
        
        # Remove output directory if it exists and is empty
        if output_dir.exists():
            try:
                output_dir.rmdir()
            except OSError:
                # Directory not empty - use shutil to remove recursively
                shutil.rmtree(output_dir)
    
    def test_generate_pdf_with_output_path(self):
        """Test PDF generation with custom output path."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com")
        )
        
        output_path = Path("custom_resume.pdf")
        pdf_bytes = generator.generate_pdf(resume_data, output_path)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert output_path.exists()
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
    
    def test_generate_html_with_template_vars(self):
        """Test HTML generation with custom template variables."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com")
        )
        
        template_vars = {"custom_title": "My Resume", "theme": "modern"}
        html_content = generator.generate_html(resume_data, template_vars=template_vars)
        
        assert isinstance(html_content, str)
        assert "Test User" in html_content
    
    def test_generate_docx_with_template_vars(self):
        """Test DOCX generation with template variables."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com")
        )
        
        output_path = Path("test_custom.docx")
        template_vars = {"custom_format": True}
        docx_bytes = generator.generate_docx(resume_data, output_path, template_vars)
        
        assert isinstance(docx_bytes, bytes)
        assert output_path.exists()
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
    
    def test_generate_all_formats_with_custom_filename(self):
        """Test generating all formats with custom filename prefix."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(name="Jane Doe", email="jane@example.com")
        )
        
        output_dir = Path("custom_output")
        results = generator.generate_all_formats(
            resume_data, 
            output_dir, 
            custom_filename="jane_resume"
        )
        
        assert isinstance(results, dict)
        assert all(format_type in results for format_type in ["html", "pdf", "docx"])
        
        # Check that custom filename was used
        for file_path in results.values():
            assert "jane_resume" in str(file_path)
        
        # Cleanup
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_validate_all_outputs(self):
        """Test output validation functionality."""
        generator = ResumeGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            summary="Test summary"
        )
        
        output_dir = Path("validation_test")
        results = generator.generate_all_formats(resume_data, output_dir)
        
        # Test validation
        validation_result = generator.validate_all_outputs(results)
        assert isinstance(validation_result, bool)
        
        # Cleanup
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_error_handling_invalid_resume_data(self):
        """Test error handling with invalid resume data."""
        generator = ResumeGenerator()
        
        with pytest.raises(Exception):
            generator.generate_html("not a resume data object")
        
        with pytest.raises(Exception):
            generator.generate_pdf(None)
        
        with pytest.raises(Exception):
            generator.generate_docx({"invalid": "data"})
    
    def test_legacy_html_generation(self):
        """Test legacy HTML generation method."""
        generator = ResumeGenerator()
        
        legacy_sections = {"summary": "Test summary"}
        html_content = generator.generate_html_legacy(legacy_sections)
        
        assert isinstance(html_content, str)
        assert "html" in html_content.lower()
        assert "legacy" in html_content.lower()


class TestOutputConfig:
    """Test OutputConfig functionality."""
    
    def test_output_config_get_output_path_invalid_format(self):
        """Test OutputConfig with invalid format."""
        config = OutputConfig()
        
        # Test invalid format
        with pytest.raises(ValueError, match="Unsupported format type"):
            config.get_output_path("invalid")
        
        # Test custom filename
        custom_path = config.get_output_path("html", "custom_resume")
        assert custom_path.name == "custom_resume.html"
    
    def test_output_config_from_dict(self):
        """Test OutputConfig.from_dict class method."""
        config_dict = {
            "output_dir": "test_dir",
            "filename_prefix": "test_file",
            "overwrite_existing": True
        }
        
        config = OutputConfig.from_dict(config_dict)
        assert config.output_dir == Path("test_dir")
        assert config.filename_prefix == "test_file"
        assert config.overwrite_existing is True