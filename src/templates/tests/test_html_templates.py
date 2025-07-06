"""
Test suite for HTML template structure and functionality.

Tests template inheritance, component rendering, accessibility,
and integration with resume data models.
"""

import pytest
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models import ResumeData, ContactInfo, Experience, Education, Skills, SkillCategory


class TestTemplateStructure:
    """Test template file structure and inheritance."""
    
    @pytest.fixture
    def template_env(self):
        """Create Jinja2 environment for template testing."""
        template_dir = Path(__file__).parent.parent
        return Environment(loader=FileSystemLoader(str(template_dir)))
    
    def test_base_template_exists(self, template_env):
        """Test that base.html template exists and loads."""
        try:
            template = template_env.get_template('base.html')
            assert template is not None
        except TemplateNotFound:
            pytest.fail("base.html template not found")
    
    def test_resume_template_exists(self, template_env):
        """Test that resume.html template exists and loads."""
        try:
            template = template_env.get_template('resume.html')
            assert template is not None
        except TemplateNotFound:
            pytest.fail("resume.html template not found")
    
    def test_component_templates_exist(self, template_env):
        """Test that all component templates exist."""
        components = [
            'components/header.html',
            'components/summary.html', 
            'components/experience.html',
            'components/education.html',
            'components/skills.html'
        ]
        
        for component in components:
            try:
                template = template_env.get_template(component)
                assert template is not None
            except TemplateNotFound:
                pytest.fail(f"Component template {component} not found")


