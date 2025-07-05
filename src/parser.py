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


class ATSRenderer(mistune.HTMLRenderer):
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

    def heading(self, text: str, level: int, **attrs) -> str:
        """
        Handle heading elements for section detection.

        Args:
            text: The heading text
            level: Heading level (1-6)
            **attrs: Additional attributes

        Returns:
            str: Processed heading text
        """
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
        return super().heading(text, level, **attrs)

    def paragraph(self, text: str) -> str:
        """
        Handle paragraph elements.

        Args:
            text: Paragraph text

        Returns:
            str: Processed paragraph text
        """
        if self.current_section and text.strip():
            self.current_section_content.append(text.strip())
        return super().paragraph(text)

    def list_item(self, text: str) -> str:
        """
        Handle list item elements for bullet extraction.

        Args:
            text: List item text

        Returns:
            str: Processed list item text
        """
        if self.current_section:
            # Clean up HTML tags and extract plain text
            import re
            # Remove HTML tags first
            cleaned_text = re.sub(r'<[^>]+>', '', text)
            # Clean up bullet point markers
            cleaned_text = re.sub(r'^[\s\-\*\+•]+', '', cleaned_text.strip())
            if cleaned_text:
                self.current_section_content.append(cleaned_text)
        return super().list_item(text)

    def link(self, link: str, text: str = None, title: str = None) -> str:
        """
        Handle link elements.

        Args:
            link: The URL
            text: Link text
            title: Link title

        Returns:
            str: Processed link
        """
        if self.current_section:
            link_text = text or link
            self.current_section_content.append(f"{link_text}: {link}")
        return super().link(link, text, title)

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
        
        # Extract email - support Unicode characters
        email_match = re.search(r'\b([\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,})\b', markdown_content, re.UNICODE)
        email = email_match.group(1) if email_match else None
        
        if not email:
            raise InvalidMarkdownError("Email address is required but not found")
        
        # Extract phone - be more specific to avoid matching dates
        phone_patterns = [
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # US phone
            r'\+\d{1,3}[-.\s]?\d{4,14}',  # International format
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # (555) 123-4567
        ]
        phone = None
        for pattern in phone_patterns:
            phone_match = re.search(pattern, markdown_content)
            if phone_match:
                phone = phone_match.group(0).strip()
                break
        
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
        # Look for experience section and subsections
        experience_section = sections.get('experience') or sections.get('work experience')
        if not experience_section:
            return []
        
        experiences = []
        
        # First, try to extract from the main experience section content
        content = experience_section.content
        
        # Also look for subsections that are experience entries (level 3 headings under experience)
        experience_subsections = []
        for section_name, section in sections.items():
            # Look for sections that could be experience subsections
            # Must be level 3 and contain job title keywords AND exclude education/certification keywords
            if (section.level == 3 and 
                any(keyword in section_name.lower() for keyword in ['developer', 'engineer', 'manager', 'analyst', 'director', 'lead', 'senior', 'junior', 'intern', 'consultant', 'specialist', 'coordinator', 'administrator']) and
                not any(exclude_keyword in section_name.lower() for exclude_keyword in ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'certified', 'certification', 'aws', 'google cloud', 'microsoft', 'cisco'])):
                experience_subsections.append((section_name, section))
        
        # If we found subsections, process them as individual experience entries
        if experience_subsections:
            for section_name, section in experience_subsections:
                exp_entry = self._parse_experience_from_subsection(section_name, section)
                if exp_entry:
                    experiences.append(exp_entry)
        else:
            # Fall back to parsing the main experience section content
            experiences = self._parse_experience_from_content(content)
        
        return experiences

    def _parse_experience_from_subsection(self, section_name: str, section: ResumeSection) -> Optional[Experience]:
        """Parse experience entry from a subsection."""
        # Extract title and company from section name
        title = "Unknown"
        company = "Unknown"
        start_date = None
        end_date = None
        
        # Try different formats: "Title at Company", "Title - Company", etc.
        if ' at ' in section_name:
            parts = section_name.split(' at ', 1)
            title = parts[0].strip().title()  # Convert to title case
            company = parts[1].strip().title()  # Convert to title case
        elif ' - ' in section_name:
            parts = section_name.split(' - ', 1)
            title = parts[0].strip().title()  # Convert to title case
            company = parts[1].strip().title()  # Convert to title case
        else:
            # Just use the section name as title
            title = section_name.title()
        
        # Extract bullets and look for dates in the content
        bullets = []
        for line in section.content:
            line = line.strip()
            if line:
                # Check if this line contains date information
                date_match = re.search(r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|Present|Current)', line, re.IGNORECASE)
                if date_match and not start_date:
                    start_date = date_match.group(1)
                    end_date = date_match.group(2)
                    continue  # Don't add this line as a bullet
                
                bullets.append(line)
        
        return Experience(
            title=title,
            company=company,
            start_date=start_date or "Unknown",
            end_date=end_date or "Unknown",
            bullets=bullets
        )
    
    def _parse_experience_from_content(self, content: List[str]) -> List[Experience]:
        """Parse experience entries from flat content list."""
        experiences = []
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
        
        # Look for education subsections (degree entries as separate sections)
        degree_sections = []
        for section_name, section in sections.items():
            # Check if this looks like a degree section
            if (section_name != 'education' and 
                any(keyword in section_name.lower() for keyword in 
                    ['bachelor', 'master', 'phd', 'ph.d', 'doctorate', 'associate', 'diploma', 'certificate', 'degree'])):
                degree_sections.append((section_name, section))
        
        # Process degree subsections
        for section_name, section in degree_sections:
            degree = section_name.title()  # Convert to title case
            
            # Extract school and other info from content
            school = 'Unknown'
            start_date = None
            end_date = None
            
            if section.content:
                # First line is usually school, second might be dates
                lines = []
                for item in section.content:
                    lines.extend(item.split('\n'))
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this looks like dates
                    if re.match(r'\d{4}[-–]\d{4}|\d{4}-Present|\d{4}', line):
                        if '-' in line or '–' in line:
                            parts = re.split(r'[-–]', line)
                            start_date = parts[0].strip()
                            end_date = parts[1].strip() if len(parts) > 1 else None
                        else:
                            start_date = line
                    elif not re.match(r'\d{4}', line):  # Not a year, likely school
                        school = line
            
            education_entries.append(Education(
                degree=degree,
                school=school,
                start_date=start_date,
                end_date=end_date
            ))
        
        # If no degree subsections found, try original approach
        if not education_entries:
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
        
        # First check if the main skills section has content
        if content:
            categories, raw_skills = self._parse_skills_from_content(content)
        
        # Also check for skills subsections (level 3 headings under skills)
        skills_subsections = []
        for section_name, section in sections.items():
            if (section.level == 3 and 
                section_name.lower() not in ['skills', 'technical skills'] and
                any(keyword in section_name.lower() for keyword in ['programming', 'languages', 'tools', 'frameworks', 'technologies', 'software'])):
                skills_subsections.append((section_name, section))
        
        # If we found subsections, process them as skill categories
        if skills_subsections:
            for section_name, section in skills_subsections:
                category_skills = []
                for line in section.content:
                    line = line.strip()
                    if line:
                        # Split by common separators
                        skill_items = [s.strip() for s in re.split(r'[,;•|]', line) if s.strip()]
                        category_skills.extend(skill_items)
                
                if category_skills:
                    # Remove colon from category name if present
                    category_name = section_name.rstrip(':')
                    categories.append(SkillCategory(
                        name=category_name,
                        skills=category_skills
                    ))
        
        if categories:
            return Skills(categories=categories)
        elif raw_skills:
            return Skills(raw_skills=raw_skills)
        else:
            return None
    
    def _parse_skills_from_content(self, content: List[str]) -> tuple[List[SkillCategory], List[str]]:
        """Parse skills from content lines."""
        categories = []
        raw_skills = []
        
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
        
        return categories, raw_skills

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
