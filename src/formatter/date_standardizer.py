"""
Date standardization module for ATS compliance.

This module provides functionality to standardize various date formats
into ATS-compliant formats for optimal parsing.
"""

import re
from typing import Optional


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
