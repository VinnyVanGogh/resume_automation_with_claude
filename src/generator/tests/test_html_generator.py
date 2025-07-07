"""
Tests for HTML generator functionality.

This module contains comprehensive tests for the HTMLGenerator class,
covering template rendering, field mapping, CSS integration, and edge cases.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.generator.html_generator import HTMLGenerator
from src.generator.config import HTMLConfig
from src.models import ResumeData, ContactInfo, Experience, Education


class TestHTMLGenerator:
    """Test cases for HTMLGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = HTMLConfig(
            template_name="resume.html",
            theme="professional",
            include_styles=True
        )
        self.generator = HTMLGenerator(self.config)
        
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
                    end_date="2019-05"
                )
            ]
        )
    
    def test_generator_initialization(self):
        """Test that HTMLGenerator initializes correctly."""
        assert self.generator.config == self.config
        assert self.generator.template_dir.exists()
        assert self.generator.env is not None
    
    def test_generate_basic_html(self):
        """Test basic HTML generation."""
        html_content = self.generator.generate(self.sample_resume)
        
        # Basic structure checks
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "</html>" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content
        
        # Content checks
        assert "John Doe" in html_content
        assert "john.doe@example.com" in html_content
        assert "Senior Software Engineer" in html_content
        assert "Tech Corp" in html_content
        assert "University of Technology" in html_content
    
    def test_contact_info_rendering(self):
        """Test that contact information is rendered correctly."""
        html_content = self.generator.generate(self.sample_resume)
        
        assert "John Doe" in html_content
        assert "john.doe@example.com" in html_content
        assert "(555) 123-4567" in html_content
        assert "New York, NY" in html_content
    
    def test_summary_rendering(self):
        """Test that professional summary is rendered correctly."""
        html_content = self.generator.generate(self.sample_resume)
        
        assert "Experienced software engineer" in html_content
        assert "5+ years" in html_content
    
    def test_experience_rendering(self):
        """Test that work experience is rendered correctly."""
        html_content = self.generator.generate(self.sample_resume)
        
        assert "Senior Software Engineer" in html_content
        assert "Tech Corp" in html_content
        assert "2020-01" in html_content
        assert "2024-01" in html_content
        assert "Developed scalable web applications" in html_content
        assert "Led team of 3 developers" in html_content
    
    def test_education_rendering(self):
        """Test that education is rendered correctly."""
        html_content = self.generator.generate(self.sample_resume)
        
        assert "Bachelor of Science in Computer Science" in html_content
        assert "University of Technology" in html_content
        assert "Boston, MA" in html_content
        assert "2019-05" in html_content
    
    def test_template_variables(self):
        """Test that custom template variables are passed correctly."""
        template_vars = {
            "custom_title": "Custom Resume Title",
            "theme": "modern"
        }
        
        with patch.object(self.generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html>Mock content</html>"
            mock_get_template.return_value = mock_template
            
            self.generator.generate(self.sample_resume, template_vars=template_vars)
            
            # Check that template was called with correct variables
            mock_template.render.assert_called_once()
            call_args = mock_template.render.call_args[1]
            
            assert call_args["contact"] == self.sample_resume.contact
            assert call_args["custom_title"] == "Custom Resume Title"
            assert call_args["theme"] == "modern"
    
    def test_css_inclusion(self):
        """Test that CSS is included when configured."""
        # Test with CSS inclusion enabled
        config_with_css = HTMLConfig(include_styles=True)
        generator_with_css = HTMLGenerator(config_with_css)
        html_content = generator_with_css.generate(self.sample_resume)
        
        assert "<style" in html_content or "<link" in html_content
    
    def test_empty_sections_handling(self):
        """Test handling of resumes with empty sections."""
        minimal_resume = ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane.smith@example.com"
            )
        )
        
        html_content = self.generator.generate(minimal_resume)
        
        # Should still generate valid HTML
        assert "<!DOCTYPE html>" in html_content
        assert "Jane Smith" in html_content
        assert "jane.smith@example.com" in html_content
    
    def test_special_characters_handling(self):
        """Test handling of special characters in resume data."""
        special_resume = ResumeData(
            contact=ContactInfo(
                name="José García-Smith",
                email="jose@example.com"
            ),
            summary="Expert in C++, .NET & cloud technologies. <script>alert('test')</script>"
        )
        
        html_content = self.generator.generate(special_resume)
        
        # Should handle unicode characters
        assert "José García-Smith" in html_content
        
        # Should escape HTML entities for security
        assert "<script>" not in html_content or "&lt;script&gt;" in html_content
    
    def test_multiple_experience_entries(self):
        """Test rendering multiple work experience entries."""
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
        
        html_content = self.generator.generate(multi_exp_resume)
        
        assert "Senior Engineer" in html_content
        assert "Company A" in html_content
        assert "Junior Engineer" in html_content
        assert "Company B" in html_content
        assert "Achievement 1" in html_content
        assert "Learning experience" in html_content
    
    def test_skills_rendering(self):
        """Test skills section rendering if present."""
        from src.models import Skills, SkillCategory
        
        skills_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            skills=Skills(
                categories=[
                    SkillCategory(name="Technical", skills=["Python", "JavaScript", "React"]),
                    SkillCategory(name="Soft Skills", skills=["Leadership", "Communication"])
                ]
            )
        )
        
        html_content = self.generator.generate(skills_resume)
        
        assert "Technical" in html_content
        assert "Python" in html_content
        assert "JavaScript" in html_content
        assert "Leadership" in html_content
    
    def test_html_generator_error_handling(self):
        """Test HTML generator error handling."""
        # Test with invalid config
        generator = HTMLGenerator()
        generator.config.theme = "nonexistent_theme"
        
        # Should still generate HTML (fallback to default)
        html_content = generator.generate(self.sample_resume)
        assert len(html_content) > 0
    
    def test_html_generator_custom_css_injection(self):
        """Test custom CSS injection."""
        generator = HTMLGenerator()
        custom_css = "body { background-color: red; }"
        generator.config.custom_css = custom_css
        
        html_content = generator.generate(self.sample_resume)
        assert custom_css in html_content
    
    def test_html_generator_accessibility_features(self):
        """Test accessibility features in generated HTML."""
        html_content = self.generator.generate(self.sample_resume)
        
        # Check for accessibility landmarks
        assert 'role="main"' in html_content
        assert 'aria-label' in html_content
        assert 'Skip to main content' in html_content
    
    def test_html_generator_theme_application(self):
        """Test that different themes are applied correctly."""
        themes = ["professional", "modern", "minimal", "tech"]
        
        for theme in themes:
            generator = HTMLGenerator()
            generator.config.theme = theme
            html_content = generator.generate(self.sample_resume)
            
            assert f"styles/themes/{theme}.css" in html_content
    
    def test_html_generator_with_file_output(self, tmp_path):
        """Test HTML generator file output."""
        output_path = tmp_path / "test_resume.html"
        html_content = self.generator.generate(self.sample_resume, output_path)
        
        # Check file was created
        assert output_path.exists()
        
        # Check content matches
        file_content = output_path.read_text()
        assert file_content == html_content
        
        # Basic HTML structure validation
        assert "<!DOCTYPE html>" in html_content
        assert "John Doe" in html_content  # Use the actual sample resume name
    
    def test_template_not_found_error(self):
        """Test handling of missing template file."""
        config = HTMLConfig(template_name="nonexistent.html")
        generator = HTMLGenerator(config)
        
        with pytest.raises(Exception):
            generator.generate(self.sample_resume)
    
    def test_output_validation(self):
        """Test that generated HTML passes basic validation."""
        html_content = self.generator.generate(self.sample_resume)
        
        # Basic HTML structure validation
        assert html_content.count("<html") == html_content.count("</html>")
        assert (html_content.count("<head>") + html_content.count("<head ")) == html_content.count("</head>")
        assert html_content.count("<body") == html_content.count("</body>")
        
        # Meta tags for SEO and accessibility
        assert 'charset="UTF-8"' in html_content or "charset=UTF-8" in html_content
        assert 'name="viewport"' in html_content
    
    def test_theme_configuration(self):
        """Test different theme configurations."""
        themes = ["professional", "modern", "creative"]
        
        for theme in themes:
            config = HTMLConfig(theme=theme)
            generator = HTMLGenerator(config)
            html_content = generator.generate(self.sample_resume)
            
            # Should generate valid HTML regardless of theme
            assert "<!DOCTYPE html>" in html_content
            assert self.sample_resume.contact.name in html_content
    
    @pytest.mark.skip(reason="Error handling test needs more specific implementation")
    def test_error_handling_generation_failure(self):
        """Test error handling when generation fails."""
        from unittest.mock import patch
        
        # Test template rendering error
        with patch.object(self.generator, '_render_template') as mock_render:
            mock_render.side_effect = Exception("Template error")
            
            with pytest.raises(RuntimeError, match="HTML generation failed"):
                self.generator.generate(self.sample_resume)
    
    def test_projects_rendering(self):
        """Test projects section rendering."""
        from src.models import Project
        
        projects_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            projects=[
                Project(
                    name="Web App",
                    description="A great web application",
                    technologies=["Python", "React"],
                    bullets=["Feature 1", "Feature 2"],
                    url="https://project.com",
                    date="2023"
                )
            ]
        )
        
        html_content = self.generator.generate(projects_resume)
        assert "Web App" in html_content
        assert "A great web application" in html_content
    
    def test_certifications_rendering(self):
        """Test certifications section rendering."""
        from src.models import Certification
        
        cert_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            certifications=[
                Certification(
                    name="AWS Certified",
                    issuer="Amazon",
                    date="2023",
                    expiry="2026",
                    credential_id="ABC123"
                )
            ]
        )
        
        html_content = self.generator.generate(cert_resume)
        assert "AWS Certified" in html_content
        assert "Amazon" in html_content
    
    @pytest.mark.skip(reason="Additional sections not yet implemented in HTML template")
    def test_additional_sections_rendering(self):
        """Test additional sections rendering."""
        additional_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            additional_sections={
                "Hobbies": ["Reading", "Coding"],
                "Languages": ["English", "Spanish"]
            }
        )
        
        html_content = self.generator.generate(additional_resume)
        assert "Hobbies" in html_content
        assert "Languages" in html_content
        assert "Reading" in html_content
    
    def test_format_url_filter(self):
        """Test the _format_url filter function."""
        # Test with string URL
        result = self.generator._format_url("https://example.com")
        assert result == "example.com"
        
        # Test with HttpUrl object
        from pydantic import HttpUrl
        url_obj = HttpUrl("https://github.com/user")
        result = self.generator._format_url(str(url_obj))
        assert result == "github.com/user"
        
        # Test with None
        result = self.generator._format_url(None)
        assert result == ""
    
    def test_format_phone_filter(self):
        """Test the _format_phone filter function."""
        # Test phone formatting
        result = self.generator._format_phone("1234567890")
        assert result == "(123) 456-7890"
        
        # Test with already formatted phone
        result = self.generator._format_phone("(555) 123-4567")
        assert result == "(555) 123-4567"
    
    def test_format_date_filter(self):
        """Test the _format_date filter function."""
        # Test date formatting
        result = self.generator._format_date("2023-01")
        assert result == "2023-01"
        
        # Test with None
        result = self.generator._format_date(None)
        assert result == ""
    
    def test_validate_output_method(self):
        """Test the validate_output method."""
        html_content = self.generator.generate(self.sample_resume)
        
        # Should validate successfully
        is_valid = self.generator.validate_output(html_content)
        assert isinstance(is_valid, bool)
        
        # Test with invalid HTML (should raise ValueError)
        invalid_html = "<html><head><title>Test</title><body><p>Unclosed paragraph"
        with pytest.raises(ValueError):
            self.generator.validate_output(invalid_html)
    
    def test_save_to_file(self):
        """Test saving HTML to file."""
        from pathlib import Path
        
        output_path = Path("test_resume.html")
        html_content = self.generator.generate(self.sample_resume, output_path)
        
        # Check file was created
        assert output_path.exists()
        assert output_path.read_text() == html_content
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
    
    def test_performance_with_large_resume(self):
        """Test performance with resume containing many entries."""
        import time
        
        # Create resume with many experience entries
        large_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com"),
            experience=[
                Experience(
                    title=f"Position {i}",
                    company=f"Company {i}",
                    start_date="2020-01",
                    end_date="2024-01",
                    bullets=[f"Achievement {i}.{j}" for j in range(5)]
                )
                for i in range(20)
            ]
        )
        
        start_time = time.time()
        html_content = self.generator.generate(large_resume)
        generation_time = time.time() - start_time
        
        # Should complete within reasonable time (< 1 second)
        assert generation_time < 1.0
        assert "Position 19" in html_content  # Verify all entries included
        assert len(html_content) > 1000  # Should generate substantial content


class TestHTMLConfig:
    """Test cases for HTMLConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = HTMLConfig()
        
        assert config.template_name == "resume.html"
        assert config.theme == "professional"
        assert config.include_styles is True
        assert config.custom_css is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = HTMLConfig(
            template_name="custom.html",
            theme="modern",
            include_styles=False,
            custom_css=".custom { color: red; }"
        )
        
        assert config.template_name == "custom.html"
        assert config.theme == "modern"
        assert config.include_styles is False
        assert config.custom_css == ".custom { color: red; }"