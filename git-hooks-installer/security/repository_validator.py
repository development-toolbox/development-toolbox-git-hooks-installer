"""
Repository Validator - Ensures repository safety before git operations.

This module implements comprehensive repository state validation to prevent
dangerous git operations that could commit user secrets or bypass security.
"""

import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RepositoryValidator:
    """Validates repository state for safe git operations."""
    
    def __init__(self, repo_path: Path):
        """Initialize validator for given repository path."""
        # Validate repo_path
        if not isinstance(repo_path, Path):
            repo_path = Path(repo_path)
        
        # Ensure path is absolute and resolved
        self.repo_path = repo_path.resolve()
        
        # Check path exists and is a directory
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")
        if not self.repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {self.repo_path}")
            
        self.validation_errors: List[str] = []
    
    def validate_git_repository(self) -> bool:
        """Ensure target is a valid git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            self.validation_errors.append(f"Not a git repository: {self.repo_path}")
            return False
        return True
    
    def validate_clean_working_tree(self) -> bool:
        """Ensure repository has no uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "status", "--porcelain"],
                capture_output=True, text=True, check=True,
                timeout=10,  # Add timeout
                env={**subprocess.os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable prompts
            )
            
            if result.stdout.strip():
                self.validation_errors.append("Repository has uncommitted changes:")
                for line in result.stdout.strip().split('\n'):
                    status_code = line[:2]
                    file_path = line[3:].strip()
                    
                    if status_code.startswith('??'):
                        self.validation_errors.append(f"  Untracked: {file_path}")
                    elif status_code.startswith('M'):
                        self.validation_errors.append(f"  Modified: {file_path}")
                    elif status_code.startswith('A'):
                        self.validation_errors.append(f"  Added: {file_path}")
                    elif status_code.startswith('D'):
                        self.validation_errors.append(f"  Deleted: {file_path}")
                    else:
                        self.validation_errors.append(f"  {status_code.strip()}: {file_path}")
                
                self.validation_errors.append("Please commit or stash changes before installation.")
                return False
                
            return True
            
        except subprocess.CalledProcessError as e:
            self.validation_errors.append(f"Failed to check repository status: {e}")
            return False
    
    def validate_git_config(self) -> bool:
        """Ensure git user configuration is set."""
        try:
            # Check user.name
            name_result = subprocess.run(
                ["git", "-C", str(self.repo_path), "config", "user.name"],
                capture_output=True, text=True, check=False, timeout=5,
                env={**subprocess.os.environ, 'GIT_TERMINAL_PROMPT': '0'}
            )
            
            # Check user.email
            email_result = subprocess.run(
                ["git", "-C", str(self.repo_path), "config", "user.email"],
                capture_output=True, text=True, check=False, timeout=5,
                env={**subprocess.os.environ, 'GIT_TERMINAL_PROMPT': '0'}
            )
            
            if name_result.returncode != 0 or not name_result.stdout.strip():
                self.validation_errors.append("Git user.name not configured")
                
            if email_result.returncode != 0 or not email_result.stdout.strip():
                self.validation_errors.append("Git user.email not configured")
            
            if name_result.returncode != 0 or email_result.returncode != 0:
                self.validation_errors.append("Configure git with:")
                self.validation_errors.append('  git config user.name "Your Name"')
                self.validation_errors.append('  git config user.email "your.email@example.com"')
                return False
                
            return True
            
        except Exception as e:
            self.validation_errors.append(f"Failed to check git configuration: {e}")
            return False
    
    def validate_no_conflicting_branches(self, branch_pattern: str) -> bool:
        """Ensure no existing branches match the pattern we want to create."""
        # Validate branch pattern to prevent injection
        import re
        if not branch_pattern or not re.match(r'^[a-zA-Z0-9/_.*-]+$', branch_pattern):
            self.validation_errors.append(f"Invalid branch pattern: {branch_pattern}")
            return False
        
        # Limit pattern length
        if len(branch_pattern) > 255:
            self.validation_errors.append("Branch pattern too long")
            return False
            
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "branch", "--list", branch_pattern],
                capture_output=True, text=True, check=True,
                timeout=10,  # Add timeout
                env={**subprocess.os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable prompts
            )
            
            if result.stdout.strip():
                existing_branches = result.stdout.strip().split('\n')
                self.validation_errors.append(f"Conflicting branches exist:")
                for branch in existing_branches:
                    self.validation_errors.append(f"  {branch.strip()}")
                self.validation_errors.append("Please delete or rename existing branches.")
                return False
                
            return True
            
        except subprocess.CalledProcessError as e:
            self.validation_errors.append(f"Failed to check existing branches: {e}")
            return False
    
    def validate_branch_protection(self) -> Tuple[bool, Optional[str]]:
        """Check if main branch has protection (warning, not error)."""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            current_branch = result.stdout.strip()
            
            # Check if we can determine main/master branch
            main_branches = ["main", "master"]
            main_branch = None
            
            for branch in main_branches:
                check_result = subprocess.run(
                    ["git", "-C", str(self.repo_path), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
                    capture_output=True, check=False
                )
                if check_result.returncode == 0:
                    main_branch = branch
                    break
            
            if main_branch:
                # This is a warning, not an error - we can't programmatically check
                # branch protection rules without GitHub/GitLab API access
                logger.warning(f"Consider protecting '{main_branch}' branch on your git platform")
                return True, main_branch
            else:
                logger.warning("Could not determine main branch for protection check")
                return True, None
                
        except Exception as e:
            logger.warning(f"Could not validate branch protection: {e}")
            return True, None
    
    def detect_sensitive_files(self) -> List[str]:
        """Detect potentially sensitive files that should never be committed."""
        sensitive_patterns = [
            ".env", "*.env", ".env.*",
            "*.key", "*.pem", "*.p12", "*.pfx",
            "config.json", "secrets.json", "credentials.json",
            "*.secret", "*.secrets", 
            "password*", "*password*",
            "api_key*", "*api_key*",
            ".aws/credentials", ".ssh/id_*"
        ]
        
        sensitive_files = []
        
        try:
            # Check for untracked files matching sensitive patterns
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "ls-files", "--others", "--exclude-standard"],
                capture_output=True, text=True, check=True,
                timeout=10,  # Add timeout
                env={**subprocess.os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable prompts
            )
            
            untracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            for file_path in untracked_files:
                file_name = Path(file_path).name.lower()
                for pattern in sensitive_patterns:
                    pattern_lower = pattern.lower().replace('*', '')
                    if pattern_lower in file_name:
                        sensitive_files.append(file_path)
                        break
                        
        except subprocess.CalledProcessError:
            pass  # Non-critical if we can't check
            
        return sensitive_files
    
    def validate_all(self, branch_pattern: Optional[str] = None) -> bool:
        """Run all validation checks."""
        self.validation_errors.clear()
        
        # Critical validations (must pass)
        validations = [
            self.validate_git_repository(),
            self.validate_clean_working_tree(),
            self.validate_git_config(),
        ]
        
        # Branch conflict check if pattern provided
        if branch_pattern:
            validations.append(self.validate_no_conflicting_branches(branch_pattern))
        
        # Non-critical validations (warnings only)
        self.validate_branch_protection()
        
        # Check for sensitive files (warning)
        sensitive_files = self.detect_sensitive_files()
        if sensitive_files:
            logger.warning("Potential sensitive files detected:")
            for file_path in sensitive_files:
                logger.warning(f"  {file_path}")
            logger.warning("Ensure these files are properly ignored before installation.")
        
        return all(validations)
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self.validation_errors.copy()
    
    def print_validation_errors(self) -> None:
        """Print all validation errors in a user-friendly format."""
        if not self.validation_errors:
            return
            
        logger.error("❌ Repository validation failed:")
        for error in self.validation_errors:
            if error.startswith("  "):
                logger.error(error)  # Already indented
            else:
                logger.error(f"   {error}")