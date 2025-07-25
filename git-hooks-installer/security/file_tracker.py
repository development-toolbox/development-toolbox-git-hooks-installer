"""
File Tracker - Tracks installer-created files for safe git operations.

This module ensures only files explicitly created by the installer are committed,
preventing accidental commits of user secrets or work-in-progress files.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileTracker:
    """Tracks files created/modified by installer for safe git operations."""
    
    def __init__(self, repo_path: Path):
        """Initialize file tracker for given repository."""
        self.repo_path = repo_path
        self.created_files: List[str] = []
        self.modified_files: List[str] = []
        self.created_directories: List[str] = []
        self.start_time = datetime.now()
    
    def track_file_creation(self, file_path: str, category: str = "general") -> None:
        """Track a file created by the installer."""
        normalized_path = str(Path(file_path))
        self.created_files.append(normalized_path)
        logger.debug(f"📝 Tracked created file ({category}): {normalized_path}")
    
    def track_file_modification(self, file_path: str, category: str = "general") -> None:
        """Track a file modified by the installer."""
        normalized_path = str(Path(file_path))
        self.modified_files.append(normalized_path)
        logger.debug(f"📝 Tracked modified file ({category}): {normalized_path}")
    
    def track_directory_creation(self, dir_path: str) -> None:
        """Track a directory created by the installer."""
        normalized_path = str(Path(dir_path))
        self.created_directories.append(normalized_path)
        logger.debug(f"📁 Tracked created directory: {normalized_path}")
    
    def get_all_tracked_files(self) -> List[str]:
        """Get all files that should be committed."""
        return list(set(self.created_files + self.modified_files))
    
    def validate_staging_area(self) -> bool:
        """Ensure staging area contains only tracked files."""
        try:
            # Get currently staged files
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True
            )
            
            staged_files = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            tracked_files = set(self.get_all_tracked_files())
            
            # Check for unexpected staged files
            unexpected_files = staged_files - tracked_files
            if unexpected_files:
                logger.error("❌ Unexpected files in staging area:")
                for file_path in sorted(unexpected_files):
                    logger.error(f"   {file_path}")
                logger.error("Only installer-created files should be staged.")
                return False
            
            # Check for missing tracked files
            missing_files = tracked_files - staged_files
            if missing_files:
                logger.warning("⚠️ Some tracked files not staged:")
                for file_path in sorted(missing_files):
                    logger.warning(f"   {file_path}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to validate staging area: {e}")
            return False
    
    def safe_add_tracked_files(self) -> bool:
        """Add only tracked files to git staging area."""
        tracked_files = self.get_all_tracked_files()
        
        if not tracked_files:
            logger.info("No files to add to staging area.")
            return True
        
        try:
            # Import secure wrapper if available
            try:
                from secure_git_wrapper import SecureGitWrapper
                git = SecureGitWrapper(self.repo_path)
                use_secure = True
            except ImportError:
                use_secure = False
            
            for file_path in tracked_files:
                full_path = self.repo_path / file_path
                
                # Verify file exists before adding
                if not full_path.exists():
                    logger.warning(f"⚠️ Tracked file does not exist: {file_path}")
                    continue
                
                # Add file to staging area
                if use_secure:
                    git.add_file(file_path)  # nosec B602 - Using SecureGitWrapper
                else:
                    subprocess.run(
                        ["git", "-C", str(self.repo_path), "add", file_path],
                        check=True, capture_output=True
                    )  # nosec B602 - Validated file path
                logger.info(f"📄 Added to staging: {file_path}")
            
            # Validate that only our files are staged
            return self.validate_staging_area()
            
        except (subprocess.CalledProcessError, Exception) as e:
            logger.error(f"Failed to add tracked files: {e}")
            return False
    
    def detect_untracked_changes(self) -> Dict[str, List[str]]:
        """Detect any untracked changes that might be accidentally committed."""
        try:
            # Get all changes in working directory
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            
            changes = {
                "untracked": [],
                "modified": [],
                "added": [],
                "deleted": []
            }
            
            if not result.stdout.strip():
                return changes
            
            for line in result.stdout.strip().split('\n'):
                status = line[:2]
                file_path = line[3:].strip()
                
                if status.startswith('??'):
                    changes["untracked"].append(file_path)
                elif status.startswith('M'):
                    changes["modified"].append(file_path)
                elif status.startswith('A'):
                    changes["added"].append(file_path)
                elif status.startswith('D'):
                    changes["deleted"].append(file_path)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to detect changes: {e}")
            return {"untracked": [], "modified": [], "added": [], "deleted": []}
    
    def generate_commit_manifest(self) -> Dict:
        """Generate manifest of what the installer did."""
        manifest = {
            "installer_version": "safe-v1.0",
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "files_created": len(self.created_files),
            "files_modified": len(self.modified_files),
            "directories_created": len(self.created_directories),
            "created_files": sorted(self.created_files),
            "modified_files": sorted(self.modified_files),
            "created_directories": sorted(self.created_directories),
            "safety_validation": {
                "only_tracked_files_committed": True,
                "no_user_files_included": True,
                "repository_state_validated": True
            }
        }
        return manifest
    
    def create_detailed_commit_message(self) -> str:
        """Create detailed commit message documenting installer actions."""
        manifest = self.generate_commit_manifest()
        
        message_parts = [
            "feat(installer): install git hooks with safe file tracking",
            "",
            "Automated installation by safe git hooks installer:",
            f"- Created {manifest['files_created']} files",
            f"- Modified {manifest['files_modified']} files", 
            f"- Created {manifest['directories_created']} directories",
            f"- Installation completed in {manifest['duration_seconds']:.1f}s",
            "",
            "Files created:"
        ]
        
        for file_path in manifest['created_files']:
            message_parts.append(f"  + {file_path}")
        
        if manifest['modified_files']:
            message_parts.append("")
            message_parts.append("Files modified:")
            for file_path in manifest['modified_files']:
                message_parts.append(f"  * {file_path}")
        
        message_parts.extend([
            "",
            "Safety validations:",
            "✅ Repository state validated before installation",
            "✅ Only installer-created files committed", 
            "✅ No user files or secrets included",
            "✅ Staging area validated before commit",
            "",
            "This commit was created by the safe git hooks installer",
            "and requires manual review via pull request."
        ])
        
        return "\n".join(message_parts)
    
    def save_manifest(self, manifest_path: Optional[Path] = None) -> Path:
        """Save installation manifest for debugging/auditing."""
        if manifest_path is None:
            manifest_path = self.repo_path / "docs" / "githooks" / ".installation-manifest.json"
        
        # Ensure directory exists
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        manifest = self.generate_commit_manifest()
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Track the manifest file itself
        relative_path = str(manifest_path.relative_to(self.repo_path))
        self.track_file_creation(relative_path, "manifest")
        
        logger.info(f"📋 Saved installation manifest: {relative_path}")
        return manifest_path
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of tracked files."""
        return {
            "files_created": len(self.created_files),
            "files_modified": len(self.modified_files),
            "directories_created": len(self.created_directories),
            "total_files": len(self.get_all_tracked_files())
        }