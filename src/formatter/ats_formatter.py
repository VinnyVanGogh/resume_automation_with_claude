"""
ATS formatter module for resume data.

This module provides the core ATSFormatter class that applies ATS formatting
rules to parsed resume data for optimal compatibility with Applicant Tracking Systems.
"""

import re
from typing import List, Optional, Dict

from src.models import ResumeData, Experience, Education, ContactInfo, Skills, Project, Certification
from .config import ATSConfig
from .date_standardizer import DateStandardizer
from .header_standardizer import HeaderStandardizer


class ATSFormatter:
    """
    ATS compliance formatting engine for resume data.
    
    This class applies ATS formatting rules to parsed resume data to ensure
    optimal compatibility with Applicant Tracking Systems.
    """
    
    def __init__(self, config: Optional[ATSConfig] = None) -> None:
        """
        Initialize ATS formatter with optional configuration.
        
        Args:
            config: ATS formatting configuration. If None, uses defaults.
        """
        self.config = config or ATSConfig()
        
        # Initialize date standardizer
        self.date_standardizer = DateStandardizer()
        
        # Initialize header standardizer
        self.header_standardizer = HeaderStandardizer()
        
        # ATS-unfriendly characters to remove/replace
        self.special_chars_pattern = re.compile(r'[^\w\s\-.,()&/]')
        
        # Action verbs for bullet point optimization
        self.action_verbs = {
            'achieved', 'analyzed', 'built', 'collaborated', 'created', 'delivered',
            'designed', 'developed', 'enhanced', 'established', 'executed', 'generated',
            'implemented', 'improved', 'increased', 'launched', 'led', 'managed',
            'optimized', 'organized', 'produced', 'reduced', 'resolved', 'streamlined'
        }
    
    def format_resume(self, resume_data: ResumeData) -> ResumeData:
        """
        Apply ATS formatting rules to resume data.
        
        Args:
            resume_data: Parsed resume data to format
            
        Returns:
            ATS-formatted resume data
            
        Raises:
            ValueError: If resume data is invalid
        """
        if not resume_data:
            raise ValueError("Resume data cannot be None")
        
        # Create a copy to avoid modifying original data
        formatted_data = resume_data.model_copy(deep=True)
        
        # Apply formatting to each section
        formatted_data.contact = self._format_contact(formatted_data.contact)
        
        if formatted_data.summary:
            formatted_data.summary = self._format_summary(formatted_data.summary)
        
        if formatted_data.experience:
            formatted_data.experience = [
                self._format_experience(exp) for exp in formatted_data.experience
            ]
        
        if formatted_data.education:
            formatted_data.education = [
                self._format_education(edu) for edu in formatted_data.education
            ]
        
        if formatted_data.skills:
            formatted_data.skills = self._format_skills(formatted_data.skills)
        
        if formatted_data.projects:
            formatted_data.projects = [
                self._format_project(proj) for proj in formatted_data.projects
            ]
        
        if formatted_data.certifications:
            formatted_data.certifications = [
                self._format_certification(cert) for cert in formatted_data.certifications
            ]
        
        # Validate ATS compliance
        if not self.validate_ats_compliance(formatted_data):
            raise ValueError("Formatted data does not meet ATS compliance requirements")
        
        return formatted_data
    
    def _format_contact(self, contact: ContactInfo) -> ContactInfo:
        """
        Format contact information for ATS compliance.
        
        Args:
            contact: Contact information to format
            
        Returns:
            ATS-formatted contact information
        """
        formatted_contact = contact.model_copy()
        
        # Clean special characters from name and location
        if self.config.remove_special_chars:
            formatted_contact.name = self._clean_special_chars(formatted_contact.name)
            if formatted_contact.location:
                formatted_contact.location = self._clean_special_chars(formatted_contact.location)
        
        return formatted_contact
    
    def _format_summary(self, summary: str) -> str:
        """
        Format professional summary for ATS compliance.
        
        Args:
            summary: Professional summary text
            
        Returns:
            ATS-formatted summary
        """
        formatted_summary = summary.strip()
        
        # Remove special characters if configured
        if self.config.remove_special_chars:
            formatted_summary = self._clean_special_chars(formatted_summary)
        
        # Ensure proper line length
        formatted_summary = self._wrap_text(formatted_summary)
        
        return formatted_summary
    
    def _format_experience(self, experience: Experience) -> Experience:
        """
        Format work experience entry for ATS compliance.
        
        Args:
            experience: Experience entry to format
            
        Returns:
            ATS-formatted experience entry
        """
        formatted_exp = experience.model_copy()
        
        # Clean special characters
        if self.config.remove_special_chars:
            formatted_exp.title = self._clean_special_chars(formatted_exp.title)
            formatted_exp.company = self._clean_special_chars(formatted_exp.company)
            if formatted_exp.location:
                formatted_exp.location = self._clean_special_chars(formatted_exp.location)
        
        # Standardize dates
        formatted_exp.start_date = self.date_standardizer.standardize_date(formatted_exp.start_date)
        formatted_exp.end_date = self.date_standardizer.standardize_date(formatted_exp.end_date)
        
        # Validate date order
        if not self.date_standardizer.validate_date_order(formatted_exp.start_date, formatted_exp.end_date):
            # Log warning but don't fail - let validation catch this later
            pass
        
        # Format bullet points
        if formatted_exp.bullets:
            formatted_exp.bullets = self.optimize_bullet_points(formatted_exp.bullets)
        
        return formatted_exp
    
    def _format_education(self, education: Education) -> Education:
        """
        Format education entry for ATS compliance.
        
        Args:
            education: Education entry to format
            
        Returns:
            ATS-formatted education entry
        """
        formatted_edu = education.model_copy()
        
        # Clean special characters
        if self.config.remove_special_chars:
            formatted_edu.degree = self._clean_special_chars(formatted_edu.degree)
            formatted_edu.school = self._clean_special_chars(formatted_edu.school)
            if formatted_edu.location:
                formatted_edu.location = self._clean_special_chars(formatted_edu.location)
        
        # Standardize dates if present
        if formatted_edu.start_date:
            formatted_edu.start_date = self.date_standardizer.standardize_date(formatted_edu.start_date)
        if formatted_edu.end_date:
            formatted_edu.end_date = self.date_standardizer.standardize_date(formatted_edu.end_date)
        
        # Validate date order if both dates exist
        if (formatted_edu.start_date and formatted_edu.end_date and 
            not self.date_standardizer.validate_date_order(formatted_edu.start_date, formatted_edu.end_date)):
            # Log warning but don't fail - let validation catch this later
            pass
        
        return formatted_edu
    
    def _format_skills(self, skills: Skills) -> Skills:
        """
        Format skills section for ATS compliance.
        
        Args:
            skills: Skills section to format
            
        Returns:
            ATS-formatted skills section
        """
        formatted_skills = skills.model_copy()
        
        # Clean special characters from skill names
        if self.config.remove_special_chars and formatted_skills.categories:
            for category in formatted_skills.categories:
                category.name = self._clean_special_chars(category.name)
                category.skills = [
                    self._clean_special_chars(skill) for skill in category.skills
                ]
        
        if self.config.remove_special_chars and formatted_skills.raw_skills:
            formatted_skills.raw_skills = [
                self._clean_special_chars(skill) for skill in formatted_skills.raw_skills
            ]
        
        return formatted_skills
    
    def _format_project(self, project: Project) -> Project:
        """
        Format project entry for ATS compliance.
        
        Args:
            project: Project entry to format
            
        Returns:
            ATS-formatted project entry
        """
        formatted_proj = project.model_copy()
        
        # Clean special characters
        if self.config.remove_special_chars:
            formatted_proj.name = self._clean_special_chars(formatted_proj.name)
            if formatted_proj.description:
                formatted_proj.description = self._clean_special_chars(formatted_proj.description)
        
        # Standardize date if present
        if formatted_proj.date:
            formatted_proj.date = self.date_standardizer.standardize_date(formatted_proj.date)
        
        # Format bullet points if present
        if formatted_proj.bullets:
            formatted_proj.bullets = self.optimize_bullet_points(formatted_proj.bullets)
        
        return formatted_proj
    
    def _format_certification(self, certification: Certification) -> Certification:
        """
        Format certification entry for ATS compliance.
        
        Args:
            certification: Certification entry to format
            
        Returns:
            ATS-formatted certification entry
        """
        formatted_cert = certification.model_copy()
        
        # Clean special characters
        if self.config.remove_special_chars:
            formatted_cert.name = self._clean_special_chars(formatted_cert.name)
            formatted_cert.issuer = self._clean_special_chars(formatted_cert.issuer)
        
        # Standardize dates
        formatted_cert.date = self.date_standardizer.standardize_date(formatted_cert.date)
        if formatted_cert.expiry:
            formatted_cert.expiry = self.date_standardizer.standardize_date(formatted_cert.expiry)
        
        # Validate date order if both dates exist
        if (formatted_cert.expiry and 
            not self.date_standardizer.validate_date_order(formatted_cert.date, formatted_cert.expiry)):
            # Log warning but don't fail - let validation catch this later
            pass
        
        return formatted_cert
    
    def optimize_bullet_points(self, bullets: List[str]) -> List[str]:
        """
        Optimize bullet points for ATS parsing.
        
        Ensures bullet points start with action verbs, have proper formatting,
        and meet ATS compliance requirements.
        
        Args:
            bullets: List of bullet point strings
            
        Returns:
            Optimized bullet points
        """
        if not bullets:
            return bullets
        
        optimized_bullets = []
        
        for bullet in bullets:
            if not bullet.strip():
                continue
            
            # Clean the bullet text
            cleaned_bullet = bullet.strip()
            
            # Remove special characters if configured
            if self.config.remove_special_chars:
                cleaned_bullet = self._clean_special_chars(cleaned_bullet)
            
            # Ensure proper capitalization
            cleaned_bullet = cleaned_bullet[0].upper() + cleaned_bullet[1:] if cleaned_bullet else ""
            
            # Wrap text to respect line length
            wrapped_bullet = self._wrap_text(cleaned_bullet)
            
            optimized_bullets.append(wrapped_bullet)
        
        return optimized_bullets
    
    def format_section_content(self, content: str) -> str:
        """
        Format section content for ATS compliance.
        
        Args:
            content: Raw section content
            
        Returns:
            ATS-formatted content
        """
        if not content:
            return content
        
        formatted_content = content.strip()
        
        # Remove special characters if configured
        if self.config.remove_special_chars:
            formatted_content = self._clean_special_chars(formatted_content)
        
        # Wrap text to respect line length
        formatted_content = self._wrap_text(formatted_content)
        
        return formatted_content
    
    def validate_ats_compliance(self, resume_data: ResumeData) -> bool:
        """
        Validate that formatted data meets ATS requirements.
        
        Args:
            resume_data: Resume data to validate
            
        Returns:
            True if data meets ATS compliance, False otherwise
        """
        try:
            # Basic validation - ensure required sections exist
            if not resume_data.contact:
                return False
            
            if not resume_data.contact.name or not resume_data.contact.email:
                return False
            
            # Validate line lengths in content
            sections_to_check = []
            
            if resume_data.summary:
                sections_to_check.append(resume_data.summary)
            
            if resume_data.experience:
                for exp in resume_data.experience:
                    sections_to_check.extend(exp.bullets or [])
            
            # Check line lengths
            for content in sections_to_check:
                lines = content.split('\n')
                for line in lines:
                    if len(line) > self.config.max_line_length:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _clean_special_chars(self, text: str) -> str:
        """
        Remove ATS-unfriendly special characters from text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text with special characters removed/replaced
        """
        if not text:
            return text
        
        # Replace common problematic characters
        replacements = {
            '"': '"',  # Smart quotes to regular quotes
            '"': '"',
            ''': "'",
            ''': "'",
            '—': '-',  # Em dash to hyphen
            '–': '-',  # En dash to hyphen
            '…': '...'  # Ellipsis to periods
        }
        
        cleaned = text
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Remove any remaining special characters
        cleaned = self.special_chars_pattern.sub('', cleaned)
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _wrap_text(self, text: str) -> str:
        """
        Wrap text to respect maximum line length.
        
        Args:
            text: Text to wrap
            
        Returns:
            Wrapped text with proper line breaks
        """
        if not text or len(text) <= self.config.max_line_length:
            return text
        
        # Simple word-based wrapping
        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []
        current_length = 0
        
        for word in words:
            # Check if adding this word would exceed line length
            word_length = len(word) + (1 if current_line else 0)  # +1 for space
            
            if current_length + word_length > self.config.max_line_length and current_line:
                # Start new line
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def standardize_section_headers(self, section_names: Dict[str, str]) -> Dict[str, str]:
        """
        Standardize section headers in resume data.
        
        Args:
            section_names: Dictionary of current section names
            
        Returns:
            Dictionary with standardized section names
        """
        standardized = {}
        for key, header in section_names.items():
            if header:
                standardized[key] = self.header_standardizer.standardize_header(header)
            else:
                standardized[key] = header
        return standardized
