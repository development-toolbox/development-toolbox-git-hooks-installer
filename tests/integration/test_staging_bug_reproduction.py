#!/usr/bin/env python3
"""
Test to reproduce and fix the exact staging bug the user experienced.
This test replicates the scenario where files are tracked but not actually staged.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import pytest

# Import the main installer class
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "git-hooks-installer"))

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "git_hooks_installer", 
        Path(__file__).parent.parent.parent / "git-hooks-installer" / "git-hooks-installer.py"
    )
    git_hooks_installer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(git_hooks_installer_module)
    GitHooksInstaller = git_hooks_installer_module.GitHooksInstaller
except Exception as e:
    GitHooksInstaller = None


@unittest.skipIf(GitHooksInstaller is None, "Could not import GitHooksInstaller")
class TestStagingBugReproduction(unittest.TestCase):
    """Test to reproduce and verify fix for staging bug."""
    
    def setUp(self):
        """Create temporary directories for each test."""
        # Create temporary target repo (simulates user's test repo)
        self.target_temp_dir = tempfile.mkdtemp()
        self.target_repo = Path(self.target_temp_dir)
        
        # Create temporary source directory (copy of actual installer)
        self.source_temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.source_temp_dir)
        
        # Initialize target as git repo
        subprocess.run(["git", "init"], cwd=self.target_temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.target_temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.target_temp_dir, check=True)
        
        # Create a basic main branch with initial commit
        test_file = self.target_repo / "README.md"
        test_file.write_text("# Test Repository")
        subprocess.run(["git", "add", "README.md"], cwd=self.target_temp_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.target_temp_dir, check=True)
        
        # Copy installer files to source directory (same structure as user's installer)
        installer_root = Path(__file__).parent.parent.parent / "git-hooks-installer"
        self._copy_installer_files(installer_root, self.source_dir)
    
    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.target_temp_dir)
        shutil.rmtree(self.source_temp_dir)
    
    def _copy_installer_files(self, src_root, dst_root):
        """Copy the exact installer files that were in user's failing scenario."""
        
        # Copy all necessary directories and files exactly as they exist
        directories_to_copy = [
            "git-hooks",
            "scripts", 
            "docs",
            "developer-setup",
            "security"
        ]
        
        for dir_name in directories_to_copy:
            src_dir = src_root / dir_name
            dst_dir = dst_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, dst_dir)
    
    def get_staged_files(self):
        """Get currently staged files in target repo."""
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=self.target_temp_dir, capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    
    def test_exact_user_scenario_staging_bug(self):
        """Test the exact scenario that failed for the user."""
        
        # Create installer with the same parameters user used
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True  # --no-ci flag user used
        )
        
        # Run through the exact same steps that failed
        self.assertTrue(installer.pre_flight_checks())
        self.assertTrue(installer.create_safe_feature_branch())
        
        # Install each component (same order as user's log)
        self.assertTrue(installer.install_git_hooks())
        self.assertTrue(installer.install_scripts_directory())
        self.assertTrue(installer.install_documentation())
        self.assertTrue(installer.install_developer_setup())
        self.assertTrue(installer.create_shell_wrappers())
        self.assertTrue(installer.save_version_info())
        
        # Get tracked files count before staging
        tracked_files_before = installer.file_tracker.get_all_tracked_files()
        tracked_count = len(tracked_files_before)
        
        print(f"DEBUG: Tracked {tracked_count} files before staging")
        for i, f in enumerate(tracked_files_before):
            print(f"  {i+1:2d}. {f}")
        
        # Stage tracked files (this is where the bug occurs)
        stage_success = installer.file_tracker.safe_add_tracked_files(skip_validation=True)
        self.assertTrue(stage_success, "Staging should succeed")
        
        # Get staged files count after staging  
        staged_files = self.get_staged_files()
        staged_count = len(staged_files)
        
        print(f"DEBUG: Staged {staged_count} files after staging")
        for i, f in enumerate(staged_files):
            print(f"  {i+1:2d}. {f}")
        
        # THIS IS THE BUG: tracked_count should equal staged_count
        if tracked_count != staged_count:
            print("ERROR: Staging bug reproduced!")
            print(f"Tracked: {tracked_count}, Staged: {staged_count}")
            
            # Find the missing files
            tracked_set = set(f.replace('\\', '/') for f in tracked_files_before)
            staged_set = set(f.replace('\\', '/') for f in staged_files)
            missing = tracked_set - staged_set
            
            print("Missing files from staging:")
            for f in sorted(missing):
                full_path = installer.target_repo / f
                exists = full_path.exists()
                print(f"  - {f} (exists: {exists})")
        
        # The bug is fixed if all tracked files are actually staged
        self.assertEqual(
            tracked_count, 
            staged_count, 
            f"Staging bug detected: {tracked_count} tracked != {staged_count} staged"
        )
        
        # Additional verification: specific files that failed in user's scenario
        problematic_files = [
            'docs/githooks/example-of-logs.md',
            'docs/githooks/user-story-example-readme.md', 
            'scripts/post-commit/githooks_utils.py',
            'scripts/post-commit/update-readme.sh'
        ]
        
        for file_path in problematic_files:
            normalized = file_path.replace('\\', '/')
            self.assertIn(
                normalized, 
                [f.replace('\\', '/') for f in staged_files],
                f"File {file_path} should be staged but is missing"
            )
    
    def test_staging_verification_after_each_file(self):
        """Test that each individual file gets staged correctly."""
        
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Run pre-flight and setup
        installer.pre_flight_checks()
        installer.create_safe_feature_branch()
        installer.install_git_hooks()
        installer.install_scripts_directory()
        installer.install_documentation()
        installer.install_developer_setup()
        installer.create_shell_wrappers()
        installer.save_version_info()
        
        # Test staging each file individually
        tracked_files = installer.file_tracker.get_all_tracked_files()
        
        for file_path in tracked_files:
            with self.subTest(file_path=file_path):
                # Clear staging area
                subprocess.run(["git", "reset"], cwd=self.target_temp_dir, check=True, capture_output=True)
                
                # Try to stage just this file
                try:
                    installer.git.add_file(file_path)
                    
                    # Verify it's actually staged
                    staged = self.get_staged_files()
                    normalized_file = file_path.replace('\\', '/')
                    staged_normalized = [f.replace('\\', '/') for f in staged]
                    
                    self.assertIn(
                        normalized_file,
                        staged_normalized,
                        f"File {file_path} failed to stage properly"
                    )
                    
                except Exception as e:
                    self.fail(f"Failed to stage file {file_path}: {e}")
    
    def test_path_normalization_in_staging(self):
        """Test that path normalization doesn't break staging."""
        
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Create test files with different path formats
        test_files = [
            "docs/test-forward-slash.md",
            "scripts\\test-backslash.py",  # Windows-style path
            "developer-setup/test-mixed/file.txt"
        ]
        
        for file_path in test_files:
            # Track the file
            installer.file_tracker.track_file_creation(file_path)
            
            # Create the actual file
            full_path = installer.target_repo / file_path.replace('\\', '/')
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Test content for {file_path}")
        
        # Stage all tracked files
        success = installer.file_tracker.safe_add_tracked_files(skip_validation=True)
        self.assertTrue(success, "Should successfully stage files with mixed path formats")
        
        # Verify all files are staged
        staged_files = self.get_staged_files()
        self.assertEqual(len(staged_files), len(test_files), "All test files should be staged")


