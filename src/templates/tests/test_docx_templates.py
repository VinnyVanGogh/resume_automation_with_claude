"""
Tests for DOCX template system functionality.

This module contains comprehensive tests for DOCX template configuration,
style loading, validation, and template variation testing.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from src.generator.docx_generator import DOCXGenerator
from src.generator.config import DOCXConfig
from src.models import ResumeData, ContactInfo


class TestDOCXTemplateSystem:
    """Test cases for DOCX template system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.templates_dir = Path(__file__).parent.parent / "docx"
        self.styles_path = self.templates_dir / "styles.yaml"
        self.templates_path = self.templates_dir / "templates.yaml"
        
        # Sample resume data for testing
        self.sample_resume = ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="john.doe@example.com",
                phone="(555) 123-4567",
                location="New York, NY"
            ),
            summary="Experienced software engineer with 5+ years in full-stack development."
        )
    
    def test_styles_yaml_exists(self):
        """Test that styles.yaml file exists."""
        assert self.styles_path.exists(), f"styles.yaml not found at {self.styles_path}"
    
    def test_templates_yaml_exists(self):
        """Test that templates.yaml file exists."""
        assert self.templates_path.exists(), f"templates.yaml not found at {self.templates_path}"
    
    def test_styles_yaml_validity(self):
        """Test that styles.yaml is valid YAML."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        assert isinstance(styles_config, dict), "styles.yaml should contain a dictionary"
        assert 'document' in styles_config, "styles.yaml should have 'document' section"
        assert 'paragraph_styles' in styles_config, "styles.yaml should have 'paragraph_styles' section"
        assert 'themes' in styles_config, "styles.yaml should have 'themes' section"
    
    def test_templates_yaml_validity(self):
        """Test that templates.yaml is valid YAML."""
        with open(self.templates_path, 'r') as f:
            templates_config = yaml.safe_load(f)
        
        assert isinstance(templates_config, dict), "templates.yaml should contain a dictionary"
        assert 'templates' in templates_config, "templates.yaml should have 'templates' section"
        assert 'sections' in templates_config, "templates.yaml should have 'sections' section"
    
    def test_required_paragraph_styles(self):
        """Test that all required paragraph styles are defined."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        paragraph_styles = styles_config.get('paragraph_styles', {})
        required_styles = ['Normal', 'Heading1', 'Heading2', 'Heading3', 'BulletList', 'ContactInfo']
        
        for style in required_styles:
            assert style in paragraph_styles, f"Required style '{style}' not found in paragraph_styles"
    
    def test_required_themes(self):
        """Test that all required themes are defined."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        themes = styles_config.get('themes', {})
        required_themes = ['professional', 'modern', 'minimal', 'tech']
        
        for theme in required_themes:
            assert theme in themes, f"Required theme '{theme}' not found in themes"
    
    def test_required_templates(self):
        """Test that all required templates are defined."""
        with open(self.templates_path, 'r') as f:
            templates_config = yaml.safe_load(f)
        
        templates = templates_config.get('templates', {})
        required_templates = ['professional', 'modern', 'minimal', 'tech']
        
        for template in required_templates:
            assert template in templates, f"Required template '{template}' not found in templates"
    
    def test_document_configuration(self):
        """Test document configuration structure."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        document = styles_config.get('document', {})
        assert 'page_size' in document, "Document should specify page_size"
        assert 'margins' in document, "Document should specify margins"
        
        margins = document.get('margins', {})
        required_margins = ['top', 'bottom', 'left', 'right']
        for margin in required_margins:
            assert margin in margins, f"Margin '{margin}' not specified"
    
    def test_ats_compliance_settings(self):
        """Test ATS compliance configuration."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        ats_compliance = styles_config.get('ats_compliance', {})
        assert isinstance(ats_compliance, dict), "ATS compliance should be a dictionary"
        
        required_settings = ['use_simple_fonts', 'avoid_graphics', 'use_standard_headings']
        for setting in required_settings:
            assert setting in ats_compliance, f"ATS setting '{setting}' not found"
    
    def test_font_specifications(self):
        """Test that font specifications are valid."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        fonts = styles_config.get('fonts', {})
        assert 'primary' in fonts, "Primary font should be specified"
        
        # Check that primary font is ATS-compliant
        primary_font = fonts.get('primary', '')
        ats_fonts = ['Arial', 'Calibri', 'Times New Roman', 'Helvetica']
        assert primary_font in ats_fonts, f"Primary font '{primary_font}' should be ATS-compliant"
    
    def test_theme_font_consistency(self):
        """Test that theme fonts are consistent and valid."""
        with open(self.styles_path, 'r') as f:
            styles_config = yaml.safe_load(f)
        
        themes = styles_config.get('themes', {})
        for theme_name, theme_config in themes.items():
            if 'fonts' in theme_config and 'primary' in theme_config['fonts']:
                font = theme_config['fonts']['primary']
                assert isinstance(font, str), f"Theme {theme_name} font should be a string"
                assert len(font) > 0, f"Theme {theme_name} font should not be empty"


