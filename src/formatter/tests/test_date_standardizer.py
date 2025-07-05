"""
Tests for Date Standardizer module.

Comprehensive test suite for the DateStandardizer class ensuring proper
date format standardization for ATS compliance.
"""

import pytest
from src.formatter import DateStandardizer


class TestDateStandardizer:
    """Test suite for DateStandardizer class."""
    
    @pytest.fixture
    def date_standardizer(self) -> DateStandardizer:
        """Create DateStandardizer instance for testing."""
        return DateStandardizer()
    
    def test_standardize_full_month_names(self, date_standardizer) -> None:
        """Test standardization of full month names."""
        test_cases = [
            ("January 2020 - December 2021", "January 2020 - December 2021"),
            ("january 2020 - december 2021", "January 2020 - December 2021"),
            ("JANUARY 2020 - DECEMBER 2021", "January 2020 - December 2021"),
        ]
        
        for input_date, expected in test_cases:
            result = date_standardizer.standardize_date(input_date)
            assert result == expected
    
    def test_standardize_abbreviated_months(self, date_standardizer) -> None:
        """Test standardization of abbreviated month names."""
        test_cases = [
            ("Jan 2020 - Dec 2021", "January 2020 - December 2021"),
            ("Feb 2020 - Mar 2021", "February 2020 - March 2021"),
            ("Sep 2020 - Oct 2021", "September 2020 - October 2021"),
            ("Sept 2020 - Nov 2021", "September 2020 - November 2021"),
        ]
        
        for input_date, expected in test_cases:
            result = date_standardizer.standardize_date(input_date)
            assert result == expected
    
    def test_standardize_present_variations(self, date_standardizer) -> None:
        """Test standardization of present/current variations."""
        test_cases = [
            ("January 2020 - Present", "January 2020 - Present"),
            ("January 2020 - Current", "January 2020 - Present"),
            ("January 2020 - Now", "January 2020 - Present"),
            ("January 2020 - Ongoing", "January 2020 - Present"),
            ("January 2020 - Today", "January 2020 - Present"),
        ]
        
        for input_date, expected in test_cases:
            result = date_standardizer.standardize_date(input_date)
            assert result == expected
    
    def test_standardize_year_only_ranges(self, date_standardizer) -> None:
        """Test standardization of year-only date ranges."""
        test_cases = [
            ("2020 - 2021", "2020 - 2021"),
            ("2020 - Present", "2020 - Present"),
            ("2020 - Current", "2020 - Present"),
        ]
        
        for input_date, expected in test_cases:
            result = date_standardizer.standardize_date(input_date)
            assert result == expected
    
    def test_standardize_single_dates(self, date_standardizer) -> None:
        """Test standardization of single dates."""
        test_cases = [
            ("January 2020", "January 2020"),
            ("Jan 2020", "January 2020"),
            ("2020", "2020"),
        ]
        
        for input_date, expected in test_cases:
            result = date_standardizer.standardize_date(input_date)
            assert result == expected
    
    def test_standardize_different_separators(self, date_standardizer) -> None:
        """Test standardization with different date separators."""
        test_cases = [
            ("January 2020 – December 2021", "January 2020 - December 2021"),  # en dash
            ("January 2020 — December 2021", "January 2020 - December 2021"),  # em dash
            ("January 2020 - December 2021", "January 2020 - December 2021"),  # hyphen
        ]
        
        for input_date, expected in test_cases:
            result = date_standardizer.standardize_date(input_date)
            assert result == expected
    
    def test_standardize_empty_or_none_input(self, date_standardizer) -> None:
        """Test standardization with empty or None input."""
        assert date_standardizer.standardize_date("") == ""
        assert date_standardizer.standardize_date("   ") == "   "
        assert date_standardizer.standardize_date(None) is None
    
    def test_standardize_invalid_dates(self, date_standardizer) -> None:
        """Test standardization with invalid or unrecognized date formats."""
        invalid_dates = [
            "Some random text",
            "Not a date at all",
            "123-456-789",
        ]
        
        for invalid_date in invalid_dates:
            result = date_standardizer.standardize_date(invalid_date)
            # Should return the cleaned original if no pattern matches
            assert result == invalid_date
    
    def test_standardize_date_range_method(self, date_standardizer) -> None:
        """Test the standardize_date_range method."""
        start_date = "Jan 2020"
        end_date = "Dec 2021"
        
        standardized_start, standardized_end = date_standardizer.standardize_date_range(start_date, end_date)
        
        assert standardized_start == "January 2020"
        assert standardized_end == "December 2021"
    
    def test_validate_date_order_valid(self, date_standardizer) -> None:
        """Test date order validation with valid dates."""
        test_cases = [
            ("January 2020", "December 2021", True),
            ("2020", "2021", True),
            ("January 2020", "Present", True),
            ("2020", "Current", True),
            ("January 2021", "January 2021", True),  # Same year should be valid
        ]
        
        for start_date, end_date, expected in test_cases:
            result = date_standardizer.validate_date_order(start_date, end_date)
            assert result == expected
    
    def test_validate_date_order_invalid(self, date_standardizer) -> None:
        """Test date order validation with invalid dates."""
        test_cases = [
            ("December 2021", "January 2020", False),  # End before start
            ("2021", "2020", False),  # End year before start year
        ]
        
        for start_date, end_date, expected in test_cases:
            result = date_standardizer.validate_date_order(start_date, end_date)
            assert result == expected
    
    def test_validate_date_order_unparseable(self, date_standardizer) -> None:
        """Test date order validation with unparseable dates."""
        # Should return True (assume valid) if dates can't be parsed
        result = date_standardizer.validate_date_order("Not a date", "Also not a date")
        assert result is True
    
    def test_extract_year_valid(self, date_standardizer) -> None:
        """Test year extraction from valid date strings."""
        test_cases = [
            ("January 2020", 2020),
            ("Jan 2020 - Dec 2021", 2020),  # Should extract first year
            ("2020", 2020),
            ("Born in 1995", 1995),
        ]
        
        for date_str, expected_year in test_cases:
            result = date_standardizer._extract_year(date_str)
            assert result == expected_year
    
    def test_extract_year_invalid(self, date_standardizer) -> None:
        """Test year extraction from invalid date strings."""
        invalid_dates = [
            "No year here",
            "123",  # Too short to be a year
            "12345",  # Too long to be a year
            "",
            None,
        ]
        
        for invalid_date in invalid_dates:
            result = date_standardizer._extract_year(invalid_date)
            assert result is None
    
    def test_is_present_date(self, date_standardizer) -> None:
        """Test present date detection."""
        present_variations = ["present", "current", "now", "ongoing", "today"]
        
        for variation in present_variations:
            assert date_standardizer._is_present_date(variation) is True
            assert date_standardizer._is_present_date(variation.upper()) is True
            assert date_standardizer._is_present_date(variation.capitalize()) is True
        
        # Non-present dates
        non_present = ["December 2021", "2021", "Not present", ""]
        for non_present_date in non_present:
            assert date_standardizer._is_present_date(non_present_date) is False
    
    def test_standardize_month_mapping(self, date_standardizer) -> None:
        """Test individual month standardization."""
        test_cases = [
            ("jan", "January"),
            ("JAN", "January"),
            ("January", "January"),
            ("feb", "February"),
            ("sept", "September"),
            ("sep", "September"),
            ("december", "December"),
            ("unknown", "Unknown"),  # Should return title case if not found
        ]
        
        for input_month, expected in test_cases:
            result = date_standardizer._standardize_month(input_month)
            assert result == expected
    
    def test_edge_cases(self, date_standardizer) -> None:
        """Test edge cases and special scenarios."""
        # Dates with extra whitespace
        result = date_standardizer.standardize_date("  January 2020  -  December 2021  ")
        assert result == "January 2020 - December 2021"
        
        # Mixed case with spaces
        result = date_standardizer.standardize_date("jAnUaRy 2020 - dEcEmBeR 2021")
        assert result == "January 2020 - December 2021"
        
        # Date range without end year (should be handled gracefully)
        result = date_standardizer.standardize_date("January 2020 - December")
        assert "January 2020" in result
        assert "December" in result
    
    def test_format_matched_date_edge_cases(self, date_standardizer) -> None:
        """Test edge cases in date formatting."""
        # Test with different group lengths
        groups_1 = ("2020",)
        result = date_standardizer._format_matched_date(groups_1, "2020")
        assert result == "2020"
        
        # Test 3-group year format
        groups_3_year = ("2020", "2021", "present")
        result = date_standardizer._format_matched_date(groups_3_year, "2020-present")
        assert result == "2020 - Present"
        
        # Test 3-group month format
        groups_3_month = ("January", "2020", "present")
        result = date_standardizer._format_matched_date(groups_3_month, "January 2020-present")
        assert result == "January 2020 - Present"
    
    def test_validate_date_order_exception_handling(self, date_standardizer) -> None:
        """Test date order validation with exception cases."""
        # Should return True if any exception occurs during parsing
        result = date_standardizer.validate_date_order("invalid", "also invalid")
        assert result is True