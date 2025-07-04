"""
Pydantic models for resume data structures.

This module defines the data models used throughout the resume
automation pipeline for type-safe data handling.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class ContactInfo(BaseModel):
    """
    Contact information for the resume.

    Attributes:
        name: Full name of the person
        email: Email address
        phone: Phone number (optional)
        linkedin: LinkedIn profile URL (optional)
        github: GitHub profile URL (optional)
        website: Personal website URL (optional)
        location: City, State/Country (optional)
    """

    name: str = Field(..., min_length=1, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github: Optional[HttpUrl] = Field(None, description="GitHub profile URL")
    website: Optional[HttpUrl] = Field(None, description="Personal website URL")
    location: Optional[str] = Field(None, description="Location (City, State/Country)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        # Remove common separators and validate length
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone number must be between 10-15 digits")
        return v


class Experience(BaseModel):
    """
    Work experience entry.

    Attributes:
        title: Job title/position
        company: Company name
        start_date: Start date (can be string like "January 2020")
        end_date: End date or "Present"
        location: Job location (optional)
        bullets: List of accomplishment bullets
    """

    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date or 'Present'")
    location: Optional[str] = Field(None, description="Job location")
    bullets: list[str] = Field(
        default_factory=list, description="Accomplishment bullets"
    )

    @field_validator("bullets")
    @classmethod
    def validate_bullets(cls, v: list[str]) -> list[str]:
        """Ensure bullets are non-empty strings."""
        return [b.strip() for b in v if b.strip()]


class Education(BaseModel):
    """
    Education entry.

    Attributes:
        degree: Degree or certification name
        school: School/institution name
        start_date: Start date (optional)
        end_date: End date or expected graduation
        location: School location (optional)
        gpa: GPA if notable (optional)
        honors: Honors or achievements (optional)
        coursework: Relevant coursework (optional)
    """

    degree: str = Field(..., min_length=1, description="Degree name")
    school: str = Field(..., min_length=1, description="School name")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date or expected")
    location: Optional[str] = Field(None, description="School location")
    gpa: Optional[str] = Field(None, description="GPA if notable")
    honors: Optional[list[str]] = Field(None, description="Honors/achievements")
    coursework: Optional[list[str]] = Field(None, description="Relevant coursework")


class SkillCategory(BaseModel):
    """
    A category of skills.

    Attributes:
        name: Category name (e.g., "Languages", "Frameworks")
        skills: List of skills in this category
    """

    name: str = Field(..., min_length=1, description="Category name")
    skills: list[str] = Field(..., description="Skills in category")

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: list[str]) -> list[str]:
        """Ensure skills are non-empty strings."""
        return [s.strip() for s in v if s.strip()]


class Skills(BaseModel):
    """
    Skills section containing categorized skills.

    Attributes:
        categories: List of skill categories
        raw_skills: Alternative flat list of skills (optional)
    """

    categories: Optional[list[SkillCategory]] = Field(
        None, description="Categorized skills"
    )
    raw_skills: Optional[list[str]] = Field(None, description="Flat list of skills")

    @field_validator("raw_skills")
    @classmethod
    def validate_raw_skills(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Ensure raw skills are non-empty strings."""
        if v is None:
            return v
        return [s.strip() for s in v if s.strip()]

    def has_skills(self) -> bool:
        """Check if any skills are defined."""
        return bool(self.categories or self.raw_skills)


class Project(BaseModel):
    """
    Project entry (optional section).

    Attributes:
        name: Project name
        description: Brief description
        technologies: Technologies used
        bullets: Achievement bullets
        url: Project URL (optional)
        date: Project date or date range (optional)
    """

    name: str = Field(..., min_length=1, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    technologies: Optional[list[str]] = Field(None, description="Technologies used")
    bullets: Optional[list[str]] = Field(None, description="Project highlights")
    url: Optional[HttpUrl] = Field(None, description="Project URL")
    date: Optional[str] = Field(None, description="Project date/timeframe")


class Certification(BaseModel):
    """
    Professional certification.

    Attributes:
        name: Certification name
        issuer: Issuing organization
        date: Date obtained
        expiry: Expiry date (optional)
        credential_id: Credential ID (optional)
    """

    name: str = Field(..., min_length=1, description="Certification name")
    issuer: str = Field(..., min_length=1, description="Issuing organization")
    date: str = Field(..., description="Date obtained")
    expiry: Optional[str] = Field(None, description="Expiry date")
    credential_id: Optional[str] = Field(None, description="Credential ID")


class ResumeData(BaseModel):
    """
    Complete resume data model.

    This is the root model containing all resume sections.

    Attributes:
        contact: Contact information (required)
        summary: Professional summary (optional)
        experience: Work experience entries
        education: Education entries
        skills: Skills section
        projects: Project entries (optional)
        certifications: Professional certifications (optional)
        additional_sections: Any additional custom sections
    """

    contact: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(None, description="Professional summary")
    experience: list[Experience] = Field(
        default_factory=list, description="Work experience"
    )
    education: list[Education] = Field(
        default_factory=list, description="Education entries"
    )
    skills: Optional[Skills] = Field(None, description="Skills section")
    projects: Optional[list[Project]] = Field(None, description="Projects")
    certifications: Optional[list[Certification]] = Field(
        None, description="Certifications"
    )
    additional_sections: Optional[dict[str, list[str]]] = Field(
        None, description="Additional custom sections"
    )

    def get_all_sections(self) -> list[str]:
        """Get list of all populated section names."""
        sections = ["contact"]
        if self.summary:
            sections.append("summary")
        if self.experience:
            sections.append("experience")
        if self.education:
            sections.append("education")
        if self.skills and self.skills.has_skills():
            sections.append("skills")
        if self.projects:
            sections.append("projects")
        if self.certifications:
            sections.append("certifications")
        if self.additional_sections:
            sections.extend(self.additional_sections.keys())
        return sections

    class Config:
        """Pydantic config."""

        json_encoders = {HttpUrl: str}