class TestDOCXGeneratorTemplateIntegration:
    """Test DOCX generator integration with template system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_resume = ResumeData(
            contact=ContactInfo(
                name="Jane Smith",
                email="jane.smith@example.com",
                phone="(555) 987-6543",
                location="San Francisco, CA"
            ),
            summary="Senior software engineer with expertise in full-stack development."
        )
    
    def test_generator_loads_styles_config(self):
        """Test that generator loads styles configuration."""
        generator = DOCXGenerator(template_name="professional")
        
        assert hasattr(generator, 'styles_config'), "Generator should have styles_config attribute"
        assert isinstance(generator.styles_config, dict), "styles_config should be a dictionary"
    
    def test_generator_loads_template_config(self):
        """Test that generator loads template configuration."""
        generator = DOCXGenerator(template_name="professional")
        
        assert hasattr(generator, 'template_config'), "Generator should have template_config attribute"
        assert isinstance(generator.template_config, dict), "template_config should be a dictionary"
    
    def test_template_selection(self):
        """Test template selection functionality."""
        templates = ['professional', 'modern', 'minimal', 'tech']
        
        for template in templates:
            generator = DOCXGenerator(template_name=template)
            assert generator.template_name == template, f"Template name should be set to {template}"
    
    def test_invalid_template_handling(self):
        """Test handling of invalid template names."""
        # Should not raise an error, but use default fallback
        generator = DOCXGenerator(template_name="nonexistent")
        assert generator.template_name == "nonexistent"  # Stores name even if invalid
    
    def test_docx_generation_with_different_templates(self):
        """Test DOCX generation with different templates."""
        templates = ['professional', 'modern', 'minimal', 'tech']
        
        for template in templates:
            generator = DOCXGenerator(template_name=template)
            docx_bytes = generator.generate(self.sample_resume)
            
            assert isinstance(docx_bytes, bytes), f"Template {template} should generate bytes"
            assert len(docx_bytes) > 1000, f"Template {template} should generate substantial content"
            assert docx_bytes.startswith(b'PK'), f"Template {template} should generate valid DOCX"
    
    def test_style_configuration_application(self):
        """Test that style configuration is applied correctly."""
        generator = DOCXGenerator(template_name="professional")
        
        # Generate document to trigger style application
        docx_bytes = generator.generate(self.sample_resume)
        
        # Basic validation that styles were applied
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000
    
    def test_fallback_to_config_when_yaml_missing(self):
        """Test fallback behavior when YAML files are missing."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = FileNotFoundError("No such file")
            
            # Should not raise an error, should use config defaults
            generator = DOCXGenerator()
            assert generator.styles_config == {}
            assert generator.template_config == {}
    
    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            # Should not raise an error, should use empty config
            generator = DOCXGenerator()
            assert generator.styles_config == {}
            assert generator.template_config == {}