class TestStagingErrorDetection(unittest.TestCase):
    """Test that staging errors are properly detected and reported."""
    
    def setUp(self):
        """Create temporary repo."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=self.temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, check=True)
        
        # Import SecureGitWrapper
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "git-hooks-installer"))
        from security.secure_git_wrapper import SecureGitWrapper, SecureGitError
        self.SecureGitWrapper = SecureGitWrapper
        self.SecureGitError = SecureGitError
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_staging_nonexistent_file_raises_error(self):
        """Test that trying to stage a nonexistent file raises proper error."""
        
        git = self.SecureGitWrapper(self.repo_path)
        
        with self.assertRaises(self.SecureGitError) as context:
            git.add_file("nonexistent/file.txt")
        
        self.assertIn("Failed to stage file", str(context.exception))
    
    def test_staging_verification_detects_failure(self):
        """Test that the new verification logic catches staging failures."""
        
        git = self.SecureGitWrapper(self.repo_path)
        
        # Create a file but then delete it before staging
        test_file = self.repo_path / "test.txt"
        test_file.write_text("test content")
        test_file.unlink()  # Delete it
        
        # This should fail with proper error message
        with self.assertRaises(self.SecureGitError) as context:
            git.add_file("test.txt")
        
        self.assertIn("Failed to stage file", str(context.exception))


if __name__ == '__main__':
    unittest.main()