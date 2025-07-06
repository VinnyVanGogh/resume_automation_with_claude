#!/usr/bin/env python
"""
Tests for HTML template integration with the modular CSS architecture.

This module tests template rendering, theme switching, and integration
with the HTML generator.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from jinja2 import Environment, FileSystemLoader

from src.generator.html_generator import HTMLGenerator
from src.generator.config import HTMLConfig, OutputConfig
from src.models import ResumeData, ContactInfo, Experience, Education, Skills, Project, Certification


class TestTemplateRendering:
    """Test template rendering functionality."""
    
    @pytest.fixture
    def template_env(self) -> Environment:
        """Create Jinja2 environment for testing."""
        template_dir = Path(__file__).parent.parent
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    @pytest.fixture
    def sample_resume_data(self) -> ResumeData:
        """Create sample resume data for testing."""
        return ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="john.doe@example.com",
                phone="(555) 123-4567",
                location="San Francisco, CA",
                linkedin="https://linkedin.com/in/johndoe",
                github="https://github.com/johndoe",
                website="https://johndoe.com"
            ),
            summary="Experienced software engineer with expertise in full-stack development.",
            experience=[
                Experience(
                    title="Senior Software Engineer",
                    company="Tech Corp",
                    location="San Francisco, CA",
                    start_date="2020-01",
                    end_date="Present",
                    bullets=[
                        "Led development of microservices architecture",
                        "Mentored junior developers",
                        "Improved system performance by 40%"
                    ]
                )
            ],
            education=[
                Education(
                    degree="B.S. Computer Science",
                    school="University of California",
                    location="Berkeley, CA",
                    start_date="2012-09",
                    end_date="2016-05",
                    gpa="3.8",
                    honors=["Magna Cum Laude"]
                )
            ],
            skills=Skills(
                categories=[
                    {"name": "Languages", "skills": ["Python", "JavaScript", "Go"]},
                    {"name": "Frameworks", "skills": ["React", "Django", "FastAPI"]}
                ],
                raw_skills=["Python", "JavaScript", "Go", "React", "Django", "FastAPI"]
            ),
            projects=[
                Project(
                    name="Open Source Project",
                    description="A popular open source tool",
                    technologies=["Python", "Docker"],
                    url="https://github.com/johndoe/project",
                    date="2023"
                )
            ],
            certifications=[
                Certification(
                    name="AWS Solutions Architect",
                    issuer="Amazon Web Services",
                    date="2023-01",
                    credential_id="AWS-123456",
                    url="https://aws.amazon.com/verify/123456"
                )
            ]
        )
    
    def test_base_template_renders(self, template_env: Environment):
        """Test that base template renders without errors."""
        template = template_env.get_template("base.html")
        html = template.render()
        
        assert "<!DOCTYPE html>" in html
        assert '<html lang="en"' in html
        assert "Professional Resume" in html  # Default title
        assert "styles/base.css" in html
        assert "styles/components.css" in html
        assert "styles/themes/professional.css" in html
    
    def test_resume_template_renders(self, template_env: Environment, sample_resume_data: ResumeData):
        """Test that resume template renders with data."""
        template = template_env.get_template("resume.html")
        
        context = {
            "contact": sample_resume_data.contact,
            "summary": sample_resume_data.summary,
            "experience": sample_resume_data.experience,
            "education": sample_resume_data.education,
            "skills": sample_resume_data.skills,
            "projects": sample_resume_data.projects,
            "certifications": sample_resume_data.certifications,
            "has_projects": True,
            "has_certifications": True,
            "has_summary": True,
            "config": HTMLConfig()
        }
        
        html = template.render(**context)
        
        # Check basic structure
        assert "John Doe" in html
        assert "john.doe@example.com" in html
        assert "Senior Software Engineer" in html
        assert "Tech Corp" in html
        assert "B.S. Computer Science" in html
        assert "Python" in html
        assert "Open Source Project" in html
        assert "AWS Solutions Architect" in html
    
    def test_theme_switching(self, template_env: Environment):
        """Test that different themes can be loaded."""
        template = template_env.get_template("resume.html")
        
        themes = ["professional", "modern", "minimal", "tech"]
        for theme in themes:
            config = HTMLConfig(theme=theme)
            html = template.render(
                config=config,
                contact=ContactInfo(name="Test", email="test@test.com")
            )
            assert f"styles/themes/{theme}.css" in html


class TestHTMLGeneratorIntegration:
    """Test HTML generator integration with new template structure."""
    
    @pytest.fixture
    def html_generator(self) -> HTMLGenerator:
        """Create HTML generator instance."""
        return HTMLGenerator()
    
    @pytest.fixture
    def sample_resume(self) -> ResumeData:
        """Create sample resume for testing."""
        return ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane@example.com",
                phone="(555) 123-9876",
                location="New York, NY"
            ),
            summary="Software developer with 5 years of experience.",
            experience=[],
            education=[],
            skills=Skills(raw_skills=["Python", "SQL"])
        )
    
    def test_html_generator_with_themes(self, html_generator: HTMLGenerator, sample_resume: ResumeData, tmp_path: Path):
        """Test HTML generator works with different themes."""
        themes = ["professional", "modern", "minimal", "tech"]
        
        for theme in themes:
            html_generator.config.theme = theme
            output_path = tmp_path / f"resume_{theme}.html"
            
            html_content = html_generator.generate(sample_resume, output_path)
            
            assert output_path.exists()
            assert f"styles/themes/{theme}.css" in html_content
            assert "Jane Smith" in html_content
    
    def test_html_generator_custom_css(self, html_generator: HTMLGenerator, sample_resume: ResumeData):
        """Test HTML generator with custom CSS."""
        custom_css = """
        .custom-class {
            color: blue;
        }
        """
        
        html_generator.config.custom_css = custom_css
        html_content = html_generator.generate(sample_resume)
        
        # Check for key parts of the custom CSS rather than exact string match
        assert ".custom-class" in html_content
        assert "color: blue" in html_content
        assert "<style>" in html_content
    
    def test_html_generator_template_context(self, html_generator: HTMLGenerator, sample_resume: ResumeData):
        """Test that HTML generator passes correct context to templates."""
        with patch.object(html_generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_get_template.return_value = mock_template
            mock_template.render.return_value = "<html>Test</html>"
            
            html_generator.generate(sample_resume)
            
            # Verify template was called with correct context
            mock_template.render.assert_called_once()
            context = mock_template.render.call_args[1]
            
            assert context["contact"] == sample_resume.contact
            assert context["summary"] == sample_resume.summary
            assert context["theme"] == "professional"  # default theme
            assert context["has_summary"] is True


class TestTemplateComponents:
    """Test individual template components."""
    
    @pytest.fixture
    def component_env(self) -> Environment:
        """Create environment for component testing."""
        template_dir = Path(__file__).parent.parent
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def test_header_component(self, component_env: Environment):
        """Test header component renders correctly."""
        template = component_env.get_template("components/header.html")
        
        contact = ContactInfo(
            name="Test User",
            email="test@example.com",
            phone="123-456-7890",
            location="Test City, ST"
        )
        
        html = template.render(contact=contact)
        
        assert "Test User" in html
        assert "test@example.com" in html
        assert "123-456-7890" in html
        assert "Test City, ST" in html
    
    def test_experience_component(self, component_env: Environment):
        """Test experience component renders correctly."""
        template = component_env.get_template("components/experience.html")
        
        experience = [
            Experience(
                title="Software Engineer",
                company="Test Company",
                location="Remote",
                start_date="2022-01",
                end_date="Present",
                bullets=["Did something", "Did another thing"]
            )
        ]
        
        html = template.render(experience=experience)
        
        assert "Software Engineer" in html
        assert "Test Company" in html
        assert "Remote" in html
        assert "Did something" in html
        assert "Did another thing" in html
    
    def test_skills_component(self, component_env: Environment):
        """Test skills component renders correctly."""
        template = component_env.get_template("components/skills.html")
        
        skills = Skills(
            categories=[
                {"name": "Programming", "skills": ["Python", "Java"]},
                {"name": "Tools", "skills": ["Git", "Docker"]}
            ]
        )
        
        html = template.render(skills=skills)
        
        assert "Programming" in html
        assert "Python" in html
        assert "Java" in html
        assert "Tools" in html
        assert "Git" in html
        assert "Docker" in html


class TestTemplateAccessibility:
    """Test template accessibility features."""
    
    @pytest.fixture
    def template_env(self) -> Environment:
        """Create template environment."""
        template_dir = Path(__file__).parent.parent
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def test_semantic_html_structure(self, template_env: Environment):
        """Test templates use semantic HTML."""
        template = template_env.get_template("resume.html")
        html = template.render(
            contact=ContactInfo(name="Test", email="test@test.com"),
            config=HTMLConfig(),
            summary="Test summary",
            experience=[],
            education=[],
            skills=Skills(raw_skills=[]),
            projects=[],
            certifications=[],
            has_projects=False,
            has_certifications=False,
            has_summary=True
        )
        
        # Check semantic elements
        assert '<main' in html
        assert '<header' in html
        assert '<section' in html
        assert 'role="main"' in html
        assert 'aria-label' in html
    
    def test_skip_navigation(self, template_env: Environment):
        """Test skip navigation link exists."""
        template = template_env.get_template("base.html")
        html = template.render()
        
        assert 'Skip to main content' in html
        assert 'sr-only' in html
        assert '#main-content' in html


class TestTemplateValidation:
    """Test template HTML validation."""
    
    def test_valid_html5_structure(self):
        """Test that generated HTML follows HTML5 standards."""
        generator = HTMLGenerator()
        resume_data = ResumeData(
            contact=ContactInfo(
                name="Validator Test",
                email="valid@test.com"
            )
        )
        
        html = generator.generate(resume_data)
        
        # Basic HTML5 validation checks
        assert html.startswith('<!DOCTYPE html>')
        assert '<html lang="en"' in html
        assert '<meta charset="UTF-8">' in html
        assert '<meta name="viewport"' in html
        
        # Validate the output
        assert generator.validate_output(html)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])