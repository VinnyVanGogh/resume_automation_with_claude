"""
File management utilities for the resume converter module.

This module provides advanced file handling, organization, naming strategies,
conflict resolution, and cleanup operations for conversion outputs.
"""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import os

from .exceptions import FileError
from .types import ConversionResult


logger = logging.getLogger(__name__)


@dataclass
class FileOrganizationStrategy:
    """
    Configuration for file organization strategy.
    
    Attributes:
        use_subdirectories: Whether to create subdirectories by format
        group_by_date: Whether to group files by date
        use_source_name: Whether to use source filename in output names
        add_timestamp: Whether to add timestamp to filenames
        preserve_structure: Whether to preserve input directory structure
    """
    use_subdirectories: bool = True
    group_by_date: bool = False
    use_source_name: bool = True
    add_timestamp: bool = False
    preserve_structure: bool = False


@dataclass
class NamingStrategy:
    """
    Configuration for file naming strategy.
    
    Attributes:
        prefix: Prefix for all generated files
        suffix: Suffix for all generated files
        include_format: Whether to include format in filename
        include_timestamp: Whether to include timestamp
        use_uuid: Whether to use UUID for uniqueness
        max_length: Maximum filename length
        replace_spaces: Whether to replace spaces with underscores
    """
    prefix: str = ""
    suffix: str = ""
    include_format: bool = False
    include_timestamp: bool = False
    use_uuid: bool = False
    max_length: int = 100
    replace_spaces: bool = True


