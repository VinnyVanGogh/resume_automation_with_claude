#!/usr/bin/env python
"""
HTML generator for resume output.

This module provides the HTMLGenerator class for creating semantic,
ATS-compliant HTML resumes using Jinja2 templates.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from src.models import ResumeData
from .config import HTMLConfig, OutputConfig


logger = logging.getLogger(__name__)


class HTMLGenerator:
    """
    Generate HTML resume output from structured resume data.
    
    This class uses Jinja2 templates to create semantic HTML5 resumes
    with ATS-compliant markup and professional styling.
    """
    
    def __init__(self, config: Optional[HTMLConfig] = None) -> None:
        """
        Initialize HTML generator with configuration.
        
        Args:
            config: HTML generation configuration. If None, uses defaults.
        """
        self.config = config or HTMLConfig()
        self.template_dir = Path(__file__).parent.parent / "templates"
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters for better formatting
        self.env.filters["format_date"] = self._format_date
        self.env.filters["format_phone"] = self._format_phone
        self.env.filters["format_url"] = self._format_url
        
        logger.info(f"HTMLGenerator initialized with template dir: {self.template_dir}")
    
    def generate(
        self, 
        resume_data: ResumeData, 
        output_path: Optional[Path] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate HTML resume from structured resume data.
        
        Args:
            resume_data: Validated resume data from Phase 3 formatter
            output_path: Optional path to save HTML file
            template_vars: Additional template variables
            
        Returns:
            str: Generated HTML content
            
        Raises:
            TemplateNotFound: If template file is not found
            ValueError: If resume data is invalid
        """
        logger.info("Starting HTML generation")
        
        # Validate input data
        if not isinstance(resume_data, ResumeData):
            raise ValueError("resume_data must be a ResumeData instance")
        
        try:
            # Load template
            template = self.env.get_template(self.config.template_name)
            
            # Prepare template context
            context = self._prepare_template_context(resume_data, template_vars)
            
            # Render template
            html_content = template.render(**context)
            
            # Post-process HTML if needed
            html_content = self._post_process_html(html_content)
            
            # Save to file if path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(html_content, encoding="utf-8")
                logger.info(f"HTML resume saved to: {output_path}")
            
            logger.info("HTML generation completed successfully")
            return html_content
            
        except TemplateNotFound as e:
            logger.error(f"Template not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            raise
    
    def _prepare_template_context(
        self, 
        resume_data: ResumeData, 
        extra_vars: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare template context with resume data and configuration.
        
        Args:
            resume_data: Resume data to render
            extra_vars: Additional template variables
            
        Returns:
            Dict[str, Any]: Template context dictionary
        """
        context = {
            # Resume data
            "contact": resume_data.contact,
            "summary": resume_data.summary,
            "experience": resume_data.experience,
            "education": resume_data.education,
            "skills": resume_data.skills,
            "projects": resume_data.projects,
            "certifications": resume_data.certifications,
            
            # Configuration
            "config": self.config,
            "theme": self.config.theme,
            "meta_description": self.config.meta_description,
            
            # Helper variables
            "has_projects": bool(resume_data.projects),
            "has_certifications": bool(resume_data.certifications),
            "has_summary": bool(resume_data.summary),
            
            # SEO and metadata
            "page_title": f"{resume_data.contact.name} - Resume",
            "canonical_url": None,  # Can be set via extra_vars
        }
        
        # Add custom CSS if provided
        if self.config.custom_css:
            context["custom_css"] = self.config.custom_css
        
        # Merge extra variables
        if extra_vars:
            context.update(extra_vars)
        
        return context
    
    def _post_process_html(self, html_content: str) -> str:
        """
        Post-process generated HTML for optimization and compliance.
        
        Args:
            html_content: Raw HTML content from template
            
        Returns:
            str: Processed HTML content
        """
        # Remove extra whitespace (but preserve formatting)
        lines = html_content.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped:  # Keep non-empty lines
                processed_lines.append(line.rstrip())
        
        return '\n'.join(processed_lines)
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """
        Jinja2 filter for formatting dates.
        
        Args:
            date_str: Date string to format
            
        Returns:
            str: Formatted date string
        """
        if not date_str:
            return ""
        
        # Handle common date variations
        if date_str.lower() in ["present", "current", "now"]:
            return "Present"
        
        return date_str
    
    def _format_phone(self, phone: Optional[str]) -> str:
        """
        Jinja2 filter for formatting phone numbers.
        
        Args:
            phone: Phone number to format
            
        Returns:
            str: Formatted phone number
        """
        if not phone:
            return ""
        
        # Remove all non-digit characters for processing
        digits = ''.join(c for c in phone if c.isdigit())
        
        # Format US phone numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        # Return original if not standard format
        return phone
    
    def _format_url(self, url: Optional[str]) -> str:
        """
        Jinja2 filter for formatting URLs.
        
        Args:
            url: URL to format
            
        Returns:
            str: Formatted URL
        """
        if not url:
            return ""
        
        # Remove protocol for display (but keep for href)
        display_url = str(url)
        if display_url.startswith(("http://", "https://")):
            display_url = display_url.split("://", 1)[1]
        
        return display_url
    
    def validate_output(self, html_content: str) -> bool:
        """
        Validate generated HTML for basic compliance.
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Basic HTML5 structure validation
        required_elements = [
            "<!DOCTYPE html>",
            "<html",
            "<head>",
            "<title>",
            "<body>",
        ]
        
        for element in required_elements:
            if element not in html_content:
                raise ValueError(f"Missing required HTML element: {element}")
        
        # ATS compliance checks
        ats_unfriendly = ["<table", "<img", "<canvas", "<svg"]
        for element in ats_unfriendly:
            if element in html_content.lower():
                logger.warning(f"ATS-unfriendly element detected: {element}")
        
        logger.info("HTML validation passed")
        return True
    
    @classmethod
    def from_config(cls, config: OutputConfig) -> "HTMLGenerator":
        """
        Create HTMLGenerator from OutputConfig.
        
        Args:
            config: Output configuration containing HTML config
            
        Returns:
            HTMLGenerator: Configured generator instance
        """
        return cls(config.html)