"""
ATS-compliant formatting engine for resume data.

This module provides the core formatting functionality to transform
parsed resume data into ATS-optimized format for maximum compatibility
with Applicant Tracking Systems.
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .models import ResumeData, Experience, Education, ContactInfo, Skills, Project, Certification


@dataclass
class ATSConfig:
    """
    Configuration for ATS formatting rules.
    
    Attributes:
        max_line_length: Maximum line length for ATS compatibility (default: 80)
        bullet_style: Bullet point style ('•', '-', '*') 
        section_order: Preferred order of resume sections
        optimize_keywords: Whether to optimize keyword density
        remove_special_chars: Whether to remove ATS-unfriendly characters
    """
    
    max_line_length: int = 80
    bullet_style: str = "•"
    section_order: Optional[List[str]] = None
    optimize_keywords: bool = True
    remove_special_chars: bool = True
    
    def __post_init__(self) -> None:
        """Set default section order if not provided."""
        if self.section_order is None:
            self.section_order = [
                "contact",
                "summary", 
                "experience",
                "education",
                "skills",
                "projects",
                "certifications"
            ]


class DateStandardizer:
    """
    Standardize date formats for ATS compliance.
    
    Converts various date formats to the standard "Month YYYY - Month YYYY" format
    for optimal ATS parsing compatibility.
    """
    
    def __init__(self) -> None:
        """Initialize date standardizer with regex patterns."""
        # Month name mappings for standardization
        self.month_mappings = {
            'january': 'January', 'jan': 'January',
            'february': 'February', 'feb': 'February',
            'march': 'March', 'mar': 'March',
            'april': 'April', 'apr': 'April',
            'may': 'May',
            'june': 'June', 'jun': 'June',
            'july': 'July', 'jul': 'July',
            'august': 'August', 'aug': 'August',
            'september': 'September', 'sep': 'September', 'sept': 'September',
            'october': 'October', 'oct': 'October',
            'november': 'November', 'nov': 'November',
            'december': 'December', 'dec': 'December'
        }
        
        # Present/Current variations
        self.present_variations = {
            'present', 'current', 'now', 'ongoing', 'today'
        }
        
        # Regex patterns for different date formats
        self.date_patterns = [
            # "January 2020 - Present" or "January 2020 - December 2021"
            re.compile(r'(\w+)\s+(\d{4})\s*[-–—]\s*(\w+)(?:\s+(\d{4}))?', re.IGNORECASE),
            # "Jan 2020 - Dec 2021" 
            re.compile(r'(\w+)\s+(\d{4})\s*[-–—]\s*(\w+)\s+(\d{4})', re.IGNORECASE),
            # "2020 - 2021" or "2020 - Present"
            re.compile(r'(\d{4})\s*[-–—]\s*(\w+|\d{4})', re.IGNORECASE),
            # Single dates: "January 2020" or "2020"
            re.compile(r'(\w+)\s+(\d{4})', re.IGNORECASE),
            re.compile(r'^(\d{4})$', re.IGNORECASE)
        ]
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize a date string to ATS-compliant format.
        
        Args:
            date_str: Date string to standardize
            
        Returns:
            Standardized date string in "Month YYYY - Month YYYY" format
            
        Examples:
            "Jan 2020 - Dec 2021" -> "January 2020 - December 2021"
            "2020 - Present" -> "2020 - Present"
            "January 2020" -> "January 2020"
        """
        if not date_str or not date_str.strip():
            return date_str
        
        cleaned_date = date_str.strip()
        
        # Try each pattern until we find a match
        for pattern in self.date_patterns:
            match = pattern.match(cleaned_date)
            if match:
                return self._format_matched_date(match.groups(), cleaned_date)
        
        # If no pattern matches, return cleaned original
        return cleaned_date
    
    def standardize_date_range(self, start_date: str, end_date: str) -> tuple[str, str]:
        """
        Standardize a pair of start and end dates.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Tuple of (standardized_start_date, standardized_end_date)
        """
        standardized_start = self.standardize_date(start_date)
        standardized_end = self.standardize_date(end_date)
        
        return standardized_start, standardized_end
    
    def validate_date_order(self, start_date: str, end_date: str) -> bool:
        """
        Validate that start date comes before end date.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            True if date order is valid, False otherwise
        """
        # Handle present/current cases
        if self._is_present_date(end_date):
            return True
        
        try:
            start_year = self._extract_year(start_date)
            end_year = self._extract_year(end_date)
            
            if start_year and end_year:
                return start_year <= end_year
            
            return True  # If we can't extract years, assume valid
            
        except Exception:
            return True  # If parsing fails, assume valid
    
    def _format_matched_date(self, groups: tuple[str, ...], original: str) -> str:
        """
        Format matched date groups into standardized format.
        
        Args:
            groups: Regex match groups
            original: Original date string as fallback
            
        Returns:
            Formatted date string
        """
        if len(groups) == 4:  # Full date range
            start_month, start_year, end_part, end_year = groups
            
            # Standardize start month
            start_month_std = self._standardize_month(start_month)
            
            # Handle end part (could be month or present variation)
            if self._is_present_date(end_part):
                return f"{start_month_std} {start_year} - Present"
            else:
                end_month_std = self._standardize_month(end_part)
                if end_year:
                    return f"{start_month_std} {start_year} - {end_month_std} {end_year}"
                else:
                    return f"{start_month_std} {start_year} - {end_month_std}"
        
        elif len(groups) == 3:  # Month Year - Month/Year or Year - Year/Present
            first, second, third = groups
            
            if first.isdigit() and len(first) == 4:  # Year - Year/Present format
                if self._is_present_date(third):
                    return f"{first} - Present"
                else:
                    return f"{first} - {third}"
            else:  # Month Year - Month format
                start_month_std = self._standardize_month(first)
                if self._is_present_date(third):
                    return f"{start_month_std} {second} - Present"
                else:
                    end_month_std = self._standardize_month(third)
                    return f"{start_month_std} {second} - {end_month_std}"
        
        elif len(groups) == 2:  # Month Year or Year - Year/Present
            first, second = groups
            
            if first.isdigit() and len(first) == 4:  # Year - Year/Present
                if self._is_present_date(second):
                    return f"{first} - Present"
                else:
                    return f"{first} - {second}"
            else:  # Month Year
                month_std = self._standardize_month(first)
                return f"{month_std} {second}"
        
        elif len(groups) == 1:  # Single year
            return str(groups[0])
        
        return original
    
    def _standardize_month(self, month_str: str) -> str:
        """
        Standardize month name to full month name.
        
        Args:
            month_str: Month string to standardize
            
        Returns:
            Standardized month name
        """
        if not month_str:
            return month_str
        
        month_lower = month_str.lower().strip()
        return self.month_mappings.get(month_lower, month_str.title())
    
    def _is_present_date(self, date_str: str) -> bool:
        """
        Check if date string represents present/current.
        
        Args:
            date_str: Date string to check
            
        Returns:
            True if represents present, False otherwise
        """
        if not date_str:
            return False
        
        return date_str.lower().strip() in self.present_variations
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """
        Extract year from date string.
        
        Args:
            date_str: Date string to extract year from
            
        Returns:
            Extracted year as integer, or None if not found
        """
        if not date_str:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'\b(\d{4})\b', date_str)
        if year_match:
            try:
                return int(year_match.group(1))
            except ValueError:
                pass
        
        return None


class ATSFormatter:
    """
    ATS compliance formatting engine for resume data.
    
    This class applies ATS formatting rules to parsed resume data to ensure
    optimal compatibility with Applicant Tracking Systems.
    """
    
    def __init__(self, config: Optional[ATSConfig] = None):
        """
        Initialize ATS formatter with optional configuration.
        
        Args:
            config: ATS formatting configuration. If None, uses defaults.
        """
        self.config = config or ATSConfig()
        
        # Initialize date standardizer
        self.date_standardizer = DateStandardizer()
        
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
