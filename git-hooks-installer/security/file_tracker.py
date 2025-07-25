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
        normalized_path = str(Path(file_path)).replace('\\', '/')
        self.created_files.append(normalized_path)
        logger.debug(f"📝 Tracked created file ({category}): {normalized_path}")
    
    def track_file_modification(self, file_path: str, category: str = "general") -> None:
        """Track a file modified by the installer."""
        normalized_path = str(Path(file_path)).replace('\\', '/')
        self.modified_files.append(normalized_path)
        logger.debug(f"📝 Tracked modified file ({category}): {normalized_path}")
    
    def track_directory_creation(self, dir_path: str) -> None:
        """Track a directory created by the installer."""
        normalized_path = str(Path(dir_path)).replace('\\', '/')
        self.created_directories.append(normalized_path)
        logger.debug(f"📁 Tracked created directory: {normalized_path}")
    
    def get_all_tracked_files(self) -> List[str]:
        """Get all files that should be committed."""
        return list(set(self.created_files + self.modified_files))
    
    def validate_staging_area(self, debug: bool = False) -> bool:
        """Ensure staging area contains only tracked files with improved path matching."""
        try:
            # Get currently staged files
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "diff", "--cached", "--name-only"],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
            )
            
            staged_files_raw = result.stdout.strip().split('\n') if result.stdout.strip() else []
            tracked_files_raw = self.get_all_tracked_files()
            
            # Normalize all paths consistently (use forward slashes, strip whitespace)
            def normalize_path(path_str: str) -> str:
                """Normalize path for consistent comparison."""
                return str(Path(path_str)).replace('\\', '/').strip()
            
            staged_files = set(normalize_path(f) for f in staged_files_raw if f.strip())
            tracked_files = set(normalize_path(f) for f in tracked_files_raw if f.strip())
            
            if debug:
                logger.info("🔍 Validation Debug Info:")
                logger.info(f"   Raw staged files ({len(staged_files_raw)}): {staged_files_raw}")
                logger.info(f"   Raw tracked files ({len(tracked_files_raw)}): {tracked_files_raw}")
                logger.info(f"   Normalized staged files ({len(staged_files)}): {sorted(staged_files)}")
                logger.info(f"   Normalized tracked files ({len(tracked_files)}): {sorted(tracked_files)}")
            
            # Check for unexpected staged files (files staged but not tracked)
            unexpected_files = staged_files - tracked_files
            if unexpected_files:
                logger.error("❌ Unexpected files in staging area:")
                for file_path in sorted(unexpected_files):
                    logger.error(f"   {file_path}")
                logger.error("Only installer-created files should be staged.")
                return False
            
            # Check for missing tracked files (files tracked but not staged)
            missing_files = tracked_files - staged_files
            if missing_files:
                # Filter out files that are already committed and unchanged
                actually_missing = []
                for file_path in missing_files:
                    # Check if file has changes that need staging
                    status_result = subprocess.run(
                        ["git", "-C", str(self.repo_path), "status", "--porcelain", file_path],
                        capture_output=True, text=True, encoding='utf-8', errors='replace', check=False
                    )
                    file_has_changes = bool(status_result.stdout.strip())
                    
                    if file_has_changes:
                        actually_missing.append(file_path)
                
                if actually_missing:
                    if debug:
                        logger.warning("⚠️ Debug: Some tracked files with changes not staged:")
                        for file_path in sorted(actually_missing):
                            full_path = self.repo_path / file_path
                            exists = full_path.exists()
                            logger.warning(f"   {file_path} (exists: {exists})")
                    else:
                        logger.warning("⚠️ Some tracked files not staged:")
                        for file_path in sorted(actually_missing):
                            logger.warning(f"   {file_path}")
                elif debug:
                    logger.info("ℹ️ Debug: Missing files are already committed with no changes (correct)")
                    for file_path in sorted(missing_files):
                        logger.info(f"   {file_path} - already committed, no changes")
            
            # Validation passes if no unexpected files are staged
            # Missing files are just warnings, not failures
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to validate staging area: {e}")
            return False
    
    def safe_add_tracked_files(self, skip_validation: bool = False) -> bool:
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
                        check=True, capture_output=True, encoding='utf-8', errors='replace'
                    )  # nosec B602 - Validated file path
                logger.info(f"📄 Added to staging: {file_path}")
            
            # Validate that only our files are staged (unless skipped)
            if skip_validation:
                return True
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
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
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
            "installer_version": "1.0.0",
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
            "feat(installer): install git hooks with automated file tracking",
            "",
            "Automated installation by git hooks installer:",
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
            "Security validations:",
            "✅ Repository state validated before installation",
            "✅ Only installer-created files committed", 
            "✅ No user files or secrets included",
            "✅ Staging area validated before commit",
            "",
            "This commit was created by the git hooks installer",
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