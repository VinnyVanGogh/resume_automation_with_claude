"""
Quality validation utilities for the resume converter module.

This module provides comprehensive output quality validation with format-specific
checks, ATS compliance validation, and quality metrics collection.
"""

import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import re

from .exceptions import ValidationError
from .types import ConversionResult


logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """
    Quality metrics for a generated output file.
    
    Attributes:
        file_path: Path to the validated file
        format_type: Format type (html, pdf, docx)
        file_size: File size in bytes
        content_score: Content quality score (0-100)
        ats_score: ATS compliance score (0-100)
        formatting_score: Formatting quality score (0-100)
        overall_score: Overall quality score (0-100)
        issues: List of quality issues found
        warnings: List of quality warnings
        recommendations: List of improvement recommendations
    """
    file_path: Path
    format_type: str
    file_size: int = 0
    content_score: float = 0.0
    ats_score: float = 0.0
    formatting_score: float = 0.0
    overall_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: str) -> None:
        """Add a quality issue."""
        self.issues.append(issue)
    
    def add_warning(self, warning: str) -> None:
        """Add a quality warning."""
        self.warnings.append(warning)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add an improvement recommendation."""
        self.recommendations.append(recommendation)
    
    def calculate_overall_score(self) -> None:
        """Calculate overall quality score from component scores."""
        # Weighted average of component scores
        weights = {
            "content": 0.4,
            "ats": 0.35,
            "formatting": 0.25
        }
        
        self.overall_score = (
            weights["content"] * self.content_score +
            weights["ats"] * self.ats_score +
            weights["formatting"] * self.formatting_score
        )


@dataclass
class ValidationReport:
    """
    Comprehensive validation report for output files.
    
    Attributes:
        is_valid: Whether all outputs pass validation
        total_files: Total number of files validated
        passed_files: Number of files that passed validation
        failed_files: Number of files that failed validation
        file_metrics: List of quality metrics for each file
        summary: Summary of validation results
    """
    is_valid: bool = True
    total_files: int = 0
    passed_files: int = 0
    failed_files: int = 0
    file_metrics: List[QualityMetrics] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def add_file_metrics(self, metrics: QualityMetrics) -> None:
        """Add metrics for a file."""
        self.file_metrics.append(metrics)
        self.total_files += 1
        
        if metrics.overall_score >= 70.0:  # Quality threshold
            self.passed_files += 1
        else:
            self.failed_files += 1
            self.is_valid = False
    
    def generate_summary(self) -> None:
        """Generate validation summary."""
        if not self.file_metrics:
            self.summary = {"message": "No files validated"}
            return
        
        # Calculate average scores
        avg_content = sum(m.content_score for m in self.file_metrics) / len(self.file_metrics)
        avg_ats = sum(m.ats_score for m in self.file_metrics) / len(self.file_metrics)
        avg_formatting = sum(m.formatting_score for m in self.file_metrics) / len(self.file_metrics)
        avg_overall = sum(m.overall_score for m in self.file_metrics) / len(self.file_metrics)
        
        # Count issues by type
        total_issues = sum(len(m.issues) for m in self.file_metrics)
        total_warnings = sum(len(m.warnings) for m in self.file_metrics)
        
        self.summary = {
            "validation_status": "PASSED" if self.is_valid else "FAILED",
            "files_validated": self.total_files,
            "files_passed": self.passed_files,
            "files_failed": self.failed_files,
            "pass_rate": (self.passed_files / self.total_files * 100) if self.total_files > 0 else 0,
            "average_scores": {
                "content": round(avg_content, 2),
                "ats_compliance": round(avg_ats, 2),
                "formatting": round(avg_formatting, 2),
                "overall": round(avg_overall, 2)
            },
            "issue_summary": {
                "total_issues": total_issues,
                "total_warnings": total_warnings,
                "critical_issues": len([m for m in self.file_metrics if m.overall_score < 50])
            }
        }


class QualityValidator:
    """
    Comprehensive quality validator for resume conversion outputs.
    
    Validates generated files for quality, ATS compliance, and formatting
    with detailed metrics and recommendations.
    """
    
    def __init__(
        self,
        min_quality_threshold: float = 70.0,
        strict_ats_validation: bool = True,
        check_file_integrity: bool = True
    ) -> None:
        """
        Initialize the quality validator.
        
        Args:
            min_quality_threshold: Minimum quality score threshold
            strict_ats_validation: Whether to use strict ATS validation
            check_file_integrity: Whether to check file integrity
        """
        self.min_quality_threshold = min_quality_threshold
        self.strict_ats_validation = strict_ats_validation
        self.check_file_integrity = check_file_integrity
        
        # ATS-friendly patterns
        self.ats_friendly_fonts = {
            "Arial", "Helvetica", "Times New Roman", "Calibri", 
            "Georgia", "Verdana", "Trebuchet MS"
        }
        
        self.ats_problematic_elements = {
            "tables", "text-boxes", "graphics", "headers", "footers",
            "columns", "special-characters"
        }
        
        logger.debug("QualityValidator initialized")
    
    def validate_output_files(
        self,
        output_files: List[Path],
        expected_formats: Optional[List[str]] = None
    ) -> ValidationReport:
        """
        Validate multiple output files comprehensively.
        
        Args:
            output_files: List of output file paths to validate
            expected_formats: Optional list of expected formats
            
        Returns:
            ValidationReport: Comprehensive validation report
        """
        report = ValidationReport()
        
        try:
            for file_path in output_files:
                try:
                    metrics = self.validate_single_file(file_path)
                    report.add_file_metrics(metrics)
                    
                except Exception as e:
                    logger.error(f"Failed to validate file {file_path}: {e}")
                    # Create failed metrics for this file
                    failed_metrics = QualityMetrics(
                        file_path=file_path,
                        format_type=self._detect_format(file_path)
                    )
                    failed_metrics.add_issue(f"Validation failed: {e}")
                    report.add_file_metrics(failed_metrics)
            
            # Generate summary
            report.generate_summary()
            
        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            raise ValidationError(f"Output validation failed: {e}")
        
        return report
    
    def validate_single_file(self, file_path: Path) -> QualityMetrics:
        """
        Validate a single output file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            QualityMetrics: Quality metrics for the file
        """
        if not file_path.exists():
            raise ValidationError(f"Output file does not exist: {file_path}")
        
        format_type = self._detect_format(file_path)
        
        metrics = QualityMetrics(
            file_path=file_path,
            format_type=format_type,
            file_size=file_path.stat().st_size
        )
        
        # Basic file validation
        self._validate_file_basic(metrics)
        
        # Format-specific validation
        if format_type == "html":
            self._validate_html_file(metrics)
        elif format_type == "pdf":
            self._validate_pdf_file(metrics)
        elif format_type == "docx":
            self._validate_docx_file(metrics)
        
        # ATS compliance validation
        self._validate_ats_compliance(metrics)
        
        # Calculate overall score
        metrics.calculate_overall_score()
        
        return metrics
    
    def _detect_format(self, file_path: Path) -> str:
        """Detect file format from path and mimetype."""
        suffix = file_path.suffix.lower()
        
        format_map = {
            ".html": "html",
            ".htm": "html", 
            ".pdf": "pdf",
            ".docx": "docx",
            ".doc": "docx"
        }
        
        return format_map.get(suffix, "unknown")
    
    def _validate_file_basic(self, metrics: QualityMetrics) -> None:
        """Perform basic file validation."""
        # Check file size
        if metrics.file_size == 0:
            metrics.add_issue("File is empty")
            return
        
        if metrics.file_size < 1024:  # Less than 1KB
            metrics.add_warning("File is very small (less than 1KB)")
        
        if metrics.file_size > 10 * 1024 * 1024:  # More than 10MB
            metrics.add_warning("File is very large (over 10MB)")
        
        # Basic content score
        if metrics.file_size > 0:
            metrics.content_score = min(100.0, max(50.0, metrics.file_size / 1024 * 10))
    
    def _validate_html_file(self, metrics: QualityMetrics) -> None:
        """Validate HTML file quality."""
        try:
            content = metrics.file_path.read_text(encoding='utf-8')
            
            # Check for basic HTML structure
            if not re.search(r'<html.*?>.*</html>', content, re.DOTALL | re.IGNORECASE):
                metrics.add_issue("Missing proper HTML structure")
            
            # Check for essential elements
            essential_tags = ['<head>', '<body>', '<title>']
            for tag in essential_tags:
                if tag not in content.lower():
                    metrics.add_warning(f"Missing {tag} element")
            
            # Check for ATS-problematic elements
            problematic_patterns = [
                r'<table[^>]*>',  # Tables
                r'<img[^>]*>',    # Images
                r'style\s*=\s*["\'][^"\']*float[^"\']*["\']'  # Floating elements
            ]
            
            for pattern in problematic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    metrics.add_warning("Contains elements that may not be ATS-friendly")
            
            # Check for proper encoding
            if 'charset=utf-8' not in content.lower():
                metrics.add_recommendation("Consider adding UTF-8 charset declaration")
            
            # Formatting score based on structure
            structure_score = 0
            if '<html' in content.lower(): structure_score += 20
            if '<head>' in content.lower(): structure_score += 20
            if '<body>' in content.lower(): structure_score += 20
            if '<title>' in content.lower(): structure_score += 20
            if 'utf-8' in content.lower(): structure_score += 20
            
            metrics.formatting_score = structure_score
            
        except Exception as e:
            metrics.add_issue(f"Failed to read HTML content: {e}")
            metrics.formatting_score = 0
    
    def _validate_pdf_file(self, metrics: QualityMetrics) -> None:
        """Validate PDF file quality."""
        try:
            # Basic PDF validation
            with open(metrics.file_path, 'rb') as f:
                header = f.read(10)
                
            if not header.startswith(b'%PDF-'):
                metrics.add_issue("File does not appear to be a valid PDF")
                return
            
            # PDF version check
            version_match = re.search(rb'%PDF-(\d+\.\d+)', header)
            if version_match:
                version = version_match.group(1).decode()
                if version < "1.4":
                    metrics.add_warning(f"PDF version {version} may not be compatible with all systems")
            
            # Estimate formatting score based on file size and structure
            # This is a simplified heuristic - in production, you might use a PDF library
            if metrics.file_size > 10000:  # Reasonable size for a resume
                metrics.formatting_score = 85.0
            else:
                metrics.formatting_score = 60.0
            
            metrics.add_recommendation("Consider validating PDF with a dedicated PDF library for deeper analysis")
            
        except Exception as e:
            metrics.add_issue(f"Failed to validate PDF: {e}")
            metrics.formatting_score = 0
    
    def _validate_docx_file(self, metrics: QualityMetrics) -> None:
        """Validate DOCX file quality."""
        try:
            # Basic DOCX validation - check if it's a valid ZIP file
            import zipfile
            
            if not zipfile.is_zipfile(metrics.file_path):
                metrics.add_issue("DOCX file is not a valid ZIP archive")
                return
            
            # Check for essential DOCX components
            with zipfile.ZipFile(metrics.file_path, 'r') as docx_zip:
                expected_files = [
                    '[Content_Types].xml',
                    'word/document.xml',
                    '_rels/.rels'
                ]
                
                missing_files = []
                for expected_file in expected_files:
                    if expected_file not in docx_zip.namelist():
                        missing_files.append(expected_file)
                
                if missing_files:
                    metrics.add_issue(f"Missing essential DOCX components: {missing_files}")
                
                # Calculate formatting score
                structure_score = len(expected_files) - len(missing_files)
                metrics.formatting_score = (structure_score / len(expected_files)) * 100
            
        except ImportError:
            metrics.add_warning("zipfile module not available for DOCX validation")
            metrics.formatting_score = 70.0  # Default score
        except Exception as e:
            metrics.add_issue(f"Failed to validate DOCX: {e}")
            metrics.formatting_score = 0
    
    def _validate_ats_compliance(self, metrics: QualityMetrics) -> None:
        """Validate ATS compliance."""
        ats_score = 100.0
        
        # File format compatibility
        if metrics.format_type not in ["pdf", "docx", "html"]:
            ats_score -= 50
            metrics.add_issue(f"Format '{metrics.format_type}' may not be ATS-compatible")
        
        # File size considerations
        if metrics.file_size > 5 * 1024 * 1024:  # 5MB
            ats_score -= 20
            metrics.add_warning("Large file size may cause ATS processing issues")
        
        # Format-specific ATS checks
        if metrics.format_type == "pdf":
            # PDF-specific ATS considerations
            if metrics.file_size < 50000:  # Very small PDF might be problematic
                ats_score -= 10
                metrics.add_warning("Very small PDF might lack sufficient content for ATS")
        
        elif metrics.format_type == "docx":
            # DOCX is generally ATS-friendly
            ats_score += 5  # Bonus for ATS-friendly format
        
        elif metrics.format_type == "html":
            # HTML needs additional checks
            ats_score -= 5  # Minor penalty as HTML is less standard for resumes
        
        # Quality-based adjustments
        if len(metrics.issues) > 0:
            ats_score -= len(metrics.issues) * 10
        
        if len(metrics.warnings) > 2:
            ats_score -= (len(metrics.warnings) - 2) * 5
        
        metrics.ats_score = max(0.0, min(100.0, ats_score))
        
        # Add ATS-specific recommendations
        if metrics.ats_score < 80:
            metrics.add_recommendation("Consider using PDF or DOCX format for better ATS compatibility")
        
        if metrics.file_size > 2 * 1024 * 1024:
            metrics.add_recommendation("Consider optimizing file size for faster ATS processing")
    
    def validate_conversion_result(self, result: ConversionResult) -> ValidationReport:
        """
        Validate a complete conversion result.
        
        Args:
            result: ConversionResult to validate
            
        Returns:
            ValidationReport: Validation report for the result
        """
        return self.validate_output_files(result.output_files)
    
    def get_quality_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """
        Get quality improvement recommendations for a file.
        
        Args:
            metrics: Quality metrics for the file
            
        Returns:
            List of improvement recommendations
        """
        recommendations = list(metrics.recommendations)
        
        # Add score-based recommendations
        if metrics.content_score < 70:
            recommendations.append("Consider adding more detailed content to improve content quality")
        
        if metrics.ats_score < 70:
            recommendations.append("Review ATS compliance guidelines and adjust formatting")
        
        if metrics.formatting_score < 70:
            recommendations.append("Review file structure and formatting for potential improvements")
        
        if metrics.overall_score < 60:
            recommendations.append("Consider regenerating the file with different settings")
        
        return recommendations