"""
Tests for PDF generator functionality.

This module contains comprehensive tests for the PDFGenerator class,
covering PDF creation, validation, metadata, and WeasyPrint integration.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile

from src.generator.pdf_generator import PDFGenerator
from src.generator.config import PDFConfig
from src.models import ResumeData, ContactInfo, Experience, Education


class TestPDFGenerator:
    """Test cases for PDFGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = PDFConfig()
        self.generator = PDFGenerator(self.config)
        
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
        """Test that PDFGenerator initializes correctly."""
        assert self.generator.config == self.config
        assert self.generator.template_dir.exists()
        assert self.generator.font_config is not None
        assert self.generator.html_generator is not None
    
    def test_generate_basic_pdf(self):
        """Test basic PDF generation."""
        pdf_bytes = self.generator.generate(self.sample_resume)
        
        # Basic PDF validation
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000  # Should be substantial content
        assert pdf_bytes.startswith(b'%PDF-')  # PDF header
        assert b'%%EOF' in pdf_bytes  # PDF footer
    
    def test_generate_pdf_with_file_output(self):
        """Test PDF generation with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_resume.pdf"
            
            pdf_bytes = self.generator.generate(self.sample_resume, output_path)
            
            # Check that file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 1000
            
            # Check that bytes are also returned
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) == output_path.stat().st_size
    
    def test_pdf_validation(self):
        """Test PDF content validation."""
        pdf_bytes = self.generator.generate(self.sample_resume)
        
        # Use the built-in validation method
        assert self.generator.validate_output(pdf_bytes) is True
    
    def test_pdf_validation_empty_content(self):
        """Test PDF validation with empty content."""
        with pytest.raises(ValueError, match="PDF content is empty"):
            self.generator.validate_output(b"")
    
    def test_pdf_validation_invalid_format(self):
        """Test PDF validation with invalid format."""
        with pytest.raises(ValueError, match="Invalid PDF format"):
            self.generator.validate_output(b"Not a PDF file")
    
    def test_pdf_validation_too_small(self):
        """Test PDF validation with file too small."""
        with pytest.raises(ValueError, match="PDF file too small"):
            self.generator.validate_output(b"%PDF-1.7\n" + b"x" * 100)
    
    def test_page_count_estimation(self):
        """Test page count estimation."""
        pdf_bytes = self.generator.generate(self.sample_resume)
        page_count = self.generator.get_page_count(pdf_bytes)
        
        assert isinstance(page_count, int)
        assert page_count >= 1
    
    def test_page_count_with_large_resume(self):
        """Test page count with resume that should span multiple pages."""
        # Create a resume with lots of content
        large_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            summary="Very long summary that contains extensive details about professional experience and skills. " * 10,
            experience=[
                Experience(
                    title=f"Position {i}",
                    company=f"Company {i}",
                    start_date="2020-01",
                    end_date="2024-01",
                    bullets=[f"Very detailed achievement {i}.{j} with extensive explanation and context." for j in range(10)]
                )
                for i in range(10)
            ]
        )
        
        pdf_bytes = self.generator.generate(large_resume)
        page_count = self.generator.get_page_count(pdf_bytes)
        
        # Large resume should likely span multiple pages
        assert page_count >= 1
    
    def test_custom_pdf_config(self):
        """Test PDF generation with custom configuration."""
        custom_config = PDFConfig(
            page_size="A4",
            margin_top=1.0,
            margin_bottom=1.0,
            margin_left=1.0,
            margin_right=1.0,
            font_family="Arial",
            font_size=12
        )
        
        generator = PDFGenerator(custom_config)
        pdf_bytes = generator.generate(self.sample_resume)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
    
    def test_pdf_css_generation(self):
        """Test PDF-specific CSS generation."""
        css_content = self.generator._get_pdf_css()
        
        assert isinstance(css_content, str)
        assert "@page" in css_content
        assert "margin:" in css_content
        assert "font-family:" in css_content
        assert "page-break" in css_content
    
    def test_pdf_specific_css_configuration(self):
        """Test PDF-specific CSS with custom configuration."""
        custom_config = PDFConfig(
            page_size="Letter",
            font_family="Times New Roman",
            font_size=11
        )
        
        generator = PDFGenerator(custom_config)
        css_content = generator._get_pdf_specific_css()
        
        assert "Letter" in css_content
        assert "Times New Roman" in css_content
        assert "11pt" in css_content
    
    def test_html_content_generation_for_pdf(self):
        """Test HTML content generation optimized for PDF."""
        html_content = self.generator._generate_pdf_html(
            self.sample_resume,
            {"pdf_mode": True}
        )
        
        assert isinstance(html_content, str)
        assert "<!DOCTYPE html>" in html_content
        assert "John Doe" in html_content
    
    def test_template_variables_for_pdf(self):
        """Test that PDF-specific template variables are passed."""
        with patch.object(self.generator.html_generator, 'generate') as mock_generate:
            mock_generate.return_value = "<html>Mock content</html>"
            
            self.generator._generate_pdf_html(self.sample_resume, {"custom": "value"})
            
            # Check that PDF-specific variables were added
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[1]["template_vars"]
            
            assert call_args["pdf_mode"] is True
            assert call_args["include_print_styles"] is True
            assert call_args["optimize_for_print"] is True
            assert call_args["custom"] == "value"
    
    def test_error_handling_invalid_resume_data(self):
        """Test error handling with invalid resume data."""
        with pytest.raises(ValueError, match="resume_data must be a ResumeData instance"):
            self.generator.generate("not a resume")
    
    def test_error_handling_template_error(self):
        """Test error handling when template rendering fails."""
        with patch.object(self.generator.html_generator, 'generate') as mock_generate:
            mock_generate.side_effect = Exception("Template error")
            
            with pytest.raises(RuntimeError, match="PDF generation failed"):
                self.generator.generate(self.sample_resume)
    
    def test_default_css_fallback(self):
        """Test fallback to default CSS when styles.css not found."""
        # Mock missing CSS file
        with patch.object(Path, 'read_text') as mock_read:
            mock_read.side_effect = FileNotFoundError()
            
            css_content = self.generator._get_pdf_css()
            
            assert isinstance(css_content, str)
            assert "Default PDF styles" in css_content
            assert "font-family: Arial" in css_content
    
    def test_from_config_class_method(self):
        """Test creating PDFGenerator from OutputConfig."""
        from src.generator.config import OutputConfig
        
        output_config = OutputConfig()
        generator = PDFGenerator.from_config(output_config)
        
        assert isinstance(generator, PDFGenerator)
        assert generator.config == output_config.pdf
    
    def test_directory_creation_for_output(self):
        """Test that output directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "dir" / "resume.pdf"
            
            self.generator.generate(self.sample_resume, output_path)
            
            assert output_path.exists()
            assert output_path.parent.exists()
    
    def test_performance_benchmark(self):
        """Test PDF generation performance."""
        import time
        
        start_time = time.time()
        pdf_bytes = self.generator.generate(self.sample_resume)
        generation_time = time.time() - start_time
        
        # Should complete within reasonable time (< 3 seconds)
        assert generation_time < 3.0
        assert len(pdf_bytes) > 1000
    
    def test_minimal_resume_pdf_generation(self):
        """Test PDF generation with minimal resume data."""
        minimal_resume = ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane@example.com"
            )
        )
        
        pdf_bytes = self.generator.generate(minimal_resume)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
        assert self.generator.validate_output(pdf_bytes) is True
    
    def test_unicode_character_handling(self):
        """Test handling of unicode characters in PDF generation."""
        unicode_resume = ResumeData(
            contact=ContactInfo(
                name="José García-Müller",
                email="jose@example.com"
            ),
            summary="Expert in résumé writing with ñ and ü characters."
        )
        
        pdf_bytes = self.generator.generate(unicode_resume)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
        assert self.generator.validate_output(pdf_bytes) is True


class TestPDFConfig:
    """Test cases for PDFConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PDFConfig()
        
        assert config.page_size == "Letter"
        assert config.margin_top == 0.75
        assert config.margin_bottom == 0.75
        assert config.margin_left == 0.75
        assert config.margin_right == 0.75
        assert config.font_family == "Arial"
        assert config.font_size == 11
        assert config.optimize_size is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PDFConfig(
            page_size="A4",
            margin_top=1.0,
            font_family="Times New Roman",
            font_size=12,
            optimize_size=True
        )
        
        assert config.page_size == "A4"
        assert config.margin_top == 1.0
        assert config.font_family == "Times New Roman"
        assert config.font_size == 12
        assert config.optimize_size is True
    
    def test_config_validation(self):
        """Test configuration value validation."""
        # Valid configurations should work
        PDFConfig(font_size=10)
        PDFConfig(font_size=14)
        
        # Test edge cases
        PDFConfig(margin_top=0.0)
        PDFConfig(margin_bottom=2.0)