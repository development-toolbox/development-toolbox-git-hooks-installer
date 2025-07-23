import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

# Import the main module functions we want to test
# Adjust the import path based on your project structure
from git_hooks_installer.installer import install_hook_from_template, check_hook_version

class TestGitHooksInstaller:
    """Integration tests for git hooks installer"""
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing"""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
            
            # Create hooks directory if it doesn't exist
            hooks_dir = os.path.join(temp_dir, ".git", "hooks")
            os.makedirs(hooks_dir, exist_ok=True)
            
            yield temp_dir
        finally:
            # Clean up
            shutil.rmtree(temp_dir)
    
    def test_install_hook_from_template(self, temp_git_repo):
        """Test that a hook can be installed from a template"""
        # Create a simple template
        template_dir = os.path.join(temp_git_repo, "templates")
        os.makedirs(template_dir, exist_ok=True)
        
        template_path = os.path.join(template_dir, "pre-commit.template")
        with open(template_path, "w") as f:
            f.write("#!/bin/sh\n\n# TEST HOOK v1.0.0\necho 'Test hook executed'\nexit 0\n")
        
        # Install the hook
        hook_path = install_hook_from_template("pre-commit", template_path, temp_git_repo)
        
        # Verify the hook was installed
        assert os.path.exists(hook_path)
        
        # Verify hook content
        with open(hook_path, "r") as f:
            content = f.read()
            assert "TEST HOOK v1.0.0" in content
        
        # Verify the hook is executable
        assert os.access(hook_path, os.X_OK)
    
    def test_check_hook_version(self, temp_git_repo):
        """Test checking hook version"""
        # Create a hook with a version
        hooks_dir = os.path.join(temp_git_repo, ".git", "hooks")
        hook_path = os.path.join(hooks_dir, "pre-commit")
        
        with open(hook_path, "w") as f:
            f.write("#!/bin/sh\n\n# TEST HOOK v1.0.0\necho 'Test hook executed'\nexit 0\n")
        
        # Make it executable
        os.chmod(hook_path, 0o755)
        
        # Check version
        version = check_hook_version(hook_path)
        assert version == "1.0.0"
    
    def test_hook_execution(self, temp_git_repo):
        """Test that an installed hook can actually run"""
        # Create a hook that creates a marker file when executed
        hooks_dir = os.path.join(temp_git_repo, ".git", "hooks")
        hook_path = os.path.join(hooks_dir, "pre-commit")
        marker_file = os.path.join(temp_git_repo, "hook_executed")
        
        with open(hook_path, "w") as f:
            f.write(f"#!/bin/sh\n\ntouch {marker_file}\nexit 0\n")
        
        # Make it executable
        os.chmod(hook_path, 0o755)
        
        # Create and commit a test file to trigger the pre-commit hook
        test_file = os.path.join(temp_git_repo, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")
        
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_git_repo)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_git_repo)
        subprocess.run(["git", "commit", "-m", "Test commit"], cwd=temp_git_repo)
        
        # Check if marker file was created (hook was executed)
        assert os.path.exists(marker_file)
