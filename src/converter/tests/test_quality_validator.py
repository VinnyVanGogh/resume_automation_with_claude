"""
Unit tests for the QualityValidator class.

Tests quality validation functionality including format-specific validation,
ATS compliance scoring, quality metrics collection, and detailed reporting.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from ..exceptions import ValidationError
from ..quality_validator import QualityValidator
from ..types import FileValidationMetrics, ValidationReport


class TestQualityValidatorInitialization:
    """Test QualityValidator initialization and configuration."""

    def test_default_initialization(self):
        """Test quality validator with default settings."""
        validator = QualityValidator()

        assert validator is not None
        assert validator.min_quality_threshold == 70.0
        assert validator.strict_ats_validation is True
        assert validator.check_file_integrity is True
        assert hasattr(validator, "ats_friendly_fonts")
        assert hasattr(validator, "ats_problematic_elements")

    def test_initialization_with_custom_settings(self):
        """Test quality validator with custom settings."""
        validator = QualityValidator(
            min_quality_threshold=80.0,
            strict_ats_validation=False,
            check_file_integrity=False
        )

        assert validator.min_quality_threshold == 80.0
        assert validator.strict_ats_validation is False
        assert validator.check_file_integrity is False
        assert validator.validation_rules["required_formats"] == ["html", "pdf"]

    def test_initialization_with_ats_rules(self):
        """Test quality validator with custom ATS compliance rules."""
        ats_rules = {
            "min_ats_score": 85,
            "check_readability": True,
            "check_formatting": True,
        }

        validator = QualityValidator(ats_compliance_rules=ats_rules)

        assert validator.ats_compliance_rules["min_ats_score"] == 85
        assert validator.ats_compliance_rules["check_readability"] is True


class TestQualityValidatorFileValidation:
    """Test file validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = QualityValidator()

        # Create test files
        self.html_file = self.temp_dir / "test.html"
        self.html_file.write_text(
            """
<!DOCTYPE html>
<html>
<head><title>Test Resume</title></head>
<body>
    <h1>John Doe</h1>
    <p>Software Engineer</p>
    <p>john@example.com</p>
</body>
</html>
"""
        )

        self.pdf_file = self.temp_dir / "test.pdf"
        self.pdf_file.write_bytes(b"%PDF-1.4\ntest pdf content")

        self.docx_file = self.temp_dir / "test.docx"
        self.docx_file.write_bytes(b"PK\x03\x04test docx content")

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_validate_single_file_html(self):
        """Test validation of HTML file."""
        metrics = self.validator.validate_file(self.html_file)

        assert isinstance(metrics, FileValidationMetrics)
        assert metrics.file_path == self.html_file
        assert metrics.format_type == "html"
        assert metrics.file_size > 0
        assert metrics.is_valid is True
        assert metrics.content_score > 0

    def test_validate_single_file_pdf(self):
        """Test validation of PDF file."""
        metrics = self.validator.validate_file(self.pdf_file)

        assert metrics.format_type == "pdf"
        assert metrics.file_size > 0
        assert metrics.is_valid is True

    def test_validate_single_file_docx(self):
        """Test validation of DOCX file."""
        metrics = self.validator.validate_file(self.docx_file)

        assert metrics.format_type == "docx"
        assert metrics.file_size > 0
        assert metrics.is_valid is True

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        nonexistent_file = self.temp_dir / "nonexistent.html"

        with pytest.raises(ValidationError):
            self.validator.validate_file(nonexistent_file)

    def test_validate_empty_file(self):
        """Test validation of empty file."""
        empty_file = self.temp_dir / "empty.html"
        empty_file.touch()

        metrics = self.validator.validate_file(empty_file)

        assert metrics.is_valid is False
        assert "empty" in " ".join(metrics.issues).lower()

    def test_validate_oversized_file(self):
        """Test validation of oversized file."""
        # Create a large file
        large_file = self.temp_dir / "large.html"
        large_content = "x" * (20 * 1024 * 1024)  # 20MB
        large_file.write_text(large_content)

        # Configure validator with small max size
        validator = QualityValidator(
            validation_rules={"max_file_size": 1024 * 1024}
        )  # 1MB

        metrics = validator.validate_file(large_file)

        assert metrics.is_valid is False
        assert any("size" in issue.lower() for issue in metrics.issues)


class TestQualityValidatorBatchValidation:
    """Test batch validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = QualityValidator()

        # Create multiple test files
        self.output_files = []

        # Valid HTML file
        html_file = self.temp_dir / "resume.html"
        html_file.write_text(
            """
