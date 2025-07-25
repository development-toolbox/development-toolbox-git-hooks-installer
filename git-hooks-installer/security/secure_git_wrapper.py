"""
Secure Git Wrapper - Provides additional security measures for subprocess Git commands.

This module wraps Git commands with:
- Command whitelisting
- Argument validation
- Path sanitization
- Timeout protection
- No shell execution
- Comprehensive error handling
"""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class SecureGitError(Exception):
    """Custom exception for secure git operations."""
    pass

class SecureGitWrapper:
    """Secure wrapper for Git commands with additional safety measures."""
    
    # Whitelist of allowed Git commands and their valid arguments
    ALLOWED_COMMANDS = {
        'status': ['--porcelain', '--show-stash'],
        'branch': ['--show-current', '--list', '-D'],
        'checkout': ['-b', '--quiet'],
        'add': [],  # File paths will be validated separately
        'commit': ['-m', '--quiet'],
        'push': ['origin'],  # Branch names will be validated
        'remote': ['get-url', 'origin'],
        'init': ['--quiet'],
        'config': ['user.name', 'user.email'],
        'show-ref': ['--verify', '--quiet'],
        'log': ['--oneline'],
        'diff': ['--cached', '--name-only'],
        'ls-files': ['--others', '--exclude-standard'],
        'reset': ['--hard', 'HEAD', '--quiet'],
        'clean': ['-fd', '--quiet']
    }
    
    # Regex patterns for validation
    BRANCH_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9/_-]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9._/\\-]+$')
    
    def __init__(self, repo_path: Union[str, Path], timeout: int = 30):
        """
        Initialize secure Git wrapper.
        
        Args:
            repo_path: Path to Git repository
            timeout: Maximum execution time in seconds (default: 30)
        """
        self.repo_path = Path(repo_path).resolve()
        self.timeout = timeout
        
        # Verify repo path exists and is a directory
        if not self.repo_path.exists():
            raise SecureGitError(f"Repository path does not exist: {self.repo_path}")
        if not self.repo_path.is_dir():
            raise SecureGitError(f"Repository path is not a directory: {self.repo_path}")
    
    def _validate_command(self, git_command: str, args: List[str]) -> None:
        """Validate Git command and arguments against whitelist."""
        if git_command not in self.ALLOWED_COMMANDS:
            raise SecureGitError(f"Git command not allowed: {git_command}")
        
        # Check if arguments are in the allowed list for this command
        allowed_args = self.ALLOWED_COMMANDS[git_command]
        for arg in args:
            # Skip file paths and branch names for now (validated separately)
            if arg.startswith('-') and arg not in allowed_args:
                raise SecureGitError(f"Argument not allowed for {git_command}: {arg}")
    
    def _validate_branch_name(self, branch_name: str) -> None:
        """Validate branch name for safety."""
        if not branch_name:
            raise SecureGitError("Branch name cannot be empty")
        if not self.BRANCH_NAME_PATTERN.match(branch_name):
            raise SecureGitError(f"Invalid branch name format: {branch_name}")
        if len(branch_name) > 255:
            raise SecureGitError("Branch name too long")
    
    def _validate_file_path(self, file_path: str) -> Path:
        """Validate and sanitize file path."""
        try:
            # Convert to Path object and resolve
            path = Path(file_path)
            
            # Check for path traversal attempts
            if '..' in path.parts:
                raise SecureGitError(f"Path traversal detected: {file_path}")
            
            # Ensure path is relative and within repo
            if path.is_absolute():
                # Check if it's within the repo
                try:
                    path.relative_to(self.repo_path)
                except ValueError:
                    raise SecureGitError(f"Absolute path outside repository: {file_path}")
            else:
                # Make it relative to repo
                full_path = self.repo_path / path
                full_path.relative_to(self.repo_path)  # Verify it's within repo
            
            return path
        except Exception as e:
            raise SecureGitError(f"Invalid file path: {file_path} - {str(e)}")
    
    def _build_command(self, git_command: str, *args: str) -> List[str]:
        """Build secure Git command with validated arguments."""
        cmd = ["git", "-C", str(self.repo_path), git_command]
        cmd.extend(args)
        return cmd
    
    def run(self, git_command: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """
        Execute a Git command securely.
        
        Args:
            git_command: The Git command to run (e.g., 'status', 'add')
            *args: Arguments for the Git command
            check: Whether to raise exception on non-zero exit code
            
        Returns:
            subprocess.CompletedProcess object
            
        Raises:
            SecureGitError: If command validation fails
            subprocess.CalledProcessError: If command execution fails
        """
        # Convert args to list and validate
        args_list = list(args)
        self._validate_command(git_command, args_list)
        
        # Build command
        cmd = self._build_command(git_command, *args_list)
        
        logger.debug(f"Executing secure Git command: {' '.join(cmd)}")
        
        try:
            # Run with security measures
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',  # Force UTF-8 encoding
                errors='replace',  # Replace invalid characters instead of failing
                check=check,
                timeout=self.timeout,
                shell=False,  # NEVER use shell=True
                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable Git prompts
            )
            
            if result.stdout:
                logger.debug(f"Git output: {result.stdout.strip()}")
            if result.stderr:
                logger.debug(f"Git stderr: {result.stderr.strip()}")
                
            return result
            
        except subprocess.TimeoutExpired:
            raise SecureGitError(f"Git command timed out after {self.timeout} seconds")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise
    
    # Convenience methods for common Git operations
    
    def status_clean(self) -> bool:
        """Check if working tree is clean."""
        result = self.run("status", "--porcelain")
        return not result.stdout.strip()
    
    def get_current_branch(self) -> str:
        """Get current branch name."""
        result = self.run("branch", "--show-current")
        return result.stdout.strip()
    
    def create_branch(self, branch_name: str) -> None:
        """Create and checkout a new branch."""
        self._validate_branch_name(branch_name)
        self.run("checkout", "-b", branch_name)
    
    def add_file(self, file_path: str) -> None:
        """Add a file to staging area."""
        validated_path = self._validate_file_path(file_path)
        # Ensure forward slashes for Git compatibility on Windows
        git_path = str(validated_path).replace('\\', '/')
        
        # Check if file has changes before attempting to stage
        status_result = self.run("status", "--porcelain", git_path, check=False)
        file_has_changes = bool(status_result.stdout.strip())
        
        # Add the file
        result = self.run("add", git_path)
        
        # Only verify staging if the file had changes
        if file_has_changes:
            # Verify the file was actually staged by checking if it appears in staging
            check_result = self.run("diff", "--cached", "--name-only", check=False)
            staged_files = [f.strip() for f in check_result.stdout.split('\n') if f.strip()]
            
            # Check if our file is in the staged files list
            if git_path not in staged_files:
                # More detailed error with debugging info
                logger.error(f"STAGING DEBUG - Failed to stage: {file_path}")
                logger.error(f"  - Original path: {file_path}")
                logger.error(f"  - Validated path: {validated_path}")
                logger.error(f"  - Git path: {git_path}")
                logger.error(f"  - File exists: {(self.repo_path / git_path).exists()}")
                logger.error(f"  - All staged files: {staged_files}")
                raise SecureGitError(f"Failed to stage file: {file_path} (git_path: {git_path})")
        else:
            # File has no changes - this is expected behavior, not an error
            logger.debug(f"File {file_path} has no changes, git add correctly did nothing")
    
    def commit(self, message: str) -> None:
        """Create a commit with message."""
        if not message:
            raise SecureGitError("Commit message cannot be empty")
        if len(message) > 5000:  # Reasonable limit
            raise SecureGitError("Commit message too long")
        self.run("commit", "-m", message)
    
    def push_branch(self, branch_name: str) -> None:
        """Push branch to origin."""
        self._validate_branch_name(branch_name)
        self.run("push", "origin", branch_name)
    
    def checkout_branch(self, branch_name: str) -> None:
        """Checkout an existing branch."""
        self._validate_branch_name(branch_name)
        self.run("checkout", branch_name, "--quiet")
    
    def delete_branch(self, branch_name: str) -> None:
        """Delete a branch."""
        self._validate_branch_name(branch_name)
        self.run("branch", "-D", branch_name)


# Example usage with bandit suppression comments
def example_safe_usage():
    """Example of using SecureGitWrapper with bandit suppressions."""
    
    git = SecureGitWrapper("/path/to/repo")
    
    # These are now secure and can suppress bandit warnings:
    # nosec B602 - Using SecureGitWrapper with validation
    git.run("status", "--porcelain")  # nosec
    
    # nosec B602 - Branch name validated before use
    git.create_branch("feat/new-feature")  # nosec
    
    # nosec B602 - File path validated and sanitized
    git.add_file("src/main.py")  # nosec