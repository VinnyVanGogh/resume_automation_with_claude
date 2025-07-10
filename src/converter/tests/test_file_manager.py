"""
Unit tests for the FileManager class.

Tests file management functionality including organization strategies,
naming conventions, conflict resolution, and cleanup operations.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ..exceptions import FileError
from ..file_manager import (
    FileManagementReport,
    FileManager,
    FileOrganizationStrategy,
    NamingStrategy,
)


class TestFileOrganizationStrategy:
    """Test FileOrganizationStrategy data class."""

    def test_default_organization_strategy(self):
        """Test default organization strategy values."""
        strategy = FileOrganizationStrategy()

        assert strategy.use_subdirectories is True
        assert strategy.group_by_date is False
        assert strategy.use_source_name is True
        assert strategy.add_timestamp is False
        assert strategy.preserve_structure is False

    def test_custom_organization_strategy(self):
        """Test custom organization strategy configuration."""
        strategy = FileOrganizationStrategy(
            use_subdirectories=False,
            group_by_date=True,
            use_source_name=False,
            add_timestamp=True,
            preserve_structure=True,
        )

        assert strategy.use_subdirectories is False
        assert strategy.group_by_date is True
        assert strategy.use_source_name is False
        assert strategy.add_timestamp is True
        assert strategy.preserve_structure is True


class TestNamingStrategy:
    """Test NamingStrategy data class."""

    def test_default_naming_strategy(self):
        """Test default naming strategy values."""
        strategy = NamingStrategy()

        assert strategy.prefix == ""
        assert strategy.suffix == ""
        assert strategy.include_format is False
        assert strategy.include_timestamp is False
        assert strategy.use_uuid is False
        assert strategy.max_length == 100
        assert strategy.replace_spaces is True

    def test_custom_naming_strategy(self):
        """Test custom naming strategy configuration."""
        strategy = NamingStrategy(
            prefix="resume",
            suffix="final",
            include_format=True,
            include_timestamp=True,
            use_uuid=True,
            max_length=50,
            replace_spaces=False,
        )

        assert strategy.prefix == "resume"
        assert strategy.suffix == "final"
        assert strategy.include_format is True
        assert strategy.include_timestamp is True
        assert strategy.use_uuid is True
        assert strategy.max_length == 50
        assert strategy.replace_spaces is False


class TestFileManagementReport:
    """Test FileManagementReport data class."""

    def test_default_report(self):
        """Test default report values."""
        report = FileManagementReport()

        assert report.total_files == 0
        assert report.created_files == 0
        assert report.moved_files == 0
        assert report.deleted_files == 0
        assert len(report.errors) == 0
        assert len(report.warnings) == 0
        assert len(report.operations) == 0

    def test_add_operation(self):
        """Test adding operations to report."""
        report = FileManagementReport()

        report.add_operation("Created directory: output/")
        report.add_operation("Moved file: test.html")

        assert len(report.operations) == 2
        assert "Created directory" in report.operations[0]
        assert "Moved file" in report.operations[1]

    def test_add_error(self):
        """Test adding errors to report."""
        report = FileManagementReport()

        report.add_error("Permission denied")
        report.add_error("File not found")

        assert len(report.errors) == 2
        assert "Permission denied" in report.errors
        assert "File not found" in report.errors

    def test_add_warning(self):
        """Test adding warnings to report."""
        report = FileManagementReport()

        report.add_warning("File already exists")
        report.add_warning("Large file size")

        assert len(report.warnings) == 2
        assert "File already exists" in report.warnings
        assert "Large file size" in report.warnings


class TestFileManagerInitialization:
    """Test FileManager initialization and setup."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_default_initialization(self):
        """Test file manager with default settings."""
        base_dir = self.temp_dir / "output"
        file_manager = FileManager(base_output_dir=base_dir)

        assert file_manager.base_output_dir == base_dir
        assert isinstance(file_manager.organization_strategy, FileOrganizationStrategy)
        assert isinstance(file_manager.naming_strategy, NamingStrategy)
        assert file_manager.create_backups is True
        assert file_manager.auto_cleanup is False

        # Base directory should be created
        assert base_dir.exists()

    def test_initialization_with_custom_strategies(self):
        """Test file manager with custom strategies."""
        base_dir = self.temp_dir / "custom_output"

        org_strategy = FileOrganizationStrategy(use_subdirectories=False)
        naming_strategy = NamingStrategy(prefix="test", include_timestamp=True)

        file_manager = FileManager(
            base_output_dir=base_dir,
            organization_strategy=org_strategy,
            naming_strategy=naming_strategy,
            create_backups=False,
            auto_cleanup=True,
        )

        assert file_manager.organization_strategy == org_strategy
        assert file_manager.naming_strategy == naming_strategy
        assert file_manager.create_backups is False
        assert file_manager.auto_cleanup is True

    def test_initialization_creates_base_directory(self):
        """Test that initialization creates base directory."""
        base_dir = self.temp_dir / "new_output"
        assert not base_dir.exists()

        file_manager = FileManager(base_output_dir=base_dir)

        assert base_dir.exists()
        assert base_dir.is_dir()


