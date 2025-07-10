"""
Configuration and fixtures for integration tests.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def integration_test_dir() -> Path:
    """Get the integration test directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def samples_directory() -> Path:
    """Get the samples directory for test resumes."""
    return Path(__file__).parent / "samples"