class TestDOCXTemplateValidation:
    """Test DOCX template validation and quality assurance."""
    
    def test_professional_template_validation(self):
        """Test professional template meets quality standards."""
        generator = DOCXGenerator(template_name="professional")
        
        # Check that required configurations are loaded
        assert 'paragraph_styles' in generator.styles_config
        assert 'themes' in generator.styles_config
        assert 'professional' in generator.styles_config.get('themes', {})
    
    def test_modern_template_validation(self):
        """Test modern template meets quality standards."""
        generator = DOCXGenerator(template_name="modern")
        
        # Check that theme-specific config exists
        themes = generator.styles_config.get('themes', {})
        if 'modern' in themes:
            modern_theme = themes['modern']
            assert 'colors' in modern_theme or 'fonts' in modern_theme
    
    def test_minimal_template_validation(self):
        """Test minimal template meets quality standards."""
        generator = DOCXGenerator(template_name="minimal")
        
        # Should still have all required styles
        styles = generator.styles_config.get('paragraph_styles', {})
        required_styles = ['Normal', 'Heading1', 'Heading2']
        for style in required_styles:
            assert style in styles
    
    def test_tech_template_validation(self):
        """Test tech template meets quality standards."""
        generator = DOCXGenerator(template_name="tech")
        
        # Should have appropriate font choices for tech roles
        themes = generator.styles_config.get('themes', {})
        if 'tech' in themes:
            tech_theme = themes['tech']
            # Tech theme might use different fonts like Consolas
            assert isinstance(tech_theme, dict)
    
    def test_template_consistency(self):
        """Test that all templates have consistent structure."""
        templates = ['professional', 'modern', 'minimal', 'tech']
        
        for template_name in templates:
            generator = DOCXGenerator(template_name=template_name)
            
            # All templates should be able to generate basic resume
            sample_resume = ResumeData(
                contact=ContactInfo(name="Test User", email="test@example.com")
            )
            
            docx_bytes = generator.generate(sample_resume)
            assert isinstance(docx_bytes, bytes)
            assert len(docx_bytes) > 500  # Should generate some content
    
    def test_ats_compliance_validation(self):
        """Test that templates maintain ATS compliance."""
        generator = DOCXGenerator(template_name="professional")
        
        ats_config = generator.styles_config.get('ats_compliance', {})
        
        # Should have ATS compliance settings
        assert 'use_simple_fonts' in ats_config
        assert 'avoid_graphics' in ats_config
        assert 'use_standard_headings' in ats_config
        
        # ATS settings should be enabled
        assert ats_config.get('use_simple_fonts', False) is True
        assert ats_config.get('avoid_graphics', False) is True
    
    def test_template_performance(self):
        """Test template loading and generation performance."""
        import time
        
        start_time = time.time()
        generator = DOCXGenerator(template_name="professional")
        load_time = time.time() - start_time
        
        # Template loading should be fast
        assert load_time < 1.0, f"Template loading took {load_time:.2f}s, should be < 1s"
        
        sample_resume = ResumeData(
            contact=ContactInfo(name="Performance Test", email="test@example.com")
        )
        
        start_time = time.time()
        docx_bytes = generator.generate(sample_resume)
        generation_time = time.time() - start_time
        
        # Generation should be reasonably fast
        assert generation_time < 3.0, f"Generation took {generation_time:.2f}s, should be < 3s"
        assert len(docx_bytes) > 1000


class TestDOCXTemplateErrorHandling:
    """Test error handling in DOCX template system."""
    
    def test_missing_styles_file_handling(self):
        """Test handling when styles.yaml is missing."""
        with patch('builtins.open', side_effect=FileNotFoundError("No such file")):
            generator = DOCXGenerator()
            # Should not raise an error and should fallback to empty config
            assert generator.styles_config == {}
    
    def test_corrupted_yaml_handling(self):
        """Test handling of corrupted YAML files."""
        corrupted_yaml = "invalid: yaml: content: ["
        
        with patch('builtins.open', mock_open(read_data=corrupted_yaml)):
            generator = DOCXGenerator()
            # Should handle gracefully
            assert generator.styles_config == {}
    
    def test_partial_config_handling(self):
        """Test handling of partial configuration files."""
        partial_config = """
        document:
          page_size: "Letter"
        # Missing other sections
        """
        
        with patch('builtins.open', mock_open(read_data=partial_config)):
            generator = DOCXGenerator()
            # Should handle partial config gracefully
            assert isinstance(generator.styles_config, dict)
    
    def test_generation_with_missing_config(self):
        """Test document generation with missing template config."""
        generator = DOCXGenerator()
        generator.styles_config = {}  # Simulate missing config
        generator.template_config = {}
        
        sample_resume = ResumeData(
            contact=ContactInfo(name="Test User", email="test@example.com")
        )
        
        # Should still generate a document using fallback styles
        docx_bytes = generator.generate(sample_resume)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 500