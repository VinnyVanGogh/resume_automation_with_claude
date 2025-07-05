"""
Header standardization module for ATS compliance.

This module provides functionality to standardize section headers
into ATS-compliant formats for optimal parsing.
"""

from typing import List, Optional, Dict


class HeaderStandardizer:
    """
    Standardize section headers for ATS compliance.
    
    Maps common header variations to ATS-standard headers to ensure
    consistent parsing across different Applicant Tracking Systems.
    """
    
    def __init__(self) -> None:
        """Initialize header standardizer with mapping rules."""
        # Standard ATS headers
        self.standard_headers = {
            'summary': 'Summary',
            'experience': 'Experience',
            'education': 'Education',
            'skills': 'Skills',
            'certifications': 'Certifications',
            'projects': 'Projects',
            'contact': 'Contact Information'
        }
        
        # Header variations mapping to standard headers
        self.header_mappings = {
            # Summary variations
            'summary': {'summary', 'professional summary', 'executive summary', 'profile', 
                       'professional profile', 'career summary', 'overview', 'objective',
                       'career objective', 'professional objective'},
            
            # Experience variations
            'experience': {'experience', 'work experience', 'professional experience',
                          'employment', 'employment history', 'work history',
                          'career history', 'professional background', 'positions held',
                          'relevant experience'},
            
            # Education variations
            'education': {'education', 'academic background', 'academic history',
                         'educational background', 'academic qualifications',
                         'qualifications', 'academic credentials', 'degrees',
                         'education and training', 'formal education'},
            
            # Skills variations
            'skills': {'skills', 'technical skills', 'core competencies',
                      'competencies', 'areas of expertise', 'expertise',
                      'capabilities', 'proficiencies', 'technical proficiencies',
                      'key skills', 'skill set', 'technologies'},
            
            # Certifications variations
            'certifications': {'certifications', 'certificates', 'professional certifications',
                              'licenses', 'licenses and certifications', 'credentials',
                              'professional credentials', 'accreditations',
                              'professional development', 'training'},
            
            # Projects variations
            'projects': {'projects', 'key projects', 'notable projects',
                        'project experience', 'selected projects',
                        'project portfolio', 'accomplishments',
                        'key accomplishments', 'achievements'},
            
            # Contact variations
            'contact': {'contact', 'contact information', 'contact details',
                       'personal information', 'personal details', 'contact info'}
        }
        
        # Create reverse mapping for efficient lookup
        self.reverse_mapping: Dict[str, str] = {}
        for standard, variations in self.header_mappings.items():
            for variation in variations:
                self.reverse_mapping[variation.lower()] = standard
    
    def standardize_header(self, header: str) -> str:
        """
        Standardize a header to ATS-compliant format.
        
        Args:
            header: Header text to standardize
            
        Returns:
            Standardized header text
            
        Examples:
            "Work Experience" -> "Experience"
            "Professional Summary" -> "Summary"
            "Technical Skills" -> "Skills"
        """
        if not header:
            return header
        
        # Clean and normalize the header
        cleaned_header = self._clean_header(header)
        
        # Look up in mapping
        header_lower = cleaned_header.lower()
        if header_lower in self.reverse_mapping:
            standard_key = self.reverse_mapping[header_lower]
            return self.standard_headers[standard_key]
        
        # If no mapping found, return title case version
        return cleaned_header.title()
    
    def is_standard_header(self, header: str) -> bool:
        """
        Check if a header is already in standard format.
        
        Args:
            header: Header to check
            
        Returns:
            True if header is standard, False otherwise
        """
        return header in self.standard_headers.values()
    
    def get_header_category(self, header: str) -> Optional[str]:
        """
        Get the category of a header.
        
        Args:
            header: Header to categorize
            
        Returns:
            Category name or None if not recognized
        """
        header_lower = header.lower().strip()
        return self.reverse_mapping.get(header_lower)
    
    def _clean_header(self, header: str) -> str:
        """
        Clean header text for standardization.
        
        Args:
            header: Header text to clean
            
        Returns:
            Cleaned header text
        """
        # Remove extra whitespace
        cleaned = ' '.join(header.split())
        
        # Remove common punctuation that might interfere
        cleaned = cleaned.strip(':.-_')
        
        return cleaned
    
    def standardize_all_headers(self, headers: List[str]) -> List[str]:
        """
        Standardize a list of headers.
        
        Args:
            headers: List of headers to standardize
            
        Returns:
            List of standardized headers
        """
        return [self.standardize_header(header) for header in headers]
    
    def suggest_header_order(self, headers: List[str]) -> List[str]:
        """
        Suggest optimal header order for ATS parsing.
        
        Args:
            headers: List of headers
            
        Returns:
            Reordered list of headers in ATS-preferred order
        """
        # ATS-preferred order
        preferred_order = [
            'Contact Information',
            'Summary',
            'Experience',
            'Education',
            'Skills',
            'Projects',
            'Certifications'
        ]
        
        standardized = self.standardize_all_headers(headers)
        
        # Sort based on preferred order
        def order_key(header: str) -> int:
            try:
                return preferred_order.index(header)
            except ValueError:
                return len(preferred_order)  # Put unknown headers at the end
        
        return sorted(standardized, key=order_key)