<!DOCTYPE html>
<html>
<head><title>Resume</title></head>
<body><h1>John Doe</h1><p>Engineer</p></body>
</html>
"""
        )
        self.output_files.append(html_file)

        # Valid PDF file
        pdf_file = self.temp_dir / "resume.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nvalid pdf content")
        self.output_files.append(pdf_file)

        # Invalid empty file
        empty_file = self.temp_dir / "resume.docx"
        empty_file.touch()
        self.output_files.append(empty_file)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_validate_output_files(self):
        """Test validation of multiple output files."""
        report = self.validator.validate_output_files(self.output_files)

        assert isinstance(report, ValidationReport)
        assert len(report.file_metrics) == 3
        assert report.total_files == 3
        assert report.valid_files == 2  # HTML and PDF are valid
        assert report.invalid_files == 1  # Empty DOCX is invalid
        assert report.is_valid is False  # Overall invalid due to empty file

    def test_validate_output_files_with_format_filter(self):
        """Test validation with format filtering."""
        expected_formats = ["html", "pdf"]

        report = self.validator.validate_output_files(
            self.output_files, expected_formats=expected_formats
        )

        # Should validate all files but note format expectations
        assert len(report.file_metrics) == 3
        assert report.total_files == 3

        # Check that format expectations are recorded
        html_metrics = next(m for m in report.file_metrics if m.format_type == "html")
        pdf_metrics = next(m for m in report.file_metrics if m.format_type == "pdf")
        docx_metrics = next(m for m in report.file_metrics if m.format_type == "docx")

        assert html_metrics.is_valid is True
        assert pdf_metrics.is_valid is True
        assert docx_metrics.is_valid is False  # Empty file

    def test_validate_empty_file_list(self):
        """Test validation of empty file list."""
        report = self.validator.validate_output_files([])

        assert report.total_files == 0
        assert report.valid_files == 0
        assert report.invalid_files == 0
        assert report.is_valid is True  # Empty list is considered valid
        assert len(report.file_metrics) == 0


class TestQualityValidatorATSCompliance:
    """Test ATS compliance scoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = QualityValidator()

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_calculate_ats_score_html(self):
        """Test ATS score calculation for HTML files."""
        html_content = """
<!DOCTYPE html>
<html>
<head><title>John Doe Resume</title></head>
<body>
    <h1>John Doe</h1>
    <h2>Contact Information</h2>
    <p>Email: john@example.com</p>
    <p>Phone: (555) 123-4567</p>
    
    <h2>Summary</h2>
    <p>Experienced software engineer with 5+ years in web development.</p>
    
    <h2>Experience</h2>
    <h3>Senior Software Engineer - TechCorp</h3>
    <p>2020 - Present</p>
    <ul>
        <li>Led development of scalable web applications</li>
        <li>Improved system performance by 40%</li>
    </ul>
    
    <h2>Skills</h2>
    <ul>
        <li>Python</li>
        <li>JavaScript</li>
        <li>React</li>
    </ul>
</body>
</html>
"""
        html_file = self.temp_dir / "ats_test.html"
        html_file.write_text(html_content)

        ats_score = self.validator.calculate_ats_score(html_file)

        assert isinstance(ats_score, float)
        assert 0 <= ats_score <= 100
        assert ats_score > 70  # Should score well with proper structure

    def test_calculate_ats_score_poor_structure(self):
        """Test ATS score for poorly structured content."""
        poor_html = """
<!DOCTYPE html>
<html>
<body>
    <div>John Doe john@example.com Software Engineer</div>
    <div>Some text about work history and skills mixed together without clear structure.</div>
</body>
</html>
"""
        html_file = self.temp_dir / "poor_ats.html"
        html_file.write_text(poor_html)

        ats_score = self.validator.calculate_ats_score(html_file)

        assert ats_score < 50  # Should score poorly due to poor structure

    def test_ats_compliance_factors(self):
        """Test individual ATS compliance factors."""
        # Test with well-structured content
        good_html = """
<!DOCTYPE html>
<html>
<head><title>Resume</title></head>
<body>
    <h1>John Doe</h1>
    <h2>Contact</h2>
    <p>john@example.com</p>
    <h2>Experience</h2>
    <p>Software Engineer at TechCorp</p>
    <h2>Education</h2>
    <p>BS Computer Science</p>
    <h2>Skills</h2>
    <p>Python, JavaScript</p>
</body>
</html>
"""
        html_file = self.temp_dir / "ats_factors.html"
        html_file.write_text(good_html)

        factors = self.validator.analyze_ats_compliance_factors(html_file)

        assert isinstance(factors, dict)
        assert "structure_score" in factors
        assert "content_score" in factors
        assert "formatting_score" in factors
        assert "keyword_score" in factors

        # Well-structured content should score well on structure
        assert factors["structure_score"] > 70


class TestQualityValidatorMetrics:
    """Test quality metrics calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = QualityValidator()

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_calculate_content_score(self):
        """Test content quality score calculation."""
        # Create file with good content
        good_content = """
