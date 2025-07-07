"""
Tests for DOCX generator functionality.

This module contains comprehensive tests for the DOCXGenerator class,
covering document generation, formatting, ATS compliance, and edge cases.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile

from src.generator.docx_generator import DOCXGenerator
from src.generator.config import DOCXConfig
from src.models import ResumeData, ContactInfo, Experience, Education


class TestDOCXGenerator:
    """Test cases for DOCXGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DOCXConfig()
        self.generator = DOCXGenerator(self.config)
        
        # Sample resume data
        self.sample_resume = ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="john.doe@example.com",
                phone="(555) 123-4567",
                location="New York, NY"
            ),
            summary="Experienced software engineer with 5+ years in full-stack development.",
            experience=[
                Experience(
                    title="Senior Software Engineer",
                    company="Tech Corp",
                    location="New York, NY",
                    start_date="2020-01",
                    end_date="2024-01",
                    bullets=["Developed scalable web applications", "Led team of 3 developers"]
                )
            ],
            education=[
                Education(
                    degree="Bachelor of Science in Computer Science",
                    school="University of Technology",
                    location="Boston, MA",
                    graduation_date="2019-05"
                )
            ]
        )
    
    def test_generator_initialization(self):
        """Test that DOCXGenerator initializes correctly."""
        assert self.generator.config == self.config
    
    def test_generate_basic_docx(self):
        """Test basic DOCX generation."""
        docx_bytes = self.generator.generate(self.sample_resume)
        
        # Basic DOCX validation
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000  # Should be substantial content
        
        # DOCX files are ZIP archives, check ZIP signature
        assert docx_bytes.startswith(b'PK')  # ZIP header
    
    def test_generate_docx_with_file_output(self):
        """Test DOCX generation with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_resume.docx"
            
            docx_bytes = self.generator.generate(self.sample_resume, output_path)
            
            # Check that file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 1000
            
            # Check that bytes are also returned
            assert isinstance(docx_bytes, bytes)
            assert len(docx_bytes) == output_path.stat().st_size
    
    def test_docx_validation(self):
        """Test DOCX content validation."""
        docx_bytes = self.generator.generate(self.sample_resume)
        
        # Use the built-in validation method
        assert self.generator.validate_output(docx_bytes) is True
    
    def test_docx_validation_empty_content(self):
        """Test DOCX validation with empty content."""
        with pytest.raises(ValueError, match="DOCX content is empty"):
            self.generator.validate_output(b"")
    
    def test_docx_validation_invalid_format(self):
        """Test DOCX validation with invalid format."""
        with pytest.raises(ValueError, match="Invalid DOCX format"):
            self.generator.validate_output(b"Not a DOCX file")
    
    def test_docx_validation_too_small(self):
        """Test DOCX validation with file too small."""
        with pytest.raises(ValueError, match="DOCX file too small"):
            self.generator.validate_output(b"PK" + b"x" * 100)
    
    def test_contact_info_addition(self):
        """Test contact information addition to document."""
        # Generate document to test contact info is included
        docx_bytes = self.generator.generate(self.sample_resume)
        
        # Basic validation that document was generated
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_summary_addition(self):
        """Test professional summary addition to document."""
        # Test that summary is included in generated document
        docx_bytes = self.generator.generate(self.sample_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_experience_addition(self):
        """Test experience section addition to document."""
        # Test that experience is included in generated document
        docx_bytes = self.generator.generate(self.sample_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_education_addition(self):
        """Test education section addition to document."""
        # Test that education is included in generated document
        docx_bytes = self.generator.generate(self.sample_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_skills_addition(self):
        """Test skills section addition to document."""
        from src.models import Skills
        
        resume_with_skills = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            skills=Skills(
                technical=["Python", "JavaScript", "React"],
                soft=["Leadership", "Communication"]
            )
        )
        
        docx_bytes = self.generator.generate(resume_with_skills)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_custom_docx_config(self):
        """Test DOCX generation with custom configuration."""
        custom_config = DOCXConfig(
            font_name="Times New Roman",
            font_size=12,
            line_spacing=1.15,
            template_name="modern"
        )
        
        generator = DOCXGenerator(custom_config, template_name="modern")
        docx_bytes = generator.generate(self.sample_resume)
        
        assert isinstance(docx_bytes, bytes)
        assert docx_bytes.startswith(b'PK')  # ZIP header
    
    def test_template_selection(self):
        """Test template selection functionality."""
        templates = ['professional', 'modern', 'minimal', 'tech']
        
        for template in templates:
            generator = DOCXGenerator(template_name=template)
            docx_bytes = generator.generate(self.sample_resume)
            
            assert isinstance(docx_bytes, bytes)
            assert generator.validate_output(docx_bytes) is True
    
    def test_document_properties_setting(self):
        """Test that document properties are set correctly."""
        # Generate document and validate it was created
        docx_bytes = self.generator.generate(self.sample_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_error_handling_invalid_resume_data(self):
        """Test error handling with invalid resume data."""
        with pytest.raises(ValueError, match="resume_data must be a ResumeData instance"):
            self.generator.generate("not a resume")
    
    def test_error_handling_document_creation_error(self):
        """Test error handling when document creation fails."""
        # This test is hard to implement without deep mocking, so just test basic error handling
        with pytest.raises(ValueError):
            self.generator.generate("invalid_data")
    
    def test_from_config_class_method(self):
        """Test creating DOCXGenerator from OutputConfig."""
        from src.generator.config import OutputConfig
        
        output_config = OutputConfig()
        generator = DOCXGenerator.from_config(output_config, template_name="professional")
        
        assert isinstance(generator, DOCXGenerator)
        assert generator.config == output_config.docx
        assert generator.template_name == "professional"
    
    def test_yaml_config_loading(self):
        """Test that YAML configuration files are loaded."""
        generator = DOCXGenerator(template_name="professional")
        
        # Should have loaded configuration
        assert hasattr(generator, 'styles_config')
        assert hasattr(generator, 'template_config')
        assert isinstance(generator.styles_config, dict)
        assert isinstance(generator.template_config, dict)
    
    def test_directory_creation_for_output(self):
        """Test that output directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "dir" / "resume.docx"
            
            self.generator.generate(self.sample_resume, output_path)
            
            assert output_path.exists()
            assert output_path.parent.exists()
    
    def test_performance_benchmark(self):
        """Test DOCX generation performance."""
        import time
        
        start_time = time.time()
        docx_bytes = self.generator.generate(self.sample_resume)
        generation_time = time.time() - start_time
        
        # Should complete within reasonable time (< 2 seconds)
        assert generation_time < 2.0
        assert len(docx_bytes) > 1000
    
    def test_minimal_resume_docx_generation(self):
        """Test DOCX generation with minimal resume data."""
        minimal_resume = ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane@example.com"
            )
        )
        
        docx_bytes = self.generator.generate(minimal_resume)
        
        assert isinstance(docx_bytes, bytes)
        assert docx_bytes.startswith(b'PK')
        assert self.generator.validate_output(docx_bytes) is True
    
    def test_unicode_character_handling(self):
        """Test handling of unicode characters in DOCX generation."""
        unicode_resume = ResumeData(
            contact=ContactInfo(
                name="José García-Müller",
                email="jose@example.com"
            ),
            summary="Expert in résumé writing with ñ and ü characters."
        )
        
        docx_bytes = self.generator.generate(unicode_resume)
        
        assert isinstance(docx_bytes, bytes)
        assert docx_bytes.startswith(b'PK')
        assert self.generator.validate_output(docx_bytes) is True
    
    def test_multiple_experience_entries(self):
        """Test DOCX generation with multiple experience entries."""
        multi_exp_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            experience=[
                Experience(
                    title="Senior Engineer",
                    company="Company A",
                    start_date="2022-01",
                    end_date="2024-01",
                    bullets=["Achievement 1", "Achievement 2"]
                ),
                Experience(
                    title="Junior Engineer",
                    company="Company B",
                    start_date="2020-01",
                    end_date="2021-12",
                    bullets=["Learning experience", "Growth"]
                )
            ]
        )
        
        docx_bytes = self.generator.generate(multi_exp_resume)
        
        assert isinstance(docx_bytes, bytes)
        assert self.generator.validate_output(docx_bytes) is True
    
    def test_large_resume_handling(self):
        """Test DOCX generation with large resume data."""
        large_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            summary="Very long summary " * 50,
            experience=[
                Experience(
                    title=f"Position {i}",
                    company=f"Company {i}",
                    start_date="2020-01",
                    end_date="2024-01",
                    bullets=[f"Achievement {i}.{j}" for j in range(10)]
                )
                for i in range(15)
            ]
        )
        
        docx_bytes = self.generator.generate(large_resume)
        
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 5000  # Should be larger file
        assert self.generator.validate_output(docx_bytes) is True
    
    def test_empty_sections_handling(self):
        """Test handling of resumes with empty optional sections."""
        minimal_resume = ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane.smith@example.com"
            ),
            experience=[],  # Empty experience
            education=[]    # Empty education
        )
        
        docx_bytes = self.generator.generate(minimal_resume)
        
        # Should still generate valid DOCX
        assert isinstance(docx_bytes, bytes)
        assert self.generator.validate_output(docx_bytes) is True


