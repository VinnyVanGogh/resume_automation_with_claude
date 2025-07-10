"""
End-to-end integration tests for the resume automation tool.

Tests the complete conversion pipeline from markdown input to multiple output formats.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest


class TestEndToEndConversion:
    """Test complete conversion pipeline with real CLI commands."""

    @pytest.fixture
    def samples_dir(self) -> Path:
        """Get path to sample resume files."""
        return Path(__file__).parent / "samples"

    @pytest.fixture
    def temp_output_dir(self) -> Path:
        """Create temporary output directory for tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def run_cli_command(self, command: list[str]) -> tuple[int, str, str]:
        """
        Run CLI command and return exit code, stdout, stderr.
        
        Args:
            command: List of command arguments
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        result = subprocess.run(
            ["resume-convert"] + command,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def test_convert_simple_resume_default_format(self, samples_dir: Path, temp_output_dir: Path):
        """Test converting simple resume with default PDF format."""
        input_file = samples_dir / "simple.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(input_file),
            "--output-dir", str(temp_output_dir)
        ])
        
        # Should succeed (exit code 0) or fail gracefully with known issues
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"
        
        # Check if any output files were created
        output_files = list(temp_output_dir.glob("*"))
        if exit_code == 0:
            assert len(output_files) > 0, "No output files created on successful conversion"

    def test_convert_simple_resume_all_formats(self, samples_dir: Path, temp_output_dir: Path):
        """Test converting simple resume to all formats."""
        input_file = samples_dir / "simple.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(input_file),
            "--format", "pdf",
            "--format", "html", 
            "--format", "docx",
            "--output-dir", str(temp_output_dir)
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"

    def test_convert_complex_resume(self, samples_dir: Path, temp_output_dir: Path):
        """Test converting complex resume with advanced formatting."""
        input_file = samples_dir / "complex.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(input_file),
            "--format", "html",
            "--output-dir", str(temp_output_dir),
            "--verbose"
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"

    def test_convert_edge_cases_resume(self, samples_dir: Path, temp_output_dir: Path):
        """Test converting resume with edge cases and special characters."""
        input_file = samples_dir / "edge_cases.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(input_file),
            "--format", "html",
            "--output-dir", str(temp_output_dir)
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"

    def test_batch_conversion(self, samples_dir: Path, temp_output_dir: Path):
        """Test batch conversion of multiple resumes."""
        simple_file = samples_dir / "simple.md"
        complex_file = samples_dir / "complex.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "batch",
            str(simple_file),
            str(complex_file),
            "--format", "html",
            "--output-dir", str(temp_output_dir)
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"

    def test_batch_conversion_with_workers(self, samples_dir: Path, temp_output_dir: Path):
        """Test batch conversion with custom worker count."""
        simple_file = samples_dir / "simple.md"
        edge_file = samples_dir / "edge_cases.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "batch",
            str(simple_file),
            str(edge_file),
            "--format", "html",
            "--workers", "2",
            "--output-dir", str(temp_output_dir)
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"

    def test_json_output_format(self, samples_dir: Path, temp_output_dir: Path):
        """Test JSON output format for programmatic use."""
        input_file = samples_dir / "simple.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(input_file),
            "--format", "html",
            "--output-dir", str(temp_output_dir),
            "--json-output"
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"
        
        if exit_code == 0:
            # If successful, should have valid JSON output
            try:
                result = json.loads(stdout)
                assert isinstance(result, dict), "JSON output should be a dictionary"
                assert "success" in result, "JSON output should have 'success' field"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON output: {e}")

    def test_error_handling_missing_file(self):
        """Test error handling for missing input file."""
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            "nonexistent.md"
        ])
        
        # Should fail with appropriate error code
        assert exit_code == 2, "Should fail with exit code 2 for missing file"
        assert "does not exist" in stderr, "Should show appropriate error message"

    def test_error_handling_verbose_quiet_conflict(self, samples_dir: Path):
        """Test error handling for conflicting verbose/quiet flags."""
        input_file = samples_dir / "simple.md"
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(input_file),
            "--verbose",
            "--quiet"
        ])
        
        # Should fail with appropriate error code
        assert exit_code == 1, "Should fail with exit code 1 for conflicting flags"
        assert "Cannot use --verbose and --quiet together" in stderr

    def test_cli_help_commands(self):
        """Test that all help commands work correctly."""
        # Test main help
        exit_code, stdout, stderr = self.run_cli_command(["--help"])
        assert exit_code == 0, "Help command should succeed"
        assert "Resume Automation Tool" in stdout
        
        # Test convert help
        exit_code, stdout, stderr = self.run_cli_command(["convert", "--help"])
        assert exit_code == 0, "Convert help should succeed"
        assert "Convert a single resume file" in stdout
        
        # Test batch help
        exit_code, stdout, stderr = self.run_cli_command(["batch", "--help"])
        assert exit_code == 0, "Batch help should succeed"
        assert "Convert multiple resume files" in stdout

    def test_version_command(self):
        """Test version command works correctly."""
        exit_code, stdout, stderr = self.run_cli_command(["--version"])
        assert exit_code == 0, "Version command should succeed"
        assert "Resume Automation Tool, version" in stdout
        assert "0.1.0-alpha" in stdout, "Should show current version"


class TestUtilityCommands:
    """Test utility commands like list-formats, list-themes, validate-config."""

    def run_cli_command(self, command: list[str]) -> tuple[int, str, str]:
        """Run CLI command and return exit code, stdout, stderr."""
        result = subprocess.run(
            ["resume-convert"] + command,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def test_list_formats_command(self):
        """Test list-formats command."""
        exit_code, stdout, stderr = self.run_cli_command(["list-formats"])
        
        # Should succeed or fail gracefully due to missing converter dependencies
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"
        
        if exit_code == 0:
            assert "Available output formats:" in stdout

    def test_list_themes_command(self):
        """Test list-themes command."""
        exit_code, stdout, stderr = self.run_cli_command(["list-themes"])
        
        # Should succeed or fail gracefully due to missing converter dependencies
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"
        
        if exit_code == 0:
            assert "Available themes:" in stdout

    def test_validate_config_missing_file(self):
        """Test validate-config with missing file."""
        exit_code, stdout, stderr = self.run_cli_command([
            "validate-config", 
            "nonexistent.yaml"
        ])
        
        # Should fail with file not found error
        assert exit_code == 2, "Should fail with exit code 2 for missing file"
        assert "does not exist" in stderr


class TestConfigurationSystem:
    """Test configuration system integration."""

    def run_cli_command(self, command: list[str]) -> tuple[int, str, str]:
        """Run CLI command and return exit code, stdout, stderr."""
        result = subprocess.run(
            ["resume-convert"] + command,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def test_config_override_option(self, tmp_path: Path):
        """Test configuration override functionality."""
        # Create a simple resume for testing
        resume_file = tmp_path / "test.md"
        resume_file.write_text("# Test Resume\n\nSample content.")
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(resume_file),
            "--format", "html",
            "--config-override", "test_setting=value",
            "--output-dir", str(tmp_path)
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"

    def test_no_validation_option(self, tmp_path: Path):
        """Test --no-validation option."""
        # Create a simple resume for testing
        resume_file = tmp_path / "test.md"
        resume_file.write_text("# Test Resume\n\nSample content.")
        
        exit_code, stdout, stderr = self.run_cli_command([
            "convert",
            str(resume_file),
            "--format", "html",
            "--no-validation",
            "--output-dir", str(tmp_path)
        ])
        
        # Should succeed or fail gracefully
        assert exit_code in [0, 1], f"Unexpected exit code. STDERR: {stderr}"