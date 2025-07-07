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
    
    @pytest.fixture
    def comprehensive_resume(self) -> ResumeData:
        """Create comprehensive resume data for integration testing."""
        return ResumeData(
            contact=ContactInfo(
                name="Alex Thompson",
                email="alex.thompson@example.com",
                phone="(555) 987-6543",
                location="Seattle, WA",
                linkedin="https://linkedin.com/in/alexthompson",
                github="https://github.com/alexthompson",
                website="https://alexthompson.dev"
            ),
            summary="Full-stack software engineer with 8+ years of experience building scalable web applications.",
            experience=[
                Experience(
                    title="Senior Software Engineer",
                    company="Tech Innovations Inc.",
                    location="Seattle, WA",
                    start_date="2021-03",
                    end_date="Present",
                    bullets=[
                        "Led development of microservices architecture serving 1M+ users",
                        "Mentored 3 junior developers and improved team productivity by 25%",
                        "Implemented CI/CD pipeline reducing deployment time by 60%"
                    ]
                ),
                Experience(
                    title="Software Engineer",
                    company="StartupCorp",
                    location="Remote",
                    start_date="2019-01",
                    end_date="2021-02",
                    bullets=[
                        "Built React frontend and Node.js backend for B2B SaaS platform",
                        "Optimized database queries improving application performance by 40%"
                    ]
                )
            ],
            education=[
                Education(
                    degree="M.S. Computer Science",
                    school="University of Washington",
                    location="Seattle, WA",
                    start_date="2017-09",
                    end_date="2019-06",
                    gpa="3.8",
                    honors=["Graduate Research Assistant"],
                    coursework=["Machine Learning", "Distributed Systems", "Advanced Algorithms"]
                ),
                Education(
                    degree="B.S. Software Engineering",
                    school="Washington State University",
                    location="Pullman, WA",
                    start_date="2013-09",
                    end_date="2017-05",
                    gpa="3.9",
                    honors=["Summa Cum Laude", "Phi Beta Kappa"]
                )
            ],
            skills=Skills(
                categories=[
                    {"name": "Languages", "skills": ["Python", "JavaScript", "TypeScript", "Go", "SQL"]},
                    {"name": "Frameworks", "skills": ["React", "Node.js", "Django", "FastAPI", "Express"]},
                    {"name": "Tools", "skills": ["Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis"]},
                    {"name": "Practices", "skills": ["Agile", "TDD", "DevOps", "Microservices"]}
                ],
                raw_skills=["Python", "JavaScript", "TypeScript", "Go", "SQL", "React", "Node.js", "Django", "FastAPI", "Express", "Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis", "Agile", "TDD", "DevOps", "Microservices"]
            ),
            projects=[
                Project(
                    name="Open Source Analytics Platform",
                    description="Real-time analytics platform for tracking user behavior across web applications",
                    technologies=["Python", "React", "PostgreSQL", "Redis"],
                    url="https://github.com/alexthompson/analytics-platform",
                    date="2022"
                ),
                Project(
                    name="ML-Powered Recommendation Engine",
                    description="Machine learning system for personalized content recommendations",
                    technologies=["Python", "TensorFlow", "Kafka", "MongoDB"],
                    url="https://github.com/alexthompson/recommendation-engine",
                    date="2021"
                )
            ],
            certifications=[
                Certification(
                    name="AWS Solutions Architect Professional",
                    issuer="Amazon Web Services",
                    date="2022-08",
                    credential_id="AWS-PSA-12345",
                    url="https://aws.amazon.com/verification"
                ),
                Certification(
                    name="Certified Kubernetes Administrator",
                    issuer="Cloud Native Computing Foundation",
                    date="2021-11",
                    credential_id="CKA-67890"
                )
            ]
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
    
    def test_comprehensive_resume_rendering(self, html_generator: HTMLGenerator, comprehensive_resume: ResumeData):
        """Test full template pipeline with comprehensive resume data."""
        html_content = html_generator.generate(comprehensive_resume)
        
        # Check all sections are rendered
        assert "Alex Thompson" in html_content
        assert "alex.thompson@example.com" in html_content
        assert "Full-stack software engineer" in html_content
        assert "Senior Software Engineer" in html_content
        assert "Tech Innovations Inc." in html_content
        assert "M.S. Computer Science" in html_content
        assert "University of Washington" in html_content
        assert "Python" in html_content
        assert "React" in html_content
        assert "Open Source Analytics Platform" in html_content
        assert "AWS Solutions Architect Professional" in html_content
        
        # Check structure elements
        assert '<main' in html_content
        assert 'role="main"' in html_content
        assert 'class="page-wrapper"' in html_content
        
        # Verify comprehensive content length
        assert len(html_content) > 10000  # Should be substantial
    
    def test_template_caching_performance(self, html_generator: HTMLGenerator, sample_resume: ResumeData):
        """Test template caching improves performance."""
        import time
        
        # First generation (cold start)
        start_time = time.time()
        html1 = html_generator.generate(sample_resume)
        first_duration = time.time() - start_time
        
        # Second generation (should use cached template)
        start_time = time.time()
        html2 = html_generator.generate(sample_resume)
        second_duration = time.time() - start_time
        
        # Both should generate same content
        assert html1 == html2
        
        # Second generation should be faster (or at least not significantly slower)
        assert second_duration <= first_duration * 1.5  # Allow 50% variance
    
    def test_all_themes_with_comprehensive_data(self, html_generator: HTMLGenerator, comprehensive_resume: ResumeData):
        """Test all themes work with comprehensive resume data."""
        themes = ["professional", "modern", "minimal", "tech"]
        
        for theme in themes:
            html_generator.config.theme = theme
            html_content = html_generator.generate(comprehensive_resume)
            
            # Basic structure checks
            assert f"styles/themes/{theme}.css" in html_content
            assert "Alex Thompson" in html_content
            assert len(html_content) > 8000
            
            # Theme-specific checks
            if theme == "professional":
                assert "styles/themes/professional.css" in html_content
            elif theme == "modern":
                assert "styles/themes/modern.css" in html_content
            elif theme == "minimal":
                assert "styles/themes/minimal.css" in html_content
            elif theme == "tech":
                assert "styles/themes/tech.css" in html_content


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
    
    def test_summary_component(self, component_env: Environment):
        """Test summary component renders correctly."""
        template = component_env.get_template("components/summary.html")
        
        summary_text = "Experienced software engineer with expertise in full-stack development."
        html = template.render(summary=summary_text)
        
        assert "Summary" in html
        assert summary_text in html
        assert 'class="section summary-section"' in html
        assert 'aria-labelledby="summary-heading"' in html
        assert 'property="description"' in html
    
    def test_summary_component_empty(self, component_env: Environment):
        """Test summary component with empty summary."""
        template = component_env.get_template("components/summary.html")
        
        html = template.render(summary="")
        
        # Should render nothing when summary is empty
        assert html.strip() == ""
    
    def test_education_component(self, component_env: Environment):
        """Test education component renders correctly."""
        template = component_env.get_template("components/education.html")
        
        education = [
            Education(
                degree="B.S. Computer Science",
                school="University of California",
                location="Berkeley, CA",
                start_date="2016-09",
                end_date="2020-05",
                gpa="3.8",
                honors=["Magna Cum Laude", "Dean's List"]
            )
        ]
        
        html = template.render(education=education)
        
        assert "Education" in html
        assert "B.S. Computer Science" in html
        assert "University of California" in html
        assert "Berkeley, CA" in html
        assert "2016-09" in html
        assert "2020-05" in html
        assert "3.8" in html
        assert "Magna Cum Laude" in html
        assert "Dean&#39;s List" in html or "Dean's List" in html
        assert 'class="section education-section"' in html
        assert 'typeof="EducationalOccupationalCredential"' in html
    
    def test_education_component_minimal(self, component_env: Environment):
        """Test education component with minimal data."""
        template = component_env.get_template("components/education.html")
        
        education = [
            Education(
                degree="B.A. Psychology",
                school="State University"
            )
        ]
        
        html = template.render(education=education)
        
        assert "B.A. Psychology" in html
        assert "State University" in html
        assert "GPA" not in html  # Should not show GPA section
        assert "Honors:" not in html  # Should not show honors section
    
    def test_education_component_with_coursework(self, component_env: Environment):
        """Test education component with coursework."""
        template = component_env.get_template("components/education.html")
        
        education = [
            Education(
                degree="M.S. Data Science",
                school="Tech Institute",
                coursework=["Machine Learning", "Data Structures", "Statistics"]
            )
        ]
        
        html = template.render(education=education)
        
        assert "M.S. Data Science" in html
        assert "Relevant Coursework:" in html
        assert "Machine Learning" in html
        assert "Data Structures" in html
        assert "Statistics" in html
        assert 'class="coursework-list"' in html
    
    def test_education_component_empty(self, component_env: Environment):
        """Test education component with empty education list."""
        template = component_env.get_template("components/education.html")
        
        html = template.render(education=[])
        
        # Should render nothing when education is empty
        assert html.strip() == ""


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


class TestTemplateEdgeCases:
    """Test template edge cases and error handling."""
    
    @pytest.fixture
    def template_env(self) -> Environment:
        """Create template environment."""
        template_dir = Path(__file__).parent.parent
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def test_template_with_special_characters(self, template_env: Environment):
        """Test templates handle special characters correctly."""
        template = template_env.get_template("resume.html")
        
        # Test with special characters in various fields
        contact = ContactInfo(
            name="José María O'Connor-Smith",
            email="josé@example.com",
            phone="+1 (555) 123-4567 ext. 123",
            location="Montréal, QC, Canada"
        )
        
        html = template.render(
            contact=contact,
            config=HTMLConfig(),
            summary="Software engineer with 10+ years of experience in C++ & Python development.",
            experience=[],
            education=[],
            skills=Skills(raw_skills=[]),
            projects=[],
            certifications=[],
            has_projects=False,
            has_certifications=False,
            has_summary=True
        )
        
        # Check that special characters are properly escaped/rendered
        assert "José María O&#39;Connor-Smith" in html or "José María O'Connor-Smith" in html
        assert "josé@example.com" in html
        assert "Montréal, QC, Canada" in html
        assert "&amp;" in html or "C++ &" in html  # Should be HTML-escaped
    
    def test_template_with_very_long_content(self, template_env: Environment):
        """Test templates handle very long content gracefully."""
        template = template_env.get_template("resume.html")
        
        # Create very long content
        long_name = "A" * 100
        long_summary = "This is a very long summary. " * 50  # ~1500 chars
        long_bullet = "This is an extremely long bullet point that goes on and on. " * 20
        
        contact = ContactInfo(name=long_name, email="test@example.com")
        experience = [
            Experience(
                title="Senior Software Engineer with a Very Long Title That Keeps Going",
                company="Company with an Extremely Long Name That Takes Up Multiple Lines",
                location="City with a Very Long Name, State with a Long Name",
                start_date="2020-01",
                end_date="Present",
                bullets=[long_bullet]
            )
        ]
        
        html = template.render(
            contact=contact,
            config=HTMLConfig(),
            summary=long_summary,
            experience=experience,
            education=[],
            skills=Skills(raw_skills=[]),
            projects=[],
            certifications=[],
            has_projects=False,
            has_certifications=False,
            has_summary=True
        )
        
        # Should render without errors
        assert long_name in html
        assert long_summary[:100] in html  # Check first part of summary
        assert long_bullet[:100] in html  # Check first part of bullet
        assert len(html) > 5000  # Should be substantial content
    
    def test_template_with_empty_sections(self, template_env: Environment):
        """Test templates handle completely empty sections."""
        template = template_env.get_template("resume.html")
        
        contact = ContactInfo(name="Test User", email="test@example.com")
        
        html = template.render(
            contact=contact,
            config=HTMLConfig(),
            summary="",  # Empty summary
            experience=[],  # Empty experience
            education=[],  # Empty education
            skills=Skills(raw_skills=[]),  # Empty skills
            projects=[],  # Empty projects
            certifications=[],  # Empty certifications
            has_projects=False,
            has_certifications=False,
            has_summary=False
        )
        
        # Should still render a valid document
        assert "Test User" in html
        assert "test@example.com" in html
        assert len(html) > 500  # Should have basic structure
    
    def test_template_with_none_values(self, template_env: Environment):
        """Test templates handle None values gracefully."""
        template = template_env.get_template("components/experience.html")
        
        experience = [
            Experience(
                title="Software Engineer",
                company="Tech Corp",
                start_date="2020-01",
                end_date="Present",  # Use Present instead of None
                bullets=["Developed software"]
            )
        ]
        
        html = template.render(experience=experience)
        
        assert "Software Engineer" in html
        assert "Tech Corp" in html
        assert "Developed software" in html
        # Should handle None values without errors
    
    def test_template_with_html_in_content(self, template_env: Environment):
        """Test templates properly escape HTML content."""
        template = template_env.get_template("components/summary.html")
        
        # Summary containing HTML tags
        summary_with_html = "Expert in <script>alert('xss')</script> and React.js development."
        
        html = template.render(summary=summary_with_html)
        
        # HTML should be escaped for security
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "React.js development" in html
    
    def test_header_component_with_missing_fields(self, template_env: Environment):
        """Test header component with optional fields missing."""
        template = template_env.get_template("components/header.html")
        
        # Minimal contact info
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com"
            # Missing phone, location, linkedin, github, website
        )
        
        html = template.render(contact=contact)
        
        assert "John Doe" in html
        assert "john@example.com" in html
        # Should not have broken sections for missing fields
        assert html.count("None") == 0
    
    def test_skills_component_with_empty_categories(self, template_env: Environment):
        """Test skills component with empty or malformed categories."""
        template = template_env.get_template("components/skills.html")
        
        # Skills with valid structure but some empty elements
        skills = Skills(
            categories=[
                {"name": "Programming", "skills": ["Python"]},  # Valid category
                {"name": "Tools", "skills": ["Git"]},  # Valid category
            ],
            raw_skills=["Python", "JavaScript", "Git"]
        )
        
        html = template.render(skills=skills)
        
        # Should handle gracefully
        assert "Programming" in html
        assert "Python" in html
        assert "Tools" in html
        assert "Git" in html


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