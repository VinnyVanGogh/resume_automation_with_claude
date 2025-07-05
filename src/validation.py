"""
Resume validation module.

This module provides comprehensive validation for resume data,
ensuring all required sections are present and properly formatted.
"""

import re
from datetime import datetime
from typing import List, Optional

from .models import ResumeData, ContactInfo, Experience, Education
from .custom_types import ValidationResult


class ResumeValidator:
    """
    Validator for resume data structure and content quality.
    
    Provides comprehensive validation including:
    - Required section validation
    - Date format validation  
    - Content quality checks
    - Configurable validation rules
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the resume validator.

        Args:
            strict_mode: Enable strict validation rules
        """
        self.strict_mode = strict_mode
        self.min_experience_count = 1 if strict_mode else 0
        self.min_education_count = 1 if strict_mode else 0
        self.min_bullet_length = 10 if strict_mode else 5
        self.max_bullet_length = 200

    def validate_resume(self, resume_data: ResumeData) -> ValidationResult:
        """
        Validate complete resume data.

        Args:
            resume_data: Resume data to validate

        Returns:
            ValidationResult: Validation result with errors and warnings
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validate contact information
        contact_errors, contact_warnings = self._validate_contact_info(resume_data.contact)
        errors.extend(contact_errors)
        warnings.extend(contact_warnings)

        # Validate experience section
        exp_errors, exp_warnings = self._validate_experience(resume_data.experience)
        errors.extend(exp_errors)
        warnings.extend(exp_warnings)

        # Validate education section
        edu_errors, edu_warnings = self._validate_education(resume_data.education)
        errors.extend(edu_errors)
        warnings.extend(edu_warnings)

        # Validate overall structure
        structure_errors, structure_warnings = self._validate_structure(resume_data)
        errors.extend(structure_errors)
        warnings.extend(structure_warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_contact_info(self, contact: ContactInfo) -> tuple[List[str], List[str]]:
        """
        Validate contact information.

        Args:
            contact: Contact information to validate

        Returns:
            tuple: (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validate required fields
        if not contact.name or len(contact.name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")

        if not contact.email:
            errors.append("Email address is required")

        # Validate optional fields if present
        if contact.phone:
            if not self._validate_phone_format(contact.phone):
                warnings.append("Phone number format may not be standard")

        if contact.linkedin:
            if not str(contact.linkedin).startswith(('https://linkedin.com', 'https://www.linkedin.com')):
                warnings.append("LinkedIn URL should start with https://www.linkedin.com")

        if contact.github:
            if not str(contact.github).startswith(('https://github.com', 'https://www.github.com')):
                warnings.append("GitHub URL should start with https://github.com")

        return errors, warnings

    def _validate_experience(self, experience: List[Experience]) -> tuple[List[str], List[str]]:
        """
        Validate work experience section.

        Args:
            experience: List of experience entries

        Returns:
            tuple: (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check minimum experience requirement
        if len(experience) < self.min_experience_count:
            if self.strict_mode:
                errors.append(f"At least {self.min_experience_count} experience entry is required")
            else:
                warnings.append("Consider adding work experience entries")

        # Validate each experience entry
        for i, exp in enumerate(experience):
            entry_prefix = f"Experience entry {i + 1}"

            # Validate required fields
            if not exp.title or len(exp.title.strip()) < 2:
                errors.append(f"{entry_prefix}: Job title must be at least 2 characters")

            if not exp.company or len(exp.company.strip()) < 2:
                errors.append(f"{entry_prefix}: Company name must be at least 2 characters")

            # Validate dates
            date_errors = self._validate_date_range(exp.start_date, exp.end_date)
            for error in date_errors:
                errors.append(f"{entry_prefix}: {error}")

            # Validate bullets
            bullet_errors, bullet_warnings = self._validate_bullets(exp.bullets, entry_prefix)
            errors.extend(bullet_errors)
            warnings.extend(bullet_warnings)

        return errors, warnings

    def _validate_education(self, education: List[Education]) -> tuple[List[str], List[str]]:
        """
        Validate education section.

        Args:
            education: List of education entries

        Returns:
            tuple: (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check minimum education requirement
        if len(education) < self.min_education_count:
            if self.strict_mode:
                errors.append(f"At least {self.min_education_count} education entry is required")
            else:
                warnings.append("Consider adding education entries")

        # Validate each education entry
        for i, edu in enumerate(education):
            entry_prefix = f"Education entry {i + 1}"

            # Validate required fields
            if not edu.degree or len(edu.degree.strip()) < 2:
                errors.append(f"{entry_prefix}: Degree name must be at least 2 characters")

            if not edu.school or len(edu.school.strip()) < 2:
                errors.append(f"{entry_prefix}: School name must be at least 2 characters")

            # Validate dates if provided
            if edu.start_date or edu.end_date:
                date_errors = self._validate_date_range(edu.start_date, edu.end_date)
                for error in date_errors:
                    warnings.append(f"{entry_prefix}: {error}")

        return errors, warnings

    def _validate_structure(self, resume_data: ResumeData) -> tuple[List[str], List[str]]:
        """
        Validate overall resume structure.

        Args:
            resume_data: Complete resume data

        Returns:
            tuple: (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check if resume has meaningful content
        sections_with_content = resume_data.get_all_sections()
        
        if len(sections_with_content) < 3:
            warnings.append("Resume should have at least 3 main sections (contact, experience, education)")

        # Check for summary
        if not resume_data.summary:
            warnings.append("Consider adding a professional summary")

        # Check for skills
        if not resume_data.skills or not resume_data.skills.has_skills():
            warnings.append("Consider adding a skills section")

        # Check overall length
        total_bullets = sum(len(exp.bullets) for exp in resume_data.experience)
        if total_bullets < 3:
            warnings.append("Resume should have at least 3 achievement bullets across all experience")

        return errors, warnings

    def _validate_bullets(self, bullets: List[str], context: str) -> tuple[List[str], List[str]]:
        """
        Validate bullet points for quality and format.

        Args:
            bullets: List of bullet points
            context: Context for error messages

        Returns:
            tuple: (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        if not bullets:
            warnings.append(f"{context}: Consider adding achievement bullets")
            return errors, warnings

        for i, bullet in enumerate(bullets):
            bullet_ref = f"{context}, bullet {i + 1}"

            # Check length
            if len(bullet) < self.min_bullet_length:
                warnings.append(f"{bullet_ref}: Bullet point is very short ({len(bullet)} chars)")

            if len(bullet) > self.max_bullet_length:
                warnings.append(f"{bullet_ref}: Bullet point is very long ({len(bullet)} chars)")

            # Check for action words (basic quality check)
            if self.strict_mode:
                action_words = ['led', 'managed', 'developed', 'created', 'implemented', 
                              'improved', 'increased', 'decreased', 'built', 'designed',
                              'analyzed', 'coordinated', 'achieved', 'delivered', 'optimized']
                
                if not any(word in bullet.lower() for word in action_words):
                    warnings.append(f"{bullet_ref}: Consider starting with a strong action verb")

        return errors, warnings

    def _validate_date_range(self, start_date: Optional[str], end_date: Optional[str]) -> List[str]:
        """
        Validate date range format and logic.

        Args:
            start_date: Start date string
            end_date: End date string

        Returns:
            List[str]: List of date validation errors
        """
        errors = []

        if not start_date:
            errors.append("Start date is missing")
            return errors

        if not end_date:
            errors.append("End date is missing")
            return errors

        # Allow "Present", "Unknown" as end date
        if end_date.lower() in ['present', 'current', 'ongoing', 'unknown']:
            return errors
        
        # Allow "Unknown" as start date too
        if start_date.lower() == 'unknown':
            # If start is unknown, don't validate end date format either
            return errors

        # Basic date format validation
        if not self._is_valid_date_format(start_date):
            errors.append(f"Start date '{start_date}' format is not recognized")

        if not self._is_valid_date_format(end_date):
            errors.append(f"End date '{end_date}' format is not recognized")

        return errors

    def _is_valid_date_format(self, date_str: str) -> bool:
        """
        Check if date string follows common formats.

        Args:
            date_str: Date string to validate

        Returns:
            bool: True if format is recognized
        """
        if not date_str:
            return False

        # Common date patterns
        patterns = [
            r'^\d{4}$',  # 2020
            r'^\d{1,2}/\d{4}$',  # 1/2020, 12/2020
            r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$',  # January 2020
            r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$',  # Jan 2020
            r'^\d{4}-\d{2}$',  # 2020-01
        ]

        return any(re.match(pattern, date_str, re.IGNORECASE) for pattern in patterns)

    def _validate_phone_format(self, phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number string

        Returns:
            bool: True if format looks valid
        """
        # Remove all non-digit characters and check length
        digits = re.sub(r'\D', '', phone)
        return 10 <= len(digits) <= 15

    def validate_markdown_structure(self, markdown_content: str) -> ValidationResult:
        """
        Validate markdown structure before parsing.

        Args:
            markdown_content: Raw markdown content

        Returns:
            ValidationResult: Structure validation result
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check for basic structure
        if not markdown_content.strip():
            errors.append("Resume content is empty")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Check for headings
        headings = re.findall(r'^#+\s+(.+)$', markdown_content, re.MULTILINE)
        if len(headings) < 2:
            warnings.append("Resume should have multiple sections with headings")

        # Check for required sections (case insensitive)
        content_lower = markdown_content.lower()
        required_sections = ['experience', 'education']
        missing_sections = []

        for section in required_sections:
            if section not in content_lower:
                missing_sections.append(section)

        if missing_sections:
            warnings.append(f"Consider adding these sections: {', '.join(missing_sections)}")

        # Check for email
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', markdown_content):
            errors.append("Email address not found in resume")

        # Check minimum length
        if len(markdown_content) < 100:
            warnings.append("Resume content seems very short")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )