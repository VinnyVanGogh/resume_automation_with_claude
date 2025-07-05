"""
Configuration module for ATS formatting.

This module provides configuration classes for controlling ATS formatting behavior.
"""

from typing import List, Optional
from dataclasses import dataclass


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
