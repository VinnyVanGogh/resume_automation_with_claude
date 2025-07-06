"""
Resume Output Generator Module.

This module provides functionality to generate resume outputs in multiple
formats (HTML, PDF, DOCX) from structured resume data.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union

from src.models import ResumeData
from .generator import HTMLGenerator, PDFGenerator, DOCXGenerator, OutputConfig


logger = logging.getLogger(__name__)


class ResumeGenerator:
    """
    Generate resume outputs in multiple formats.

    Main generator class that coordinates the generation of resumes
    in HTML, PDF, and DOCX formats from ATS-formatted resume data.
    """

    def __init__(self, config: Optional[OutputConfig] = None) -> None:
        """
        Initialize the resume generator.

        Args:
            config: Output generation configuration
        """
        self.config = config or OutputConfig()
        
        # Initialize format-specific generators
        self.html_generator = HTMLGenerator.from_config(self.config)
        self.pdf_generator = PDFGenerator.from_config(self.config)
        self.docx_generator = DOCXGenerator.from_config(self.config)
        
        logger.info("ResumeGenerator initialized with new architecture")

    def generate_html(
        self, 
        resume_data: ResumeData, 
        output_path: Optional[Path] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate HTML resume from structured resume data.

        Args:
            resume_data: ATS-formatted resume data from Phase 3
            output_path: Optional path to save HTML file
            template_vars: Additional template variables

        Returns:
            str: Generated HTML content
        """
        if output_path is None:
            output_path = self.config.get_output_path("html")
        
        return self.html_generator.generate(
            resume_data=resume_data,
            output_path=output_path,
            template_vars=template_vars
        )

    def generate_pdf(
        self, 
        resume_data: ResumeData, 
        output_path: Optional[Path] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate PDF resume from structured resume data.

        Args:
            resume_data: ATS-formatted resume data from Phase 3
            output_path: Optional path to save PDF file
            template_vars: Additional template variables

        Returns:
            bytes: Generated PDF content
        """
        if output_path is None:
            output_path = self.config.get_output_path("pdf")
        
        return self.pdf_generator.generate(
            resume_data=resume_data,
            output_path=output_path,
            template_vars=template_vars
        )

    def generate_docx(
        self, 
        resume_data: ResumeData, 
        output_path: Optional[Path] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate DOCX resume from structured resume data.

        Args:
            resume_data: ATS-formatted resume data from Phase 3
            output_path: Optional path to save DOCX file
            template_vars: Additional template variables

        Returns:
            bytes: Generated DOCX content
        """
        if output_path is None:
            output_path = self.config.get_output_path("docx")
        
        return self.docx_generator.generate(
            resume_data=resume_data,
            output_path=output_path,
            template_vars=template_vars
        )

    def generate_all_formats(
        self, 
        resume_data: ResumeData, 
        output_dir: Optional[Path] = None,
        custom_filename: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate resume in all supported formats.

        Args:
            resume_data: ATS-formatted resume data from Phase 3
            output_dir: Directory to save output files
            custom_filename: Custom filename prefix
            template_vars: Additional template variables

        Returns:
            Dict[str, str]: Dictionary mapping format to output file path
        """
        if output_dir:
            self.config.output_dir = output_dir
        
        results = {}
        
        try:
            # Generate HTML
            html_path = self.config.get_output_path("html", custom_filename)
            self.generate_html(resume_data, html_path, template_vars)
            results["html"] = str(html_path)
            logger.info(f"HTML generated: {html_path}")

            # Generate PDF
            pdf_path = self.config.get_output_path("pdf", custom_filename)
            self.generate_pdf(resume_data, pdf_path, template_vars)
            results["pdf"] = str(pdf_path)
            logger.info(f"PDF generated: {pdf_path}")

            # Generate DOCX
            docx_path = self.config.get_output_path("docx", custom_filename)
            self.generate_docx(resume_data, docx_path, template_vars)
            results["docx"] = str(docx_path)
            logger.info(f"DOCX generated: {docx_path}")

        except Exception as e:
            logger.error(f"Error generating outputs: {e}")
            raise

        return results

    # Backward compatibility methods for legacy API
    def generate_html_legacy(self, sections: Dict[str, Any]) -> str:
        """
        Legacy method for backward compatibility.
        
        Args:
            sections: Dictionary of section data (legacy format)
            
        Returns:
            str: Generated HTML content
        """
        logger.warning("Using legacy generate_html method - consider upgrading to ResumeData format")
        # This would need a converter from legacy format to ResumeData
        # For now, return a basic template
        return "<html><body><h1>Resume</h1><p>Legacy format - please use ResumeData</p></body></html>"

    def validate_all_outputs(self, results: Dict[str, str]) -> bool:
        """
        Validate all generated outputs for quality and compliance.
        
        Args:
            results: Dictionary of format to file path
            
        Returns:
            bool: True if all validations pass
        """
        all_valid = True
        
        for format_type, file_path in results.items():
            try:
                file_content = Path(file_path).read_bytes()
                
                if format_type == "html":
                    content_str = file_content.decode('utf-8')
                    self.html_generator.validate_output(content_str)
                elif format_type == "pdf":
                    self.pdf_generator.validate_output(file_content)
                elif format_type == "docx":
                    self.docx_generator.validate_output(file_content)
                
                logger.info(f"{format_type.upper()} validation passed")
                
            except Exception as e:
                logger.error(f"{format_type.upper()} validation failed: {e}")
                all_valid = False
        
        return all_valid
