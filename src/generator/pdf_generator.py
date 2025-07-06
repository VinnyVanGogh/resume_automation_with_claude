"""
PDF generator for resume output.

This module provides the PDFGenerator class for creating professional,
print-optimized PDF resumes using WeasyPrint.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from src.models import ResumeData
from .config import PDFConfig, OutputConfig
from .html_generator import HTMLGenerator


logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Generate PDF resume output from structured resume data.
    
    This class uses WeasyPrint to convert HTML resumes into
    professional, print-optimized PDF documents.
    """
    
    def __init__(self, config: Optional[PDFConfig] = None) -> None:
        """
        Initialize PDF generator with configuration.
        
        Args:
            config: PDF generation configuration. If None, uses defaults.
        """
        self.config = config or PDFConfig()
        self.template_dir = Path(__file__).parent.parent / "templates"
        
        # Initialize HTML generator for content creation
        from .config import HTMLConfig
        html_config = HTMLConfig(
            template_name="resume.html",
            theme="professional",
            include_styles=True
        )
        self.html_generator = HTMLGenerator(html_config)
        
        # Configure WeasyPrint font handling
        self.font_config = FontConfiguration()
        
        logger.info("PDFGenerator initialized")
    
    def generate(
        self, 
        resume_data: ResumeData, 
        output_path: Optional[Path] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate PDF resume from structured resume data.
        
        Args:
            resume_data: Validated resume data from Phase 3 formatter
            output_path: Optional path to save PDF file
            template_vars: Additional template variables
            
        Returns:
            bytes: Generated PDF content as bytes
            
        Raises:
            ValueError: If resume data is invalid
            RuntimeError: If PDF generation fails
        """
        logger.info("Starting PDF generation")
        
        # Validate input data
        if not isinstance(resume_data, ResumeData):
            raise ValueError("resume_data must be a ResumeData instance")
        
        try:
            # Generate HTML content first
            html_content = self._generate_pdf_html(resume_data, template_vars)
            
            # Create WeasyPrint HTML object
            html_doc = HTML(string=html_content, base_url=str(self.template_dir))
            
            # Load and configure CSS
            css_content = self._get_pdf_css()
            css_doc = CSS(string=css_content, font_config=self.font_config)
            
            # Generate PDF using WeasyPrint (simplified approach)
            pdf_bytes = html_doc.write_pdf(
                stylesheets=[css_doc]
            )
            
            # Save to file if path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(pdf_bytes)
                logger.info(f"PDF resume saved to: {output_path}")
            
            logger.info("PDF generation completed successfully")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise RuntimeError(f"PDF generation failed: {e}") from e
    
    def _generate_pdf_html(
        self, 
        resume_data: ResumeData, 
        template_vars: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate HTML content optimized for PDF conversion.
        
        Args:
            resume_data: Resume data to render
            template_vars: Additional template variables
            
        Returns:
            str: HTML content optimized for PDF
        """
        # Add PDF-specific template variables
        pdf_vars = {
            "pdf_mode": True,
            "include_print_styles": True,
            "optimize_for_print": True,
        }
        
        if template_vars:
            pdf_vars.update(template_vars)
        
        # Generate HTML using HTML generator
        html_content = self.html_generator.generate(
            resume_data=resume_data,
            template_vars=pdf_vars
        )
        
        return html_content
    
    def _get_pdf_css(self) -> str:
        """
        Get CSS content optimized for PDF generation.
        
        Returns:
            str: CSS content for PDF styling
        """
        css_path = self.template_dir / "styles.css"
        
        try:
            base_css = css_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"CSS file not found: {css_path}, using default styles")
            base_css = self._get_default_css()
        
        # Add PDF-specific styles
        pdf_specific_css = self._get_pdf_specific_css()
        
        return f"{base_css}\n\n{pdf_specific_css}"
    
    def _get_pdf_specific_css(self) -> str:
        """
        Get PDF-specific CSS overrides.
        
        Returns:
            str: PDF-specific CSS rules
        """
        return f"""
/* PDF-specific optimizations */
@page {{
    size: {self.config.page_size};
    margin: {self.config.margin_top}in {self.config.margin_right}in {self.config.margin_bottom}in {self.config.margin_left}in;
    
    @top-center {{
        content: none;
    }}
    
    @bottom-center {{
        content: none;
    }}
}}

/* Font and typography for PDF */
body {{
    font-family: {self.config.font_family}, sans-serif;
    font-size: {self.config.font_size}pt;
    line-height: 1.2;
    color: #000;
    background: #fff;
}}

/* Optimize text rendering for PDF */
* {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

/* Page break controls */
h1, h2, h3 {{
    page-break-after: avoid;
    orphans: 3;
    widows: 3;
}}

.experience-item,
.education-item,
.project-item {{
    page-break-inside: avoid;
}}

/* Remove any background colors for PDF */
* {{
    background: transparent !important;
}}

/* Ensure good contrast */
a {{
    color: #000 !important;
    text-decoration: none;
}}

/* Optimize spacing for single page when possible */
.compact {{
    margin-bottom: 8pt;
}}

.compact h2 {{
    margin-top: 10pt;
    margin-bottom: 6pt;
}}

.compact .experience-item {{
    margin-bottom: 8pt;
}}
"""
    
    def _get_default_css(self) -> str:
        """
        Get default CSS if styles.css is not found.
        
        Returns:
            str: Default CSS content
        """
        return """
/* Default PDF styles */
body {
    font-family: Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.2;
    color: #000;
    background: #fff;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 20pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 8pt;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 16pt;
    margin-bottom: 8pt;
    border-bottom: 1pt solid #000;
    padding-bottom: 2pt;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 10pt;
    margin-bottom: 4pt;
}

.contact-info {
    text-align: center;
    margin-bottom: 20pt;
}

.experience-item {
    margin-bottom: 12pt;
}

ul {
    margin: 8pt 0;
    padding-left: 18pt;
}

li {
    margin: 4pt 0;
}
"""
    
    def validate_output(self, pdf_bytes: bytes) -> bool:
        """
        Validate generated PDF for basic compliance.
        
        Args:
            pdf_bytes: PDF content to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Basic PDF validation
        if not pdf_bytes:
            raise ValueError("PDF content is empty")
        
        # Check for PDF header
        if not pdf_bytes.startswith(b'%PDF-'):
            raise ValueError("Invalid PDF format - missing PDF header")
        
        # Check minimum size (should be more than just header)
        if len(pdf_bytes) < 1000:
            raise ValueError("PDF file too small - possible generation error")
        
        logger.info("PDF validation passed")
        return True
    
    def get_page_count(self, pdf_bytes: bytes) -> int:
        """
        Get the number of pages in the generated PDF.
        
        Args:
            pdf_bytes: PDF content
            
        Returns:
            int: Number of pages
        """
        try:
            # This is a simple estimation based on PDF structure
            # For production use, consider using PyPDF2 or similar
            page_count = pdf_bytes.count(b'/Type /Page')
            return max(1, page_count)  # At least 1 page
        except Exception:
            logger.warning("Could not determine page count")
            return 1
    
    @classmethod
    def from_config(cls, config: OutputConfig) -> "PDFGenerator":
        """
        Create PDFGenerator from OutputConfig.
        
        Args:
            config: Output configuration containing PDF config
            
        Returns:
            PDFGenerator: Configured generator instance
        """
        return cls(config.pdf)