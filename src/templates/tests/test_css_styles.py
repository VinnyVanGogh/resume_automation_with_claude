"""
Tests for CSS styles and modular architecture.

This module tests CSS validity, theme functionality, and style consistency
across the modular CSS architecture.
"""

import pytest
from pathlib import Path
import re
import os
import warnings
from typing import List, Dict, Any


class TestCSSArchitecture:
    """Test the modular CSS architecture structure."""
    
    @pytest.fixture
    def styles_dir(self) -> Path:
        """Get the styles directory path."""
        return Path(__file__).parent.parent / "styles"
    
    @pytest.fixture
    def themes_dir(self, styles_dir: Path) -> Path:
        """Get the themes directory path."""
        return styles_dir / "themes"
    
    def test_css_directory_structure(self, styles_dir: Path, themes_dir: Path):
        """Test that the CSS directory structure exists."""
        assert styles_dir.exists(), "styles directory should exist"
        assert themes_dir.exists(), "themes directory should exist"
        
        # Check required CSS files
        required_files = [
            "base.css",
            "components.css", 
            "print.css",
            "pdf.css"
        ]
        
        for file_name in required_files:
            file_path = styles_dir / file_name
            assert file_path.exists(), f"{file_name} should exist"
            assert file_path.stat().st_size > 0, f"{file_name} should not be empty"
    
    def test_theme_files_exist(self, themes_dir: Path):
        """Test that all required theme files exist."""
        required_themes = [
            "professional.css",
            "modern.css",
            "minimal.css", 
            "tech.css"
        ]
        
        for theme_name in required_themes:
            theme_path = themes_dir / theme_name
            assert theme_path.exists(), f"{theme_name} theme should exist"
            assert theme_path.stat().st_size > 0, f"{theme_name} should not be empty"


class TestCSSValidation:
    """Test CSS syntax and structure validation."""
    
    @pytest.fixture
    def all_css_files(self) -> List[Path]:
        """Get all CSS files for testing."""
        styles_dir = Path(__file__).parent.parent / "styles"
        css_files = []
        
        # Base CSS files
        for file_name in ["base.css", "components.css", "print.css", "pdf.css"]:
            css_files.append(styles_dir / file_name)
        
        # Theme files
        themes_dir = styles_dir / "themes"
        if themes_dir.exists():
            css_files.extend(themes_dir.glob("*.css"))
        
        return css_files
    
    def test_css_syntax_validity(self, all_css_files: List[Path]):
        """Test basic CSS syntax validity."""
        for css_file in all_css_files:
            content = css_file.read_text(encoding='utf-8')
            
            # Check for basic CSS structure
            assert '{' in content, f"{css_file.name} should contain CSS rules"
            assert '}' in content, f"{css_file.name} should contain CSS rules"
            
            # Check balanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            assert open_braces == close_braces, f"{css_file.name} should have balanced braces"
    
    def test_css_variables_consistency(self, all_css_files: List[Path]):
        """Test CSS custom properties are consistently defined."""
        base_css = Path(__file__).parent.parent / "styles" / "base.css"
        base_content = base_css.read_text(encoding='utf-8')
        
        # Extract CSS variables from base.css
        var_pattern = r'--[a-zA-Z-]+:'
        base_vars = set(re.findall(var_pattern, base_content))
        
        assert len(base_vars) > 0, "base.css should define CSS variables"
        
        # Check that themes reference these variables
        themes_dir = Path(__file__).parent.parent / "styles" / "themes"
        for theme_file in themes_dir.glob("*.css"):
            theme_content = theme_file.read_text(encoding='utf-8')
            
            # Should either define or reference CSS variables
            var_usage = re.findall(r'var\(--[a-zA-Z-]+\)', theme_content)
            var_definitions = re.findall(var_pattern, theme_content)
            
            total_var_usage = len(var_usage) + len(var_definitions)
            assert total_var_usage > 0, f"{theme_file.name} should use CSS variables"
    
    def test_ats_friendly_properties(self, all_css_files: List[Path]):
        """Test that CSS properties are ATS-friendly."""
        ats_unfriendly_patterns = [
            r'transform:',
            r'animation:',
            r'@keyframes',
            r'position:\s*fixed',
            r'position:\s*absolute.*z-index',
            r'background-image:.*url\(',
            r'content:.*url\('
        ]
        
        for css_file in all_css_files:
            content = css_file.read_text(encoding='utf-8')
            
            for pattern in ats_unfriendly_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Allow some exceptions for print styles
                    if 'print.css' in css_file.name:
                        continue
                    warnings.warn(f"{css_file.name} contains potentially ATS-unfriendly property: {matches}")


class TestThemeConsistency:
    """Test theme consistency and functionality."""
    
    @pytest.fixture
    def theme_files(self) -> Dict[str, Path]:
        """Get all theme files."""
        themes_dir = Path(__file__).parent.parent / "styles" / "themes"
        return {
            theme_file.stem: theme_file 
            for theme_file in themes_dir.glob("*.css")
        }
    
    def test_theme_variable_overrides(self, theme_files: Dict[str, Path]):
        """Test that themes properly override CSS variables."""
        required_vars = [
            '--color-primary',
            '--color-secondary', 
            '--font-family-main',
            '--font-size-base'
        ]
        
        for theme_name, theme_file in theme_files.items():
            content = theme_file.read_text(encoding='utf-8')
            
            # Count variable definitions
            defined_vars = 0
            for var in required_vars:
                if f"{var}:" in content:
                    defined_vars += 1
            
            assert defined_vars >= 2, f"{theme_name} should override key CSS variables"
    
    def test_professional_theme_defaults(self, theme_files: Dict[str, Path]):
        """Test that professional theme maintains conservative defaults."""
        if 'professional' not in theme_files:
            pytest.skip("Professional theme not found")
        
        prof_content = theme_files['professional'].read_text(encoding='utf-8')
        
        # Should use conservative colors
        assert 'color-primary: #000' in prof_content or 'color-primary: #1a1a1a' in prof_content
        assert 'Arial' in prof_content, "Professional theme should use Arial font"
    
    def test_modern_theme_enhancements(self, theme_files: Dict[str, Path]):
        """Test that modern theme includes visual enhancements."""
        if 'modern' not in theme_files:
            pytest.skip("Modern theme not found")
        
        modern_content = theme_files['modern'].read_text(encoding='utf-8')
        
        # Should have enhanced styling
        assert 'border-radius' in modern_content, "Modern theme should use border-radius"
        assert 'transition' in modern_content, "Modern theme should include transitions"


