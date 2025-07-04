"""
Markdown Resume Parser Module.

This module provides functionality to parse Markdown-formatted resumes
into structured data for further processing.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mistune

from .models import ResumeData, ContactInfo, Experience, Education, Skills, SkillCategory
from .types import InvalidMarkdownError
from .validation import ResumeValidator


@dataclass
class ResumeSection:
    """
    Represents a parsed resume section.

    Attributes:
        title: The section title/header
        content: List of content items in the section
        level: The heading level (1-6)
        metadata: Optional metadata dictionary
    """

    title: str
    content: list[str]
    level: int
    metadata: dict[str, str] | None = None


class ATSRenderer(mistune.BaseRenderer):
    """
    Custom Mistune renderer for ATS-compliant parsing.

    Renders markdown content optimized for ATS (Applicant Tracking System)
    compatibility and structured data extraction.
    """

    def __init__(self) -> None:
        """Initialize the ATS renderer."""
        super().__init__()
        self.sections: Dict[str, ResumeSection] = {}
        self.current_section: Optional[str] = None
        self.current_section_content: List[str] = []
        self.current_level: int = 0

    def heading(self, token: dict, state) -> str:
        """
        Handle heading elements for section detection.

        Args:
            token: Token containing heading data
            state: Parser state

        Returns:
            str: Processed heading text
        """
        text = token.get('raw', '')
        level = token.get('level', 1)
        
        # Save previous section if it exists
        if self.current_section:
            self.sections[self.current_section] = ResumeSection(
                title=self.current_section,
                content=self.current_section_content.copy(),
                level=self.current_level
            )

        # Start new section
        self.current_section = text.strip().lower()
        self.current_section_content = []
        self.current_level = level
        return text

    def paragraph(self, token: dict, state) -> str:
        """
        Handle paragraph elements.

        Args:
            token: Token containing paragraph data
            state: Parser state

        Returns:
            str: Processed paragraph text
        """
        text = token.get('raw', '')
        if self.current_section:
            self.current_section_content.append(text.strip())
        return text

    def list_item(self, token: dict, state) -> str:
        """
        Handle list item elements for bullet extraction.

        Args:
            token: Token containing list item data
            state: Parser state

        Returns:
            str: Processed list item text
        """
        text = token.get('raw', '')
        if self.current_section:
            # Clean up bullet point markers
            cleaned_text = re.sub(r'^[\s\-\*\+•]+', '', text.strip())
            if cleaned_text:
                self.current_section_content.append(cleaned_text)
        return text

    def link(self, token: dict, state) -> str:
        """
        Handle link elements.

        Args:
            token: Token containing link data
            state: Parser state

        Returns:
            str: Processed link
        """
        link = token.get('link', '')
        text = token.get('raw', '')
        if self.current_section:
            link_text = text or link
            self.current_section_content.append(f"{link_text}: {link}")
        return text or link

    def blank_line(self, token: dict, state) -> str:
        """Handle blank lines."""
        return ""

    def text(self, token: dict, state) -> str:
        """Handle plain text."""
        text = token.get('raw', '')
        if self.current_section:
            self.current_section_content.append(text.strip())
        return text

    def emphasis(self, token: dict, state) -> str:
        """Handle emphasized text."""
        return token.get('raw', '')

    def strong(self, token: dict, state) -> str:
        """Handle strong text."""
        return token.get('raw', '')

    def codespan(self, token: dict, state) -> str:
        """Handle inline code."""
        return token.get('raw', '')

    def linebreak(self, token: dict, state) -> str:
        """Handle line breaks."""
        return ""

    def softbreak(self, token: dict, state) -> str:
        """Handle soft breaks."""
        return " "

    def inline_html(self, token: dict, state) -> str:
        """Handle inline HTML."""
        return token.get('raw', '')

    def block_text(self, token: dict, state) -> str:
        """Handle block text."""
        text = token.get('raw', '')
        if self.current_section:
            self.current_section_content.append(text.strip())
        return text

    def block_code(self, token: dict, state) -> str:
        """Handle code blocks."""
        code = token.get('raw', '')
        if self.current_section:
            self.current_section_content.append(f"Code: {code.strip()}")
        return code

    def block_quote(self, token: dict, state) -> str:
        """Handle block quotes."""
        text = token.get('raw', '')
        if self.current_section:
            self.current_section_content.append(f"Quote: {text.strip()}")
        return text

    def list(self, token: dict, state) -> str:
        """Handle lists."""
        return token.get('raw', '')

    def thematic_break(self, token: dict, state) -> str:
        """Handle thematic breaks (horizontal rules)."""
        return ""

    def image(self, token: dict, state) -> str:
        """Handle images."""
        return token.get('alt', '') or token.get('src', '')

    def finalize_sections(self) -> Dict[str, ResumeSection]:
        """
        Finalize parsing and return all sections.

        Returns:
            Dict[str, ResumeSection]: All parsed sections
        """
        # Save the last section
        if self.current_section:
            self.sections[self.current_section] = ResumeSection(
                title=self.current_section,
                content=self.current_section_content.copy(),
                level=self.current_level
            )
        return self.sections


class MarkdownResumeParser:
    """
    Parse Markdown resume into structured data.

    Main parser class that coordinates the parsing of markdown resumes
    into structured ResumeData objects for further processing.
    """

    def __init__(self, validate_input: bool = True, strict_validation: bool = False) -> None:
        """
        Initialize the markdown parser with ATS renderer.

        Args:
            validate_input: Whether to validate markdown structure before parsing
            strict_validation: Enable strict validation rules
        """
        self.renderer = ATSRenderer()
        self.markdown = mistune.create_markdown(renderer=self.renderer)
        self.validator = ResumeValidator(strict_mode=strict_validation)
        self.validate_input = validate_input

    def parse(self, markdown_content: str, validate_result: bool = True) -> ResumeData:
        """
        Parse markdown content into structured resume data.

        Args:
            markdown_content: Raw markdown content of the resume
            validate_result: Whether to validate the parsed result

        Returns:
            ResumeData: Structured resume data model

        Raises:
            InvalidMarkdownError: If markdown structure is invalid or validation fails
        """
        try:
            # Validate input markdown structure if enabled
            if self.validate_input:
                structure_validation = self.validator.validate_markdown_structure(markdown_content)
                if not structure_validation.valid:
                    raise InvalidMarkdownError(
                        f"Invalid markdown structure: {'; '.join(structure_validation.errors)}"
                    )
            
            # Parse markdown content
            self.markdown(markdown_content)
            sections = self.renderer.finalize_sections()
            
            # Extract contact info from the top of the document
            contact_info = self._extract_contact_info(markdown_content, sections)
            
            # Extract structured sections
            experience = self._extract_experience(sections)
            education = self._extract_education(sections)
            skills = self._extract_skills(sections)
            summary = self._extract_summary(sections)
            
            # Create ResumeData
            resume_data = ResumeData(
                contact=contact_info,
                summary=summary,
                experience=experience,
                education=education,
                skills=skills
            )
            
            # Validate the parsed result if enabled
            if validate_result:
                validation_result = self.validator.validate_resume(resume_data)
                if not validation_result.valid:
                    raise InvalidMarkdownError(
                        f"Resume validation failed: {'; '.join(validation_result.errors)}"
                    )
            
            return resume_data
            
        except InvalidMarkdownError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            raise InvalidMarkdownError(f"Failed to parse markdown resume: {str(e)}") from e

    def parse_with_warnings(self, markdown_content: str) -> tuple[ResumeData, List[str]]:
        """
        Parse markdown content and return both data and validation warnings.

        Args:
            markdown_content: Raw markdown content of the resume

        Returns:
            tuple: (ResumeData, list of warning messages)

        Raises:
            InvalidMarkdownError: If parsing fails or critical validation errors occur
        """
        try:
            # Parse without result validation first
            resume_data = self.parse(markdown_content, validate_result=False)
            
            # Get full validation results including warnings
            validation_result = self.validator.validate_resume(resume_data)
            
            # Check for critical errors
            if not validation_result.valid:
                raise InvalidMarkdownError(
                    f"Resume validation failed: {'; '.join(validation_result.errors)}"
                )
            
            return resume_data, validation_result.warnings or []
            
        except Exception as e:
            raise InvalidMarkdownError(f"Failed to parse markdown resume: {str(e)}") from e

    def _extract_contact_info(self, markdown_content: str, sections: Dict[str, ResumeSection]) -> ContactInfo:
        """
        Extract contact information from resume.

        Args:
            markdown_content: Raw markdown content
            sections: Parsed sections

        Returns:
            ContactInfo: Contact information model
        """
        lines = markdown_content.split('\n')[:10]  # Check first 10 lines
        
        # Extract name (usually the first heading)
        name_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract email
        email_match = re.search(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', markdown_content)
        email = email_match.group(1) if email_match else None
        
        if not email:
            raise InvalidMarkdownError("Email address is required but not found")
        
        # Extract phone
        phone_match = re.search(r'(\+?[\d\s\-\(\)\.]{10,})', markdown_content)
        phone = phone_match.group(1).strip() if phone_match else None
        
        # Extract URLs (LinkedIn, GitHub, website)
        urls = re.findall(r'https?://[^\s\)]+', markdown_content)
        linkedin = next((url for url in urls if 'linkedin.com' in url), None)
        github = next((url for url in urls if 'github.com' in url), None)
        website = next((url for url in urls if url not in [linkedin, github]), None)
        
        return ContactInfo(
            name=name,
            email=email,
            phone=phone,
            linkedin=linkedin,
            github=github,
            website=website
        )

    def _extract_experience(self, sections: Dict[str, ResumeSection]) -> List[Experience]:
        """
        Extract work experience from sections.

        Args:
            sections: Parsed sections

        Returns:
            List[Experience]: List of experience entries
        """
        experience_section = sections.get('experience') or sections.get('work experience')
        if not experience_section:
            return []
        
        experiences = []
        content = experience_section.content
        
        # Group content by experience entries (assuming each starts with title/company)
        current_exp = {}
        for line in content:
            line = line.strip()
            if not line:
                continue
                
            # Check if this looks like a job title or company
            if re.match(r'^[A-Z][^.]+$', line) and not line.startswith('-'):
                # Save previous experience if exists
                if current_exp:
                    experiences.append(self._create_experience_from_dict(current_exp))
                
                # Start new experience
                if ' at ' in line or ' - ' in line:
                    # Format: "Title at Company" or "Title - Company"
                    parts = re.split(r' at | - ', line, 1)
                    current_exp = {
                        'title': parts[0].strip(),
                        'company': parts[1].strip() if len(parts) > 1 else line,
                        'bullets': []
                    }
                else:
                    current_exp = {
                        'title': line,
                        'company': 'Unknown',
                        'bullets': []
                    }
            elif line.startswith('-') or line.startswith('•'):
                # This is a bullet point
                if current_exp:
                    bullet = re.sub(r'^[-•]\s*', '', line)
                    current_exp['bullets'].append(bullet)
            elif current_exp and not current_exp.get('company'):
                # This might be the company name
                current_exp['company'] = line
        
        # Add the last experience
        if current_exp:
            experiences.append(self._create_experience_from_dict(current_exp))
        
        return experiences

    def _create_experience_from_dict(self, exp_dict: Dict[str, Any]) -> Experience:
        """Create Experience object from dictionary."""
        return Experience(
            title=exp_dict.get('title', 'Unknown'),
            company=exp_dict.get('company', 'Unknown'),
            start_date=exp_dict.get('start_date', 'Unknown'),
            end_date=exp_dict.get('end_date', 'Unknown'),
            bullets=exp_dict.get('bullets', [])
        )

    def _extract_education(self, sections: Dict[str, ResumeSection]) -> List[Education]:
        """
        Extract education from sections.

        Args:
            sections: Parsed sections

        Returns:
            List[Education]: List of education entries
        """
        education_section = sections.get('education')
        if not education_section:
            return []
        
        education_entries = []
        content = education_section.content
        
        current_edu = {}
        for line in content:
            line = line.strip()
            if not line:
                continue
            
            # Check if this looks like a degree or school
            if re.match(r'^[A-Z][^.]+$', line) and not line.startswith('-'):
                # Save previous education if exists
                if current_edu:
                    education_entries.append(self._create_education_from_dict(current_edu))
                
                # Start new education entry
                current_edu = {'degree': line}
            elif current_edu and not current_edu.get('school'):
                # This is likely the school name
                current_edu['school'] = line
        
        # Add the last education entry
        if current_edu:
            education_entries.append(self._create_education_from_dict(current_edu))
        
        return education_entries

    def _create_education_from_dict(self, edu_dict: Dict[str, Any]) -> Education:
        """Create Education object from dictionary."""
        return Education(
            degree=edu_dict.get('degree', 'Unknown'),
            school=edu_dict.get('school', 'Unknown'),
            start_date=edu_dict.get('start_date'),
            end_date=edu_dict.get('end_date')
        )

    def _extract_skills(self, sections: Dict[str, ResumeSection]) -> Optional[Skills]:
        """
        Extract skills from sections.

        Args:
            sections: Parsed sections

        Returns:
            Optional[Skills]: Skills model if found
        """
        skills_section = sections.get('skills') or sections.get('technical skills')
        if not skills_section:
            return None
        
        content = skills_section.content
        categories = []
        raw_skills = []
        
        current_category = None
        for line in content:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a category (contains colon)
            if ':' in line and not line.startswith('-'):
                parts = line.split(':', 1)
                category_name = parts[0].strip()
                skills_text = parts[1].strip()
                
                # Split skills by common separators
                skill_items = [s.strip() for s in re.split(r'[,;•|]', skills_text) if s.strip()]
                
                if skill_items:
                    categories.append(SkillCategory(
                        name=category_name,
                        skills=skill_items
                    ))
            else:
                # Add to raw skills
                if line.startswith('-') or line.startswith('•'):
                    skill = re.sub(r'^[-•]\s*', '', line)
                    raw_skills.append(skill)
                else:
                    raw_skills.append(line)
        
        if categories:
            return Skills(categories=categories)
        elif raw_skills:
            return Skills(raw_skills=raw_skills)
        else:
            return None

    def _extract_summary(self, sections: Dict[str, ResumeSection]) -> Optional[str]:
        """
        Extract summary/profile from sections.

        Args:
            sections: Parsed sections

        Returns:
            Optional[str]: Summary text if found
        """
        summary_section = (sections.get('summary') or 
                         sections.get('profile') or 
                         sections.get('about'))
        
        if summary_section and summary_section.content:
            return ' '.join(summary_section.content)
        
        return None