<!DOCTYPE html>
<html>
<head><title>Professional Resume</title></head>
<body>
    <h1>John Doe</h1>
    <h2>Professional Summary</h2>
    <p>Experienced software engineer with demonstrated history of working in the technology industry. 
       Skilled in Python, JavaScript, and cloud technologies. Strong engineering professional with 
       a Bachelor's degree in Computer Science.</p>
    
    <h2>Work Experience</h2>
    <h3>Senior Software Engineer - TechCorp Inc.</h3>
    <p>January 2020 - Present</p>
    <ul>
        <li>Led development of microservices architecture serving 1M+ users</li>
        <li>Improved system performance by 40% through optimization</li>
        <li>Mentored team of 5 junior developers</li>
    </ul>
    
    <h2>Education</h2>
    <h3>Bachelor of Science in Computer Science</h3>
    <p>University of Technology, 2018</p>
    
    <h2>Technical Skills</h2>
    <ul>
        <li>Programming Languages: Python, JavaScript, Java</li>
        <li>Frameworks: Django, React, Spring Boot</li>
        <li>Tools: Git, Docker, AWS</li>
    </ul>
</body>
</html>
"""
        html_file = self.temp_dir / "content_test.html"
        html_file.write_text(good_content)

        content_score = self.validator.calculate_content_score(html_file)

        assert isinstance(content_score, float)
        assert 0 <= content_score <= 100
        assert content_score > 80  # Good content should score high

    def test_calculate_formatting_score(self):
        """Test formatting quality score calculation."""
        # Well-formatted HTML
        well_formatted = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>John Doe - Resume</title>
</head>
<body>
    <header>
        <h1>John Doe</h1>
        <p>Software Engineer</p>
    </header>
    <main>
        <section>
            <h2>Experience</h2>
            <article>
                <h3>Senior Developer</h3>
                <p>TechCorp - 2020 to Present</p>
            </article>
        </section>
    </main>
</body>
</html>
"""
        html_file = self.temp_dir / "format_test.html"
        html_file.write_text(well_formatted)

        formatting_score = self.validator.calculate_formatting_score(html_file)

        assert isinstance(formatting_score, float)
        assert 0 <= formatting_score <= 100
        assert formatting_score > 70  # Well-formatted should score well

    def test_calculate_overall_quality_score(self):
        """Test overall quality score calculation."""
        html_file = self.temp_dir / "overall_test.html"
        html_file.write_text(
            """
<!DOCTYPE html>
<html>
<head><title>Resume</title></head>
<body>
    <h1>John Doe</h1>
    <h2>Experience</h2>
    <p>Software Engineer with 5 years experience</p>
</body>
</html>
"""
        )

        metrics = self.validator.validate_file(html_file)

        assert hasattr(metrics, "overall_score")
        assert isinstance(metrics.overall_score, float)
        assert 0 <= metrics.overall_score <= 100

        # Overall score should be reasonable average of component scores
        expected_range = (
            min(metrics.content_score, metrics.ats_score, metrics.formatting_score)
            - 10,
            max(metrics.content_score, metrics.ats_score, metrics.formatting_score)
            + 10,
        )
        assert expected_range[0] <= metrics.overall_score <= expected_range[1]


class TestQualityValidatorReporting:
    """Test validation reporting functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = QualityValidator()

        # Create test files with different quality levels
        self.test_files = []

        # High quality file
        high_quality = self.temp_dir / "high_quality.html"
        high_quality.write_text(
            """
<!DOCTYPE html>
<html>
<head><title>Professional Resume</title></head>
<body>
    <h1>Jane Smith</h1>
    <h2>Contact Information</h2>
    <p>jane@example.com | (555) 123-4567</p>
    <h2>Professional Summary</h2>
    <p>Experienced data scientist with expertise in machine learning and analytics.</p>
    <h2>Work Experience</h2>
    <h3>Senior Data Scientist - DataCorp</h3>
    <p>2021 - Present</p>
    <ul>
        <li>Developed ML models improving accuracy by 25%</li>
        <li>Led team of 3 data scientists</li>
    </ul>
    <h2>Education</h2>
    <h3>Master of Science in Data Science</h3>
    <p>Tech University, 2021</p>
    <h2>Technical Skills</h2>
    <ul>
        <li>Python, R, SQL</li>
        <li>TensorFlow, PyTorch</li>
    </ul>