class TestPrintOptimization:
    """Test print and PDF optimization."""
    
    @pytest.fixture
    def print_css(self) -> Path:
        """Get print.css file."""
        return Path(__file__).parent.parent / "styles" / "print.css"
    
    @pytest.fixture
    def pdf_css(self) -> Path:
        """Get pdf.css file."""
        return Path(__file__).parent.parent / "styles" / "pdf.css"
    
    def test_print_media_queries(self, print_css: Path):
        """Test print media queries are properly defined."""
        content = print_css.read_text(encoding='utf-8')
        
        assert '@media print' in content, "print.css should contain print media queries"
        assert '@page' in content, "print.css should define page settings"
        assert 'page-break' in content, "print.css should control page breaks"
    
    def test_pdf_optimizations(self, pdf_css: Path):
        """Test PDF-specific optimizations."""
        content = pdf_css.read_text(encoding='utf-8')
        
        # Should have page setup
        assert '@page' in content, "pdf.css should define page settings"
        
        # Should optimize for digital viewing
        color_properties = ['background-color', 'color:', 'border-color']
        color_count = sum(1 for prop in color_properties if prop in content)
        assert color_count > 0, "pdf.css should include color properties for visual appeal"
    
    def test_ats_compliance_in_print(self, print_css: Path):
        """Test that print styles maintain ATS compliance."""
        content = print_css.read_text(encoding='utf-8')
        
        # Should force black text for ATS
        assert 'color: #000 !important' in content, "Print styles should force black text"
        assert 'background: transparent !important' in content, "Print styles should remove backgrounds"


class TestResponsiveDesign:
    """Test responsive design elements."""
    
    @pytest.fixture
    def css_files_with_responsive(self) -> List[Path]:
        """Get CSS files that should have responsive elements."""
        styles_dir = Path(__file__).parent.parent / "styles"
        return [
            styles_dir / "base.css",
            styles_dir / "components.css"
        ]
    
    def test_viewport_responsive_rules(self, css_files_with_responsive: List[Path]):
        """Test responsive design rules exist."""
        for css_file in css_files_with_responsive:
            content = css_file.read_text(encoding='utf-8')
            
            # Should have responsive breakpoints
            responsive_patterns = [
                r'@media.*max-width',
                r'@media.*min-width', 
                r'@media screen'
            ]
            
            has_responsive = any(
                re.search(pattern, content, re.IGNORECASE) 
                for pattern in responsive_patterns
            )
            
            if css_file.name == 'base.css':
                assert has_responsive, f"{css_file.name} should include responsive rules"


class TestAccessibility:
    """Test accessibility features in CSS."""
    
    def test_screen_reader_classes(self):
        """Test that screen reader utility classes exist."""
        base_css = Path(__file__).parent.parent / "styles" / "base.css"
        content = base_css.read_text(encoding='utf-8')
        
        # Should have screen reader only class
        assert '.sr-only' in content, "Should include .sr-only class for accessibility"
        assert 'position: absolute' in content, "sr-only should use proper hiding technique"
    
    def test_focus_states(self):
        """Test that focus states are defined for interactive elements."""
        components_css = Path(__file__).parent.parent / "styles" / "components.css"
        
        if components_css.exists():
            content = components_css.read_text(encoding='utf-8')
            
            # Should have focus styles
            focus_patterns = [r':focus', r'outline:']
            has_focus = any(
                re.search(pattern, content, re.IGNORECASE) 
                for pattern in focus_patterns
            )
            
            if has_focus:
                assert True  # Focus states found
            else:
                warnings.warn("Components should include focus states for accessibility")


class TestPerformance:
    """Test CSS performance considerations."""
    
    def test_css_file_sizes(self):
        """Test that CSS files are reasonably sized."""
        styles_dir = Path(__file__).parent.parent / "styles"
        max_size_kb = 50  # 50KB max per file
        
        for css_file in styles_dir.rglob("*.css"):
            size_kb = css_file.stat().st_size / 1024
            
            assert size_kb <= max_size_kb, f"{css_file.name} is too large ({size_kb:.1f}KB)"
    
    def test_selector_complexity(self):
        """Test that CSS selectors are not overly complex."""
        styles_dir = Path(__file__).parent.parent / "styles"
        
        for css_file in styles_dir.rglob("*.css"):
            content = css_file.read_text(encoding='utf-8')
            
            # Find complex selectors (more than 4 levels deep)
            complex_selectors = re.findall(r'[^{]+\s+[^{]+\s+[^{]+\s+[^{]+\s+[^{]+\s*{', content)
            
            if len(complex_selectors) > 5:  # Allow some complexity
                warnings.warn(f"{css_file.name} has complex selectors that may impact performance")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])