@dataclass
class FileManagementReport:
    """
    Report of file management operations.
    
    Attributes:
        total_files: Total number of files processed
        created_files: Number of files created
        moved_files: Number of files moved
        deleted_files: Number of files deleted
        errors: List of errors encountered
        warnings: List of warnings
        operations: List of operations performed
    """
    total_files: int = 0
    created_files: int = 0
    moved_files: int = 0
    deleted_files: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)
    
    def add_operation(self, operation: str) -> None:
        """Add an operation to the report."""
        self.operations.append(operation)
        logger.debug(f"File operation: {operation}")
    
    def add_error(self, error: str) -> None:
        """Add an error to the report."""
        self.errors.append(error)
        logger.error(f"File management error: {error}")
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the report."""
        self.warnings.append(warning)
        logger.warning(f"File management warning: {warning}")


class FileManager:
    """
    Advanced file manager for resume conversion outputs.
    
    Provides file organization, naming strategies, conflict resolution,
    and cleanup operations with comprehensive reporting.
    """
    
    def __init__(
        self,
        base_output_dir: Union[str, Path],
        organization_strategy: Optional[FileOrganizationStrategy] = None,
        naming_strategy: Optional[NamingStrategy] = None,
        create_backups: bool = True,
        auto_cleanup: bool = False
    ) -> None:
        """
        Initialize the file manager.
        
        Args:
            base_output_dir: Base directory for all outputs
            organization_strategy: Strategy for organizing files
            naming_strategy: Strategy for naming files
            create_backups: Whether to create backups of existing files
            auto_cleanup: Whether to automatically cleanup temp files
        """
        self.base_output_dir = Path(base_output_dir)
        self.organization_strategy = organization_strategy or FileOrganizationStrategy()
        self.naming_strategy = naming_strategy or NamingStrategy()
        self.create_backups = create_backups
        self.auto_cleanup = auto_cleanup
        
        # Internal state
        self.temp_files: Set[Path] = set()
        self.created_directories: Set[Path] = set()
        self.backup_directory: Optional[Path] = None
        
        # Initialize base directory
        self._ensure_directory_exists(self.base_output_dir)
        
        logger.debug(f"FileManager initialized with base directory: {self.base_output_dir}")
    
    def organize_output_files(
        self,
        output_files: List[Path],
        source_file: Optional[Path] = None,
        custom_organization: Optional[FileOrganizationStrategy] = None
    ) -> Tuple[List[Path], FileManagementReport]:
        """
        Organize output files according to the organization strategy.
        
        Args:
            output_files: List of output files to organize
            source_file: Optional source file for organization context
            custom_organization: Optional custom organization strategy
            
        Returns:
            Tuple of (organized_file_paths, management_report)
        """
        report = FileManagementReport(total_files=len(output_files))
        strategy = custom_organization or self.organization_strategy
        organized_files = []
        
        try:
            for output_file in output_files:
                if not output_file.exists():
                    report.add_error(f"Output file does not exist: {output_file}")
                    continue
                
                # Determine target directory
                target_dir = self._determine_target_directory(
                    output_file, source_file, strategy
                )
                
                # Generate new filename
                new_filename = self._generate_filename(
                    output_file, source_file, target_dir
                )
                
                # Handle conflicts
                target_path = self._resolve_file_conflicts(
                    target_dir / new_filename, report
                )
                
                # Move file to target location
                if target_path != output_file:
                    organized_path = self._move_file_safely(
                        output_file, target_path, report
                    )
                    organized_files.append(organized_path)
                else:
                    organized_files.append(output_file)
                
                report.created_files += 1
                report.add_operation(f"Organized: {output_file.name} -> {target_path}")
        
        except Exception as e:
            error_msg = f"Failed to organize output files: {e}"
            report.add_error(error_msg)
            raise FileError(error_msg, operation="organize")
        
        return organized_files, report
    
    def _determine_target_directory(
        self,
        output_file: Path,
        source_file: Optional[Path],
        strategy: FileOrganizationStrategy
    ) -> Path:
        """Determine target directory based on organization strategy."""
        target_dir = self.base_output_dir
        
        # Add date-based subdirectory
        if strategy.group_by_date:
            date_str = datetime.now().strftime("%Y-%m-%d")
            target_dir = target_dir / date_str
        
        # Add source-based subdirectory
        if strategy.preserve_structure and source_file:
            relative_dir = source_file.parent.relative_to(source_file.parent.anchor)
            target_dir = target_dir / relative_dir
        
        # Add format-based subdirectory
        if strategy.use_subdirectories:
            format_type = self._detect_format(output_file)
            target_dir = target_dir / format_type
        
        # Ensure directory exists
        self._ensure_directory_exists(target_dir)
        
        return target_dir
    
    def _generate_filename(
        self,
        output_file: Path,
        source_file: Optional[Path],
        target_dir: Path
    ) -> str:
        """Generate filename based on naming strategy."""
        strategy = self.naming_strategy
        
        # Start with base name
        if strategy.use_source_name and source_file:
            base_name = source_file.stem
        else:
            base_name = output_file.stem
        
        # Add prefix
        if strategy.prefix:
            base_name = f"{strategy.prefix}_{base_name}"
        
        # Add format identifier
        if strategy.include_format:
            format_type = self._detect_format(output_file)
            base_name = f"{base_name}_{format_type}"
        
        # Add timestamp
        if strategy.include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{base_name}_{timestamp}"
        
        # Add suffix
        if strategy.suffix:
            base_name = f"{base_name}_{strategy.suffix}"
        
        # Add UUID for uniqueness
        if strategy.use_uuid:
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            base_name = f"{base_name}_{unique_id}"
        
        # Replace spaces if configured
        if strategy.replace_spaces:
            base_name = base_name.replace(" ", "_")
        
        # Truncate if too long
        if len(base_name) > strategy.max_length:
            base_name = base_name[:strategy.max_length]
        
        # Add original extension
        extension = output_file.suffix
        filename = f"{base_name}{extension}"
        
        return filename
    
    def _resolve_file_conflicts(
        self,
        target_path: Path,
        report: FileManagementReport
    ) -> Path:
        """Resolve filename conflicts."""
        if not target_path.exists():
            return target_path
        
        if self.create_backups:
            # Create backup of existing file
            backup_path = self._create_backup(target_path, report)
            if backup_path:
                report.add_operation(f"Created backup: {backup_path}")
            return target_path
        
        # Generate unique filename
        base = target_path.stem
        extension = target_path.suffix
        parent = target_path.parent
        counter = 1
        
        while target_path.exists():
            new_name = f"{base}_{counter:03d}{extension}"
            target_path = parent / new_name
            counter += 1
            
            if counter > 999:  # Prevent infinite loop
                raise FileError(f"Unable to resolve filename conflict for: {target_path}")
        
        report.add_warning(f"Renamed file to avoid conflict: {target_path.name}")
        return target_path
    
    def _create_backup(self, file_path: Path, report: FileManagementReport) -> Optional[Path]:
        """Create backup of existing file."""
        try:
            if not self.backup_directory:
                self.backup_directory = self.base_output_dir / "backups"
                self._ensure_directory_exists(self.backup_directory)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_directory / backup_name
            
            shutil.copy2(file_path, backup_path)
            return backup_path
            
        except Exception as e:
            report.add_error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def _move_file_safely(
        self,
        source_path: Path,
        target_path: Path,
        report: FileManagementReport
    ) -> Path:
        """Move file safely with error handling."""
        try:
            # Ensure target directory exists
            self._ensure_directory_exists(target_path.parent)
            
            # Move file
            shutil.move(str(source_path), str(target_path))
            report.moved_files += 1
            
            return target_path
            
        except Exception as e:
            error_msg = f"Failed to move file from {source_path} to {target_path}: {e}"
            report.add_error(error_msg)
            raise FileError(error_msg, file_path=str(source_path), operation="move")
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists, creating if necessary."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self.created_directories.add(directory)
            
        except Exception as e:
            raise FileError(
                f"Failed to create directory {directory}: {e}",
                file_path=str(directory),
                operation="create_directory"
            )
    
    def _detect_format(self, file_path: Path) -> str:
        """Detect file format from extension."""
        suffix = file_path.suffix.lower()
        format_map = {
            ".html": "html",
            ".htm": "html",
            ".pdf": "pdf", 
            ".docx": "docx",
            ".doc": "docx"
        }
        return format_map.get(suffix, "unknown")
    
    def create_temp_file(
        self,
        suffix: str = "",
        prefix: str = "resume_conv_",
        directory: Optional[Path] = None
    ) -> Path:
        """
        Create a temporary file for processing.
        
        Args:
            suffix: File suffix/extension
            prefix: Filename prefix
            directory: Optional directory for temp file
            
        Returns:
            Path to created temporary file
        """
        try:
            temp_dir = directory or (self.base_output_dir / "temp")
            self._ensure_directory_exists(temp_dir)
            
            # Create temporary file
            fd, temp_path = tempfile.mkstemp(
                suffix=suffix,
                prefix=prefix,
                dir=str(temp_dir)
            )
            os.close(fd)  # Close file descriptor
            
            temp_file = Path(temp_path)
            self.temp_files.add(temp_file)
            
            logger.debug(f"Created temporary file: {temp_file}")
            return temp_file
            
        except Exception as e:
            raise FileError(f"Failed to create temporary file: {e}", operation="create_temp")
    
    def cleanup_temp_files(self) -> FileManagementReport:
        """
        Clean up temporary files created during processing.
        
        Returns:
            FileManagementReport: Report of cleanup operations
        """
        report = FileManagementReport()
        
        for temp_file in list(self.temp_files):
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    report.deleted_files += 1
                    report.add_operation(f"Deleted temporary file: {temp_file}")
                
                self.temp_files.remove(temp_file)
                
            except Exception as e:
                report.add_error(f"Failed to delete temporary file {temp_file}: {e}")
        
        logger.info(f"Cleaned up {report.deleted_files} temporary files")
        return report
    
    def get_disk_usage(self) -> Dict[str, int]:
        """
        Get disk usage information for managed directories.
        
        Returns:
            Dictionary with disk usage information
        """
        usage_info = {}
        
        try:
            # Get usage for base directory
            usage_info["base_directory"] = self._get_directory_size(self.base_output_dir)
            
            # Get usage for subdirectories
            for subdir in self.created_directories:
                if subdir.exists() and subdir != self.base_output_dir:
                    rel_path = subdir.relative_to(self.base_output_dir)
                    usage_info[str(rel_path)] = self._get_directory_size(subdir)
            
        except Exception as e:
            logger.error(f"Failed to calculate disk usage: {e}")
        
        return usage_info
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass  # Skip files we can't access
        
        return total_size
    
    def validate_output_directory(self) -> List[str]:
        """
        Validate output directory configuration and permissions.
        
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check if directory exists
        if not self.base_output_dir.exists():
            issues.append(f"Output directory does not exist: {self.base_output_dir}")
            return issues
        
        # Check if it's actually a directory
        if not self.base_output_dir.is_dir():
            issues.append(f"Output path is not a directory: {self.base_output_dir}")
        
        # Check write permissions
        try:
            test_file = self.base_output_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception:
            issues.append(f"No write permission in output directory: {self.base_output_dir}")
        
        # Check available space
        try:
            stat = shutil.disk_usage(self.base_output_dir)
            available_mb = stat.free / (1024 * 1024)
            if available_mb < 100:  # Less than 100MB
                issues.append(f"Low disk space in output directory: {available_mb:.1f}MB available")
        except Exception:
            issues.append("Unable to check disk space")
        
        return issues
    
    def generate_file_manifest(self, files: List[Path]) -> Dict[str, Any]:
        """
        Generate manifest of managed files.
        
        Args:
            files: List of files to include in manifest
            
        Returns:
            Dictionary containing file manifest
        """
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "base_directory": str(self.base_output_dir),
            "total_files": len(files),
            "files": []
        }
        
        for file_path in files:
            if file_path.exists():
                file_info = {
                    "path": str(file_path),
                    "relative_path": str(file_path.relative_to(self.base_output_dir))
                                     if self.base_output_dir in file_path.parents
                                     else str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "format": self._detect_format(file_path),
                    "checksum": self._calculate_file_checksum(file_path)
                }
                manifest["files"].append(file_info)
        
        return manifest
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "unknown"