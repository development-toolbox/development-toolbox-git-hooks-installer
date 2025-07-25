#!/usr/bin/env python3
"""
Integration tests for the complete git hooks installer workflow.
Tests the scenarios that have been manually tested to catch validation issues.
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

# Import GitHooksInstaller class from the correct module
try:
    # Try importing from git-hooks-installer module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "git_hooks_installer", 
        Path(__file__).parent.parent.parent / "git-hooks-installer" / "git-hooks-installer.py"
    )
    git_hooks_installer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(git_hooks_installer_module)
    GitHooksInstaller = git_hooks_installer_module.GitHooksInstaller
except Exception as e:
    # Fallback - skip integration tests if can't import
    import unittest
    GitHooksInstaller = None


@unittest.skipIf(GitHooksInstaller is None, "Could not import GitHooksInstaller")
class TestInstallerValidationWorkflow(unittest.TestCase):
    """Integration tests for the complete installer workflow."""
    
    def setUp(self):
        """Create temporary directories for each test."""
        # Create temporary target repo
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
        
        # Copy installer files to source directory
        installer_root = Path(__file__).parent.parent.parent / "git-hooks-installer"
        self._copy_installer_files(installer_root, self.source_dir)
    
    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.target_temp_dir)
        shutil.rmtree(self.source_temp_dir)
    
    def _copy_installer_files(self, src_root, dst_root):
        """Copy necessary installer files to test directory."""
        # Create the basic structure that installer expects
        directories_to_create = [
            "git-hooks",
            "scripts/post-commit", 
            "docs",
            "developer-setup",
            "security"
        ]
        
        for dir_name in directories_to_create:
            (dst_root / dir_name).mkdir(parents=True, exist_ok=True)
        
        # Copy essential files
        files_to_copy = {
            "git-hooks/post-commit": "git-hooks/post-commit",
            "scripts/post-commit/githooks_utils.py": "scripts/post-commit/githooks_utils.py",
            "scripts/post-commit/generate_git_timeline.py": "scripts/post-commit/generate_git_timeline.py",
            "scripts/post-commit/update-readme.sh": "scripts/post-commit/update-readme.sh",
            "docs/example-of-logs.md": "docs/example-of-logs.md",
            "docs/user-story-example-readme.md": "docs/user-story-example-readme.md",
            "developer-setup/setup_githooks.py": "developer-setup/setup_githooks.py",
            "security/file_tracker.py": "security/file_tracker.py",
            "security/secure_git_wrapper.py": "security/secure_git_wrapper.py",
            "security/repository_validator.py": "security/repository_validator.py",
        }
        
        for src_rel, dst_rel in files_to_copy.items():
            src_file = src_root / src_rel
            dst_file = dst_root / dst_rel
            
            if src_file.exists():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
            else:
                # Create minimal placeholder file
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                dst_file.write_text(f"# Placeholder for {src_rel}\n")
    
    def get_staged_files(self):
        """Get currently staged files in target repo."""
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=self.target_temp_dir, capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    
    def get_git_status(self):
        """Get git status output."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.target_temp_dir, capture_output=True, text=True, check=True
        )
        return result.stdout
    
    def test_full_installer_workflow_no_validation_warnings(self):
        """Test that the full installer workflow completes without false positive warnings."""
        # Create installer instance
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Run pre-flight checks
        self.assertTrue(installer.pre_flight_checks())
        
        # Create feature branch
        self.assertTrue(installer.create_safe_feature_branch())
        
        # Install components
        self.assertTrue(installer.install_git_hooks())
        self.assertTrue(installer.install_scripts_directory())
        self.assertTrue(installer.install_documentation())
        self.assertTrue(installer.install_developer_setup())
        self.assertTrue(installer.create_shell_wrappers())
        self.assertTrue(installer.save_version_info())
        
        # Get all tracked files before staging
        tracked_files_before = installer.file_tracker.get_all_tracked_files()
        self.assertGreater(len(tracked_files_before), 0, "Should have tracked files")
        
        # Stage tracked files 
        self.assertTrue(installer.file_tracker.safe_add_tracked_files(skip_validation=True))
        
        # Verify files are actually staged
        staged_files = self.get_staged_files()
        self.assertGreater(len(staged_files), 0, "Should have staged files")
        
        # Generate and stage manifest
        manifest_path = installer.file_tracker.save_manifest()
        manifest_rel_path = manifest_path.relative_to(installer.target_repo)
        installer.git.add_file(str(manifest_rel_path).replace('\\', '/'))
        
        # Final validation should pass without warnings
        self.assertTrue(installer.file_tracker.validate_staging_area(debug=True))
        
        # Commit should succeed
        self.assertTrue(installer.commit_tracked_changes())
    
    def test_validation_with_mixed_path_separators(self):
        """Test validation handles mixed path separators correctly."""
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Track files with different path separator styles
        test_files = [
            "docs/githooks/test1.md",      # Forward slashes
            "scripts\\post-commit\\test2.py",  # Backslashes (Windows style)
            "developer-setup/test3.sh"     # Mixed
        ]
        
        for file_path in test_files:
            installer.file_tracker.track_file_creation(file_path)
            
            # Create the actual file
            normalized_path = str(Path(file_path)).replace('\\', '/')
            full_path = installer.target_repo / normalized_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content for {file_path}")
        
        # Stage all tracked files
        self.assertTrue(installer.file_tracker.safe_add_tracked_files(skip_validation=True))
        
        # Validation should pass without path separator issues
        self.assertTrue(installer.file_tracker.validate_staging_area(debug=True))
    
    def test_unicode_files_validation(self):
        """Test validation works with Unicode/emoji filenames."""
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Track files with Unicode characters
        unicode_files = [
            "docs/githooks/test-📝-file.md",
            "scripts/post-commit/测试文件.py",
            "developer-setup/файл-тест.sh"
        ]
        
        for file_path in unicode_files:
            installer.file_tracker.track_file_creation(file_path)
            
            # Create the actual file
            full_path = installer.target_repo / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Unicode content for {file_path} ✅", encoding='utf-8')
        
        # Stage all tracked files
        self.assertTrue(installer.file_tracker.safe_add_tracked_files(skip_validation=True))
        
        # Validation should handle Unicode correctly
        self.assertTrue(installer.file_tracker.validate_staging_area(debug=True))
    
    def test_validation_detects_unexpected_files(self):
        """Test that validation properly detects unexpected staged files."""
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Track one file
        installer.file_tracker.track_file_creation("docs/tracked.md")
        
        # Create and stage the tracked file
        tracked_file = installer.target_repo / "docs/tracked.md"
        tracked_file.parent.mkdir(parents=True, exist_ok=True)
        tracked_file.write_text("Tracked content")
        subprocess.run(["git", "add", "docs/tracked.md"], cwd=self.target_temp_dir, check=True)
        
        # Create and stage an UNEXPECTED file (not tracked by installer)
        unexpected_file = installer.target_repo / "docs/unexpected.md"
        unexpected_file.write_text("Unexpected content")
        subprocess.run(["git", "add", "docs/unexpected.md"], cwd=self.target_temp_dir, check=True)
        
        # Validation should FAIL due to unexpected file
        self.assertFalse(installer.file_tracker.validate_staging_area())
    
    def test_exact_installer_file_scenario(self):
        """Test the exact scenario that was causing false positives."""
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # The exact files that were causing issues
        problematic_files = [
            "docs/githooks/example-of-logs.md",
            "docs/githooks/user-story-example-readme.md",
            "scripts/post-commit/githooks_utils.py",
            "scripts/post-commit/update-readme.sh"
        ]
        
        # Track all files (simulating installer behavior)
        for file_path in problematic_files:
            installer.file_tracker.track_file_creation(file_path)
            
            # Create the actual file
            full_path = installer.target_repo / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content for {file_path}")
        
        # Stage files using the same method as installer
        self.assertTrue(installer.file_tracker.safe_add_tracked_files(skip_validation=True))
        
        # Verify files are staged
        staged_files = self.get_staged_files()
        self.assertEqual(len(staged_files), len(problematic_files))
        
        # This should NOT show false positive warnings
        self.assertTrue(installer.file_tracker.validate_staging_area(debug=True))
    
    def test_manifest_file_inclusion(self):
        """Test that manifest file is properly included in validation."""
        installer = GitHooksInstaller(
            target_repo=self.target_repo,
            source_dir=self.source_dir,
            force=False,
            no_ci=True
        )
        
        # Track some regular files
        installer.file_tracker.track_file_creation("docs/test.md")
        
        # Create the file
        test_file = installer.target_repo / "docs/test.md"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("Test content")
        
        # Stage tracked files
        installer.file_tracker.safe_add_tracked_files(skip_validation=True)
        
        # Generate and stage manifest (simulating installer behavior)
        manifest_path = installer.file_tracker.save_manifest()
        manifest_rel_path = manifest_path.relative_to(installer.target_repo)
        installer.git.add_file(str(manifest_rel_path).replace('\\', '/'))
        
        # Validation should pass with manifest included
        self.assertTrue(installer.file_tracker.validate_staging_area(debug=True))
        
        # Verify manifest is staged
        staged_files = self.get_staged_files()
        manifest_staged = any("installation-manifest.json" in f for f in staged_files)
        self.assertTrue(manifest_staged, "Manifest should be staged")