class TestTemplateRendering:
    """Test template rendering with sample data."""
    
    @pytest.fixture
    def template_env(self):
        """Create Jinja2 environment for template testing."""
        template_dir = Path(__file__).parent.parent
        return Environment(loader=FileSystemLoader(str(template_dir)))
    
    @pytest.fixture
    def sample_resume_data(self):
        """Create real resume data for testing based on Vince's resume."""
        contact = ContactInfo(
            name="Vince Vasile",
            email="VinceVasile@vinny-van-gogh.com",
            phone=None,
            linkedin="https://linkedin.com/in/vincevasile",
            github="https://github.com/VinnyVanGogh",
            website=None,
            location="San Francisco, California"
        )
        
        experience = [
            Experience(
                title="RPA & Automation Engineer",
                company="Managed Solution",
                start_date="Nov 2024",
                end_date="Present",
                location="Remote",
                bullets=[
                    "Architected enterprise-scale multi-tenant SaaS platform with Django, React, Ruby on Rails, and FastAPI microservices",
                    "Implemented Microsoft Azure AD authentication with MSAL integration and comprehensive user management",
                    "Created advanced systems integration framework connecting ConnectWise, Asio RMM, and business-critical platforms"
                ]
            ),
            Experience(
                title="IT Systems Engineer III",
                company="VC3",
                start_date="Sep 2023",
                end_date="Nov 2024",
                location="Remote",
                bullets=[
                    "Enhanced IT infrastructure through custom Python, PowerShell, and Bash automation scripts, reducing manual tasks by 50%",
                    "Engineered comprehensive network security protocols integrating Sentinel One, CrowdStrike, and Cisco Umbrella",
                    "Led network configuration standardization across Cisco, Meraki, and HP platforms"
                ]
            )
        ]
        
        skills = Skills(
            categories=[
                SkillCategory(
                    name="Languages",
                    skills=["TypeScript", "JavaScript", "Python", "SQL", "Bash", "PowerShell"]
                ),
                SkillCategory(
                    name="Frontend", 
                    skills=["React", "React Native", "Svelte", "Expo SDK", "Tailwind CSS", "Radix UI"]
                ),
                SkillCategory(
                    name="Backend",
                    skills=["Node.js", "FastAPI", "Django", "Ruby on Rails", "PostgreSQL", "Redis"]
                ),
                SkillCategory(
                    name="AI/ML",
                    skills=["Multi-LLM coordination (Claude, Gemini, OpenAI)", "MCP architecture", "prompt engineering", "RAG systems"]
                )
            ]
        )
        
        return ResumeData(
            contact=contact,
            summary="Applied AI Engineer with 261+ AI development sessions building production-grade LLM-powered applications. Specialized in context-aware AI systems, multi-LLM coordination, and AI-augmented developer workflows.",
            experience=experience,
            education=[],  # No education section in the resume
            skills=skills
        )
    
    def test_resume_template_renders(self, template_env, sample_resume_data):
        """Test that resume template renders without errors."""
        template = template_env.get_template('resume.html')
        
        # Convert ResumeData to template context
        context = {
            'contact': sample_resume_data.contact,
            'summary': sample_resume_data.summary,
            'experience': sample_resume_data.experience,
            'education': sample_resume_data.education,
            'skills': sample_resume_data.skills,
            'projects': None,
            'certifications': None,
            'has_summary': bool(sample_resume_data.summary),
            'has_projects': False,
            'has_certifications': False,
            'config': {'include_styles': True}
        }
        
        try:
            rendered = template.render(**context)
            assert len(rendered) > 0
            assert 'Vince Vasile' in rendered
        except Exception as e:
            pytest.fail(f"Template rendering failed: {e}")
    
    def test_contact_info_renders_correctly(self, template_env, sample_resume_data):
        """Test that contact information renders correctly."""
        template = template_env.get_template('resume.html')
        
        context = {
            'contact': sample_resume_data.contact,
            'summary': None,
            'experience': [],
            'education': [],
            'skills': None,
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        # Check that contact info is present
        assert 'Vince Vasile' in rendered
        assert 'VinceVasile@vinny-van-gogh.com' in rendered
        assert 'linkedin.com/in/vincevasile' in rendered
        assert 'github.com/VinnyVanGogh' in rendered
        assert 'San Francisco, California' in rendered
    
    def test_experience_section_renders(self, template_env, sample_resume_data):
        """Test that experience section renders correctly."""
        template = template_env.get_template('resume.html')
        
        context = {
            'contact': sample_resume_data.contact,
            'summary': None,
            'experience': sample_resume_data.experience,
            'education': [],
            'skills': None,
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        # Check experience content
        assert 'Experience' in rendered
        assert 'RPA & Automation Engineer' in rendered
        assert 'Managed Solution' in rendered
        assert 'Architected enterprise-scale multi-tenant SaaS platform' in rendered
    
    def test_education_section_does_not_render_when_empty(self, template_env, sample_resume_data):
        """Test that education section doesn't render when empty.""" 
        template = template_env.get_template('resume.html')
        
        context = {
            'contact': sample_resume_data.contact,
            'summary': None,
            'experience': [],
            'education': [],  # Empty education
            'skills': None,
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        # Education section should not appear when empty
        assert 'Education' not in rendered
    
    def test_skills_section_renders(self, template_env, sample_resume_data):
        """Test that skills section renders correctly."""
        template = template_env.get_template('resume.html')
        
        context = {
            'contact': sample_resume_data.contact,
            'summary': None,
            'experience': [],
            'education': [],
            'skills': sample_resume_data.skills,
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        # Check skills content
        assert 'Skills' in rendered
        assert 'Languages:' in rendered
        assert 'TypeScript' in rendered
        assert 'Python' in rendered
        assert 'AI/ML:' in rendered
        assert 'Multi-LLM coordination' in rendered
    
    def test_conditional_sections_work(self, template_env, sample_resume_data):
        """Test that sections only render when data is present."""
        template = template_env.get_template('resume.html')
        
        # Test with minimal data
        context = {
            'contact': sample_resume_data.contact,
            'summary': None,
            'experience': [],
            'education': [],
            'skills': None,
            'projects': None,
            'certifications': None,
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        # Should not contain section headers when no data
        assert 'Experience' not in rendered
        assert 'Education' not in rendered  
        assert 'Skills' not in rendered


class TestHTMLStructure:
    """Test HTML structure and semantic markup."""
    
    @pytest.fixture
    def template_env(self):
        """Create Jinja2 environment for template testing."""
        template_dir = Path(__file__).parent.parent
        return Environment(loader=FileSystemLoader(str(template_dir)))
    
    @pytest.fixture
    def minimal_context(self):
        """Minimal context for testing HTML structure."""
        return {
            'contact': ContactInfo(
                name="Test User",
                email="test@example.com"
            ),
            'config': {'include_styles': False}
        }
    
    def test_base_template_has_proper_html5_structure(self, template_env, minimal_context):
        """Test that base template has proper HTML5 structure."""
        template = template_env.get_template('resume.html')
        rendered = template.render(**minimal_context)
        
        # Check HTML5 structure
        assert '<!DOCTYPE html>' in rendered
        assert '<html lang="en"' in rendered
        assert '<meta charset="UTF-8">' in rendered
        assert '<meta name="viewport"' in rendered
    
    def test_semantic_html_elements_present(self, template_env, minimal_context):
        """Test that semantic HTML elements are used."""
        template = template_env.get_template('resume.html')
        rendered = template.render(**minimal_context)
        
        # Check semantic elements
        assert '<main' in rendered
        assert '<header' in rendered
        assert 'role="main"' in rendered
        assert 'role="banner"' in rendered
    
    def test_accessibility_features_present(self, template_env, minimal_context):
        """Test that accessibility features are present."""
        template = template_env.get_template('resume.html')
        rendered = template.render(**minimal_context)
        
        # Check accessibility features
        assert 'Skip to main content' in rendered
        assert 'aria-label' in rendered
        assert 'id="main-content"' in rendered
    
    def test_no_inline_styles_or_scripts(self, template_env, minimal_context):
        """Test that no inline styles or scripts are present (for ATS compliance)."""
        template = template_env.get_template('resume.html')
        rendered = template.render(**minimal_context)
        
        # Should not have inline styles (except in head)
        body_content = rendered.split('<body>')[1] if '<body>' in rendered else rendered
        
        # Allow structured data script in head but no inline styles in body
        assert '<style>' not in body_content
        assert 'style=' not in body_content


class TestAccessibility:
    """Test accessibility compliance of templates."""
    
    @pytest.fixture
    def template_env(self):
        """Create Jinja2 environment for template testing."""
        template_dir = Path(__file__).parent.parent
        return Environment(loader=FileSystemLoader(str(template_dir)))
    
    def test_heading_hierarchy(self, template_env):
        """Test that heading hierarchy is logical."""
        template = template_env.get_template('resume.html')
        
        context = {
            'contact': ContactInfo(name="Test User", email="test@example.com"),
            'summary': "Test summary",
            'experience': [Experience(
                title="Test Job", 
                company="Test Corp",
                start_date="2020",
                end_date="2021",
                bullets=["Test bullet"]
            )],
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        # Check heading hierarchy (h1 -> h2 -> h3)
        assert '<h1' in rendered  # Name
        assert '<h2' in rendered  # Section headers
        assert '<h3' in rendered  # Job titles
    
    def test_skip_navigation_present(self, template_env):
        """Test that skip navigation is present for screen readers."""
        template = template_env.get_template('resume.html')
        
        context = {
            'contact': ContactInfo(name="Test User", email="test@example.com"),
            'config': {'include_styles': False}
        }
        
        rendered = template.render(**context)
        
        assert 'Skip to main content' in rendered
        assert 'href="#main-content"' in rendered
        assert 'sr-only' in rendered