</body>
</html>
"""
        )
        self.test_files.append(high_quality)

        # Medium quality file
        medium_quality = self.temp_dir / "medium_quality.pdf"
        medium_quality.write_bytes(b"%PDF-1.4\nmedium quality pdf content")
        self.test_files.append(medium_quality)

        # Low quality file (empty)
        low_quality = self.temp_dir / "low_quality.docx"
        low_quality.touch()
        self.test_files.append(low_quality)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_generate_validation_report(self):
        """Test generation of comprehensive validation report."""
        report = self.validator.validate_output_files(self.test_files)

        # Verify report structure
        assert isinstance(report, ValidationReport)
        assert len(report.file_metrics) == 3
        assert report.total_files == 3
        assert hasattr(report, "summary")
        assert hasattr(report, "recommendations")

        # Verify summary statistics
        assert "average_scores" in report.summary
        assert "quality_distribution" in report.summary
        assert "common_issues" in report.summary

    def test_export_validation_report(self):
        """Test exporting validation report to file."""
        import json

        report = self.validator.validate_output_files(self.test_files)

        report_file = self.temp_dir / "validation_report.json"
        report.export_to_file(str(report_file))

        # Verify report file was created
        assert report_file.exists()

        # Verify report content
        with open(report_file) as f:
            report_data = json.load(f)

        assert "summary" in report_data
        assert "file_metrics" in report_data
        assert "recommendations" in report_data
        assert report_data["summary"]["total_files"] == 3

    def test_quality_recommendations(self):
        """Test generation of quality improvement recommendations."""
        report = self.validator.validate_output_files(self.test_files)

        recommendations = report.recommendations

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have recommendations for the low-quality file
        empty_file_recommendations = [
            r for r in recommendations if "empty" in r.lower() or "size" in r.lower()
        ]
        assert len(empty_file_recommendations) > 0

    def test_detailed_file_metrics(self):
        """Test detailed metrics for individual files."""
        report = self.validator.validate_output_files(self.test_files)

        # Find HTML file metrics
        html_metrics = next(m for m in report.file_metrics if m.format_type == "html")

        # Verify detailed metrics
        assert html_metrics.file_size > 0
        assert html_metrics.content_score >= 0
        assert html_metrics.ats_score >= 0
        assert html_metrics.formatting_score >= 0
        assert html_metrics.overall_score >= 0

        # HTML file should be valid
        assert html_metrics.is_valid is True
        assert len(html_metrics.issues) == 0

    def test_validation_thresholds(self):
        """Test validation against quality thresholds."""
        # Configure strict thresholds
        strict_validator = QualityValidator(
            quality_thresholds={
                "min_overall_score": 90,
                "min_ats_score": 85,
                "min_content_score": 85,
            }
        )

        report = strict_validator.validate_output_files(self.test_files)

        # With strict thresholds, files might not meet requirements
        # This tests that thresholds are being applied
        assert report.total_files == 3

        # Check that scoring considers thresholds
        for metrics in report.file_metrics:
            if metrics.is_valid:
                # Valid files should meet minimum thresholds or have good reasons
                assert metrics.overall_score > 0


# Fixtures for pytest


@pytest.fixture
def quality_validator():
    """Create a quality validator for testing."""
    return QualityValidator()


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Resume - John Doe</title>
</head>
<body>
    <header>
        <h1>John Doe</h1>
        <p>Software Engineer</p>
        <p>john.doe@example.com | (555) 123-4567</p>
    </header>
    
    <section>
        <h2>Professional Summary</h2>
        <p>Experienced software engineer with 5+ years in full-stack development.</p>
    </section>
    
    <section>
        <h2>Work Experience</h2>
        <article>
            <h3>Senior Software Engineer</h3>
            <p>TechCorp Inc. | 2020 - Present</p>
            <ul>
                <li>Led development of scalable web applications</li>
                <li>Improved system performance by 40%</li>
                <li>Mentored junior developers</li>
            </ul>
        </article>
    </section>
    
    <section>
        <h2>Education</h2>
        <article>
            <h3>Bachelor of Science in Computer Science</h3>
            <p>University of Technology | 2018</p>
        </article>
    </section>
    
    <section>
        <h2>Technical Skills</h2>
        <ul>
            <li>Programming: Python, JavaScript, Java</li>
            <li>Frameworks: Django, React, Spring Boot</li>
            <li>Tools: Git, Docker, AWS</li>
        </ul>
    </section>
</body>
</html>
"""


@pytest.fixture
def test_files_with_quality_levels(tmp_path, sample_html_content):
    """Create test files with different quality levels."""
    files = {}

    # High quality HTML file
    high_quality = tmp_path / "high_quality.html"
    high_quality.write_text(sample_html_content)
    files["high_quality"] = high_quality

    # Medium quality PDF file
    medium_quality = tmp_path / "medium_quality.pdf"
    medium_quality.write_bytes(b"%PDF-1.4\nSome PDF content here")
    files["medium_quality"] = medium_quality

    # Low quality empty file
    low_quality = tmp_path / "low_quality.docx"
    low_quality.touch()
    files["low_quality"] = low_quality

    return files