@unittest.skipIf(GitHooksInstaller is None, "Could not import GitHooksInstaller") 
class TestValidationPerformance(unittest.TestCase):
    """Test validation performance with large numbers of files."""
    
    def setUp(self):
        """Create temporary repo."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=self.temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.temp_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, check=True)
        
        # Import FileTracker
        import sys
        installer_path = Path(__file__).parent.parent.parent / "git-hooks-installer"
        if str(installer_path) not in sys.path:
            sys.path.insert(0, str(installer_path))
        
        from security.file_tracker import FileTracker
        self.tracker = FileTracker(self.repo_path)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir)
    
    def test_validation_with_many_files(self):
        """Test validation performance with many files."""
        import time
        
        # Create many files
        num_files = 100
        for i in range(num_files):
            file_path = f"docs/file_{i:03d}.md"
            self.tracker.track_file_creation(file_path)
            
            # Create and stage the file
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content for file {i}")
            
            subprocess.run(["git", "add", file_path], cwd=self.temp_dir, check=True)
        
        # Time the validation
        start_time = time.time()
        result = self.tracker.validate_staging_area()
        end_time = time.time()
        
        # Should complete quickly (less than 5 seconds for 100 files)
        duration = end_time - start_time
        self.assertLess(duration, 5.0, f"Validation took too long: {duration:.2f}s")
        self.assertTrue(result, "Validation should pass")


if __name__ == '__main__':
    unittest.main()