class TestFileManagerOrganization:
    """Test file organization functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_dir = self.temp_dir / "output"
        self.file_manager = FileManager(base_output_dir=self.base_dir)

        # Create test files
        self.test_files = []
        for i, ext in enumerate([".html", ".pdf", ".docx"]):
            file_path = self.temp_dir / f"resume_{i}{ext}"
            file_path.write_text(f"Test content {i}")
            self.test_files.append(file_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_organize_files_with_subdirectories(self):
        """Test organizing files with format subdirectories."""
        organized_files, report = self.file_manager.organize_output_files(
            output_files=self.test_files
        )

        assert len(organized_files) == 3
        assert report.total_files == 3
        assert report.created_files == 3
        assert len(report.errors) == 0

        # Verify files are organized into subdirectories
        for organized_file in organized_files:
            assert organized_file.parent != self.base_dir  # Should be in subdirectory
            assert organized_file.exists()

        # Verify subdirectories were created
        assert (self.base_dir / "html").exists()
        assert (self.base_dir / "pdf").exists()
        assert (self.base_dir / "docx").exists()

    def test_organize_files_without_subdirectories(self):
        """Test organizing files without subdirectories."""
        strategy = FileOrganizationStrategy(use_subdirectories=False)
        file_manager = FileManager(
            base_output_dir=self.base_dir, organization_strategy=strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=self.test_files
        )

        # All files should be in base directory
        for organized_file in organized_files:
            assert organized_file.parent == self.base_dir

    def test_organize_files_with_date_grouping(self):
        """Test organizing files with date grouping."""
        strategy = FileOrganizationStrategy(group_by_date=True)
        file_manager = FileManager(
            base_output_dir=self.base_dir, organization_strategy=strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=self.test_files
        )

        # Files should be in date subdirectory
        for organized_file in organized_files:
            # Should contain date string in path
            path_parts = organized_file.parts
            date_found = any("20" in part for part in path_parts)  # Look for year
            assert date_found

    def test_organize_files_with_source_context(self):
        """Test organizing files with source file context."""
        source_file = self.temp_dir / "john_doe_resume.md"
        source_file.write_text("# John Doe Resume")

        strategy = FileOrganizationStrategy(use_source_name=True)
        naming_strategy = NamingStrategy(prefix="converted")

        file_manager = FileManager(
            base_output_dir=self.base_dir,
            organization_strategy=strategy,
            naming_strategy=naming_strategy,
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=self.test_files, source_file=source_file
        )

        # Verify source name influence
        for organized_file in organized_files:
            # File names should reflect source context
            assert "converted" in organized_file.name.lower()

    def test_organize_nonexistent_files(self):
        """Test organizing non-existent files."""
        nonexistent_files = [
            self.temp_dir / "missing1.html",
            self.temp_dir / "missing2.pdf",
        ]

        organized_files, report = self.file_manager.organize_output_files(
            output_files=nonexistent_files
        )

        assert len(organized_files) == 0
        assert report.total_files == 2
        assert report.created_files == 0
        assert len(report.errors) == 2
        assert all("does not exist" in error for error in report.errors)


class TestFileManagerNaming:
    """Test file naming functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_dir = self.temp_dir / "output"

        # Create test file
        self.test_file = self.temp_dir / "sample resume.html"
        self.test_file.write_text("<html><body>Test</body></html>")

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_naming_with_prefix_suffix(self):
        """Test file naming with prefix and suffix."""
        naming_strategy = NamingStrategy(prefix="converted", suffix="final")

        file_manager = FileManager(
            base_output_dir=self.base_dir, naming_strategy=naming_strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        organized_file = organized_files[0]
        assert "converted" in organized_file.name
        assert "final" in organized_file.name
        assert organized_file.suffix == ".html"

    def test_naming_with_timestamp(self):
        """Test file naming with timestamp."""
        naming_strategy = NamingStrategy(include_timestamp=True)

        file_manager = FileManager(
            base_output_dir=self.base_dir, naming_strategy=naming_strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        organized_file = organized_files[0]
        # Should contain timestamp pattern (YYYYMMDD_HHMMSS)
        assert any(char.isdigit() for char in organized_file.stem)

    def test_naming_with_format_inclusion(self):
        """Test file naming with format inclusion."""
        naming_strategy = NamingStrategy(include_format=True)

        file_manager = FileManager(
            base_output_dir=self.base_dir, naming_strategy=naming_strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        organized_file = organized_files[0]
        assert "html" in organized_file.name.lower()

    def test_naming_space_replacement(self):
        """Test space replacement in file names."""
        naming_strategy = NamingStrategy(replace_spaces=True)

        file_manager = FileManager(
            base_output_dir=self.base_dir, naming_strategy=naming_strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        organized_file = organized_files[0]
        assert " " not in organized_file.name
        assert "_" in organized_file.name

    def test_naming_length_truncation(self):
        """Test filename length truncation."""
        naming_strategy = NamingStrategy(
            prefix="very_long_prefix_that_should_cause_truncation",
            suffix="very_long_suffix_that_should_also_cause_truncation",
            max_length=20,
        )

        file_manager = FileManager(
            base_output_dir=self.base_dir, naming_strategy=naming_strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        organized_file = organized_files[0]
        # Total filename (without extension) should be truncated
        assert len(organized_file.stem) <= 20

    @patch("uuid.uuid4")
    def test_naming_with_uuid(self, mock_uuid):
        """Test file naming with UUID."""
        mock_uuid.return_value.hex = "12345678abcdef"

        naming_strategy = NamingStrategy(use_uuid=True)

        file_manager = FileManager(
            base_output_dir=self.base_dir, naming_strategy=naming_strategy
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        organized_file = organized_files[0]
        assert "12345678" in organized_file.name


class TestFileManagerConflictResolution:
    """Test file conflict resolution functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_dir = self.temp_dir / "output"

        # Create test files
        self.test_file = self.temp_dir / "test.html"
        self.test_file.write_text("Test content")

        # Create existing file in output directory
        self.base_dir.mkdir(parents=True)
        self.existing_file = self.base_dir / "html" / "test.html"
        self.existing_file.parent.mkdir(parents=True)
        self.existing_file.write_text("Existing content")

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_conflict_resolution_with_backup(self):
        """Test conflict resolution with backup creation."""
        file_manager = FileManager(base_output_dir=self.base_dir, create_backups=True)

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        # Should have created backup
        backup_dir = self.base_dir / "backups"
        assert backup_dir.exists()

        # Should have backup file
        backup_files = list(backup_dir.glob("test_*.html"))
        assert len(backup_files) > 0

        # Original file should be replaced
        organized_file = organized_files[0]
        assert organized_file.read_text() == "Test content"

    def test_conflict_resolution_without_backup(self):
        """Test conflict resolution without backup creation."""
        file_manager = FileManager(base_output_dir=self.base_dir, create_backups=False)

        organized_files, report = file_manager.organize_output_files(
            output_files=[self.test_file]
        )

        # Should have created numbered file
        organized_file = organized_files[0]
        assert "_001" in organized_file.name or organized_file.name == "test.html"

        # Should have warning about rename
        if "_001" in organized_file.name:
            assert len(report.warnings) > 0
            assert any("conflict" in warning.lower() for warning in report.warnings)

    def test_multiple_conflict_resolution(self):
        """Test resolution of multiple conflicts."""
        # Create multiple files with same name
        test_files = []
        for i in range(3):
            file_path = self.temp_dir / f"duplicate_{i}.html"
            file_path.write_text(f"Content {i}")
            test_files.append(file_path)

        # Set all files to have same target name
        naming_strategy = NamingStrategy(prefix="same", suffix="name")

        file_manager = FileManager(
            base_output_dir=self.base_dir,
            naming_strategy=naming_strategy,
            create_backups=False,
        )

        organized_files, report = file_manager.organize_output_files(
            output_files=test_files
        )

        # Should have resolved all conflicts
        assert len(organized_files) == 3

        # Files should have different names
        organized_names = [f.name for f in organized_files]
        assert len(set(organized_names)) == 3  # All unique


class TestFileManagerUtilities:
    """Test file manager utility functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_dir = self.temp_dir / "output"
        self.file_manager = FileManager(base_output_dir=self.base_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_temp_file(self):
        """Test temporary file creation."""
        temp_file = self.file_manager.create_temp_file(suffix=".html", prefix="test_")

        assert temp_file.exists()
        assert temp_file.suffix == ".html"
        assert "test_" in temp_file.name
        assert temp_file in self.file_manager.temp_files

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        # Create multiple temp files
        temp_files = []
        for i in range(3):
            temp_file = self.file_manager.create_temp_file(suffix=f".test{i}")
            temp_files.append(temp_file)

        # Verify files exist
        assert all(f.exists() for f in temp_files)
        assert len(self.file_manager.temp_files) == 3

        # Cleanup
        report = self.file_manager.cleanup_temp_files()

        # Verify cleanup
        assert report.deleted_files == 3
        assert len(self.file_manager.temp_files) == 0
        assert not any(f.exists() for f in temp_files)

    def test_get_disk_usage(self):
        """Test disk usage calculation."""
        # Create some files with known sizes
        test_file1 = self.base_dir / "test1.txt"
        test_file1.write_text("x" * 1000)  # 1KB

        test_file2 = self.base_dir / "subdir" / "test2.txt"
        test_file2.parent.mkdir(parents=True)
        test_file2.write_text("y" * 2000)  # 2KB

        usage_info = self.file_manager.get_disk_usage()

        assert isinstance(usage_info, dict)
        assert "base_directory" in usage_info
        assert usage_info["base_directory"] >= 3000  # At least 3KB

    def test_validate_output_directory(self):
        """Test output directory validation."""
        issues = self.file_manager.validate_output_directory()

        # Should have no issues with valid directory
        assert isinstance(issues, list)
        assert len(issues) == 0

    def test_validate_output_directory_nonexistent(self):
        """Test validation of non-existent directory."""
        bad_file_manager = FileManager(base_output_dir="/nonexistent/path")

        # This should create the directory, but let's test with truly invalid path
        # by manually setting an invalid path after initialization
        bad_file_manager.base_output_dir = Path("/root/restricted/path")

        issues = bad_file_manager.validate_output_directory()

        assert len(issues) > 0

    def test_generate_file_manifest(self):
        """Test file manifest generation."""
        # Create test files
        test_files = []
        for i in range(3):
            file_path = self.base_dir / f"test_{i}.html"
            file_path.write_text(f"Content {i}")
            test_files.append(file_path)

        manifest = self.file_manager.generate_file_manifest(test_files)

        assert isinstance(manifest, dict)
        assert "generated_at" in manifest
        assert "base_directory" in manifest
        assert "total_files" in manifest
        assert "files" in manifest

        assert manifest["total_files"] == 3
        assert len(manifest["files"]) == 3

        # Verify file information
        for file_info in manifest["files"]:
            assert "path" in file_info
            assert "size" in file_info
            assert "format" in file_info
            assert "checksum" in file_info

    def test_calculate_file_checksum(self):
        """Test file checksum calculation."""
        test_file = self.base_dir / "checksum_test.txt"
        test_content = "This is test content for checksum calculation"
        test_file.write_text(test_content)

        checksum = self.file_manager._calculate_file_checksum(test_file)

        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hash length
        assert checksum != "unknown"

        # Same content should produce same checksum
        checksum2 = self.file_manager._calculate_file_checksum(test_file)
        assert checksum == checksum2


class TestFileManagerErrorHandling:
    """Test error handling in file manager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_dir = self.temp_dir / "output"
        self.file_manager = FileManager(base_output_dir=self.base_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_organize_files_error_handling(self):
        """Test error handling during file organization."""
        # Create a file that will cause issues during move
        problematic_file = self.temp_dir / "problem.html"
        problematic_file.write_text("Test content")

        # Mock shutil.move to raise an exception
        with patch("shutil.move", side_effect=PermissionError("Permission denied")):
            organized_files, report = self.file_manager.organize_output_files(
                output_files=[problematic_file]
            )

            assert len(organized_files) == 0
            assert len(report.errors) > 0
            assert any("permission" in error.lower() for error in report.errors)

    def test_backup_creation_error_handling(self):
        """Test error handling during backup creation."""
        # Create existing file
        existing_file = self.base_dir / "html" / "existing.html"
        existing_file.parent.mkdir(parents=True)
        existing_file.write_text("Existing content")

        # Create new file to organize
        new_file = self.temp_dir / "existing.html"
        new_file.write_text("New content")

        # Mock backup creation to fail
        with patch.object(self.file_manager, "_create_backup", return_value=None):
            organized_files, report = self.file_manager.organize_output_files(
                output_files=[new_file]
            )

            # Should still proceed despite backup failure
            assert len(organized_files) == 1

    def test_temp_file_creation_error(self):
        """Test error handling in temporary file creation."""
        # Mock tempfile.mkstemp to raise an exception
        with patch("tempfile.mkstemp", side_effect=OSError("Disk full")):
            with pytest.raises(FileError):
                self.file_manager.create_temp_file()

    def test_directory_creation_error(self):
        """Test error handling in directory creation."""
        # Try to create directory in non-existent parent
        with patch(
            "pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            with pytest.raises(FileError):
                self.file_manager._ensure_directory_exists(
                    Path("/root/restricted/new_dir")
                )


# Fixtures for pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def file_manager(temp_workspace):
    """Create a file manager with temporary workspace."""
    base_dir = temp_workspace / "output"
    return FileManager(base_output_dir=base_dir)


@pytest.fixture
def sample_output_files(temp_workspace):
    """Create sample output files for testing."""
    files = []

    # HTML file
    html_file = temp_workspace / "resume.html"
    html_file.write_text(
        """
<!DOCTYPE html>
<html>
<head><title>Resume</title></head>
<body><h1>John Doe</h1></body>
</html>
"""
    )
    files.append(html_file)

    # PDF file (mock)
    pdf_file = temp_workspace / "resume.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\nPDF content here")
    files.append(pdf_file)

    # DOCX file (mock)
    docx_file = temp_workspace / "resume.docx"
    docx_file.write_bytes(b"PK\x03\x04DOCX content here")
    files.append(docx_file)

    return files


@pytest.fixture
def custom_organization_strategy():
    """Create a custom organization strategy for testing."""
    return FileOrganizationStrategy(
        use_subdirectories=True,
        group_by_date=True,
        use_source_name=True,
        add_timestamp=False,
        preserve_structure=False,
    )


@pytest.fixture
def custom_naming_strategy():
    """Create a custom naming strategy for testing."""
    return NamingStrategy(
        prefix="converted",
        suffix="final",
        include_format=True,
        include_timestamp=True,
        use_uuid=False,
        max_length=100,
        replace_spaces=True,
    )
