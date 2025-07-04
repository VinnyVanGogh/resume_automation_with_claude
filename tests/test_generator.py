"""
Tests for the resume output generator module.
"""

import pytest
from pathlib import Path
from src.generator import ResumeGenerator
from src.parser import ResumeSection


class TestResumeGenerator:
    """Test cases for ResumeGenerator class."""
    
    def test_generator_initialization(self):
        """Test ResumeGenerator can be initialized."""
        generator = ResumeGenerator()
        assert generator is not None
        assert generator.config_path is None
    
    def test_generator_with_config(self):
        """Test ResumeGenerator initialization with config path."""
        config_path = "test_config.yaml"
        generator = ResumeGenerator(config_path=config_path)
        assert generator.config_path == config_path
    
    def test_generate_html_basic(self):
        """Test basic HTML generation."""
        generator = ResumeGenerator()
        sections = {
            "summary": ResumeSection(
                title="Summary",
                content=["Experienced software engineer"],
                level=2
            )
        }
        
        html_content = generator.generate_html(sections)
        assert isinstance(html_content, str)
        assert "html" in html_content.lower()
        assert "resume" in html_content.lower()
    
    @pytest.mark.skip(reason="Implementation pending")
    def test_generate_pdf(self):
        """Test PDF generation."""
        generator = ResumeGenerator()
        sections = {
            "summary": ResumeSection(
                title="Summary",
                content=["Experienced software engineer"],
                level=2
            )
        }
        
        output_path = "test_resume.pdf"
        generator.generate_pdf(sections, output_path)
        # TODO: Add assertions once PDF generation is implemented
    
    @pytest.mark.skip(reason="Implementation pending")
    def test_generate_docx(self):
        """Test DOCX generation."""
        generator = ResumeGenerator()
        sections = {
            "summary": ResumeSection(
                title="Summary",
                content=["Experienced software engineer"],
                level=2
            )
        }
        
        output_path = "test_resume.docx"
        generator.generate_docx(sections, output_path)
        # TODO: Add assertions once DOCX generation is implemented
    
    def test_generate_all_formats(self):
        """Test generating all formats."""
        generator = ResumeGenerator()
        sections = {
            "summary": ResumeSection(
                title="Summary",
                content=["Experienced software engineer"],
                level=2
            )
        }
        
        # Use a temporary directory for testing
        output_dir = "test_output"
        results = generator.generate_all_formats(sections, output_dir)
        
        assert isinstance(results, dict)
        assert "html" in results
        assert "pdf" in results
        assert "docx" in results
        
        # Check that HTML file was created
        html_path = Path(results["html"])
        assert html_path.exists()
        assert html_path.suffix == ".html"
        
        # Cleanup
        if html_path.exists():
            html_path.unlink()
        if html_path.parent.exists():
            html_path.parent.rmdir()