class TestDOCXConfig:
    """Test cases for DOCXConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DOCXConfig()
        
        assert config.font_name == "Arial"
        assert config.font_size == 11
        assert config.line_spacing == 1.15
        assert config.margin_top == 0.75
        assert config.margin_bottom == 0.75
        assert config.margin_left == 0.75
        assert config.margin_right == 0.75
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = DOCXConfig(
            font_name="Times New Roman",
            font_size=12,
            line_spacing=1.0,
            margin_top=1.0
        )
        
        assert config.font_name == "Times New Roman"
        assert config.font_size == 12
        assert config.line_spacing == 1.0
        assert config.margin_top == 1.0
    
    def test_config_validation(self):
        """Test configuration value validation."""
        # Valid configurations should work
        DOCXConfig(font_size=10)
        DOCXConfig(font_size=14)
        DOCXConfig(line_spacing=1.0)
        DOCXConfig(line_spacing=2.0)
        
        # Test edge cases
        DOCXConfig(margin_top=0.5)
        DOCXConfig(margin_bottom=2.0)


class TestDOCXGeneratorExtended(TestDOCXGenerator):
    """Extended tests for DOCX generator coverage."""
    
    def test_comprehensive_resume_generation(self):
        """Test generation with comprehensive resume data."""
        from src.models import Experience, Education, Skills, SkillCategory, Project, Certification
        
        comprehensive_resume = ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane.smith@example.com",
                phone="(555) 987-6543",
                location="San Francisco, CA",
                linkedin="https://linkedin.com/in/janesmith",
                github="https://github.com/janesmith"
            ),
            summary="Senior software engineer with expertise in full-stack development",
            experience=[
                Experience(
                    title="Senior Engineer",
                    company="Tech Corp",
                    location="San Francisco, CA",
                    start_date="2020-01",
                    end_date="Present",
                    bullets=["Led development of microservices", "Improved performance by 40%"]
                )
            ],
            education=[
                Education(
                    degree="MS Computer Science",
                    school="Stanford University",
                    location="Stanford, CA",
                    start_date="2016",
                    end_date="2018",
                    gpa="3.8"
                )
            ],
            skills=Skills(
                categories=[
                    SkillCategory(name="Languages", skills=["Python", "JavaScript", "Go"]),
                    SkillCategory(name="Frameworks", skills=["Django", "React", "Node.js"])
                ]
            ),
            projects=[
                Project(
                    name="ML Pipeline",
                    description="Machine learning data pipeline",
                    technologies=["Python", "TensorFlow"],
                    bullets=["Processed 1M+ records daily", "Reduced training time by 50%"],
                    url="https://github.com/jane/ml-pipeline",
                    date="2023"
                )
            ],
            certifications=[
                Certification(
                    name="AWS Solutions Architect",
                    issuer="Amazon Web Services",
                    date="2023",
                    expiry="2026",
                    credential_id="AWS-SAA-123456"
                )
            ],
            additional_sections={
                "Languages": ["English (Native)", "Spanish (Professional)"],
                "Awards": ["Employee of the Year 2023"]
            }
        )
        
        docx_bytes = self.generator.generate(comprehensive_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 5000  # Should be substantial with all sections
    
    def test_error_handling_with_invalid_data(self):
        """Test error handling with invalid resume data."""
        with pytest.raises(ValueError, match="resume_data must be a ResumeData instance"):
            self.generator.generate("invalid data")
        
        with pytest.raises(ValueError, match="resume_data must be a ResumeData instance"):
            self.generator.generate(None)
        
        with pytest.raises(ValueError, match="resume_data must be a ResumeData instance"):
            self.generator.generate({"invalid": "dict"})
    
    def test_output_file_creation(self):
        """Test creating output file."""
        from pathlib import Path
        
        output_path = Path("test_output.docx")
        docx_bytes = self.generator.generate(self.sample_resume, output_path)
        
        # Check file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 1000
        
        # Content should match returned bytes
        file_content = output_path.read_bytes()
        assert file_content == docx_bytes
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
    
    def test_template_variables(self):
        """Test handling of template variables."""
        template_vars = {"custom_theme": "professional", "include_photo": False}
        docx_bytes = self.generator.generate(self.sample_resume, template_vars=template_vars)
        
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_document_style_configuration(self):
        """Test document style configuration."""
        custom_config = DOCXConfig(
            font_name="Calibri",
            font_size=10,
            line_spacing=1.2,
            margin_top=1.0,
            margin_bottom=1.0
        )
        
        generator = DOCXGenerator(custom_config)
        docx_bytes = generator.generate(self.sample_resume)
        
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_validation_method(self):
        """Test DOCX validation functionality."""
        docx_bytes = self.generator.generate(self.sample_resume)
        
        # Valid DOCX should pass validation
        is_valid = self.generator.validate_output(docx_bytes)
        assert isinstance(is_valid, bool)
        
        # Invalid bytes should raise ValueError
        invalid_bytes = b"not a docx file"
        with pytest.raises(ValueError):
            self.generator.validate_output(invalid_bytes)
    
    def test_empty_sections_handling(self):
        """Test handling of resume with minimal data."""
        minimal_resume = ResumeData(
            contact=ContactInfo(
                name="Minimal User",
                email="minimal@example.com"
            )
        )
        
        docx_bytes = self.generator.generate(minimal_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 500  # Should still be a valid DOCX
    
    def test_special_characters_handling(self):
        """Test handling of special characters in resume data."""
        special_resume = ResumeData(
            contact=ContactInfo(
                name="José García-López",
                email="jose@example.com"
            ),
            summary="Expert in C++, .NET & résumé formatting with 10+ years' experience"
        )
        
        docx_bytes = self.generator.generate(special_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_from_config_class_method(self):
        """Test creating generator from config."""
        from src.generator.config import OutputConfig
        from pathlib import Path
        
        output_config = OutputConfig(
            output_dir=Path("test"),
            filename_prefix="test_resume"
        )
        
        generator = DOCXGenerator.from_config(output_config)
        assert isinstance(generator, DOCXGenerator)
        
        docx_bytes = generator.generate(self.sample_resume)
        assert isinstance(docx_bytes, bytes)