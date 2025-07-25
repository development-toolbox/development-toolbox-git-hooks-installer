#!/usr/bin/env python3
"""
Git Hooks Installer - Security-first implementation.

USER STORIES IMPLEMENTED:
- US-001: Safe installation for developers with secrets
- US-002: Team lead code quality control
- US-003: Developer work-in-progress protection
- US-004: Cross-platform developer setup
- US-005: Repository administrator branch protection

SECURITY GUARANTEES:
- Never commits user files or secrets
- Always requires PR review (no auto-merge)
- Validates repository state before operations
- Tracks only installer-created files
- Fails safely with clear error messages
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Import our safety modules
from security.repository_validator import RepositoryValidator
from security.file_tracker import FileTracker
from security.secure_git_wrapper import SecureGitWrapper, SecureGitError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHooksInstaller:
    """Git hooks installer with comprehensive security validation."""

    def __init__(self, target_repo: Path, source_dir: Path, force: bool = False, no_ci: bool = False):
        """Initialize installer."""
        self.target_repo = target_repo
        self.source_dir = source_dir
        self.force = force
        self.no_ci = no_ci
        self.validator = RepositoryValidator(target_repo)
        self.file_tracker = FileTracker(target_repo)
        self.git = SecureGitWrapper(target_repo)  # Secure Git operations
        self.branch_name: Optional[str] = None
        self.original_branch: Optional[str] = None

    def pre_flight_checks(self) -> bool:
        """Run comprehensive pre-flight safety checks."""
        logger.info("🔍 Running pre-flight safety checks...")

        # Generate potential branch name for conflict check
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        potential_branch = f"feat/githooks-installation-{timestamp}"

        # Run all validations
        if not self.validator.validate_all(potential_branch):
            logger.error("❌ Pre-flight checks failed:")
            self.validator.print_validation_errors()
            logger.error("")
            logger.error("Please fix the above issues before running the installer.")
            return False

        logger.info("✅ All pre-flight checks passed")
        return True

    def get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            return self.git.get_current_branch()
        except (subprocess.CalledProcessError, SecureGitError) as e:
            logger.error(f"Failed to get current branch: {e}")
            return "main"  # Safe default

    def create_safe_feature_branch(self) -> bool:
        """Create feature branch for safe installation."""
        try:
            self.original_branch = self.get_current_branch()
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.branch_name = f"feat/githooks-installation-{timestamp}"

            logger.info(f"🌿 Creating feature branch: {self.branch_name}")

            self.git.create_branch(self.branch_name)  # nosec B602 - Using SecureGitWrapper

            logger.info(f"✅ Created and switched to branch: {self.branch_name}")
            return True

        except (subprocess.CalledProcessError, SecureGitError) as e:
            logger.error(f"Failed to create feature branch: {e}")
            return False

    def install_git_hooks(self) -> bool:
        """Install git hooks to .git/hooks/ directory."""
        hooks_src = self.source_dir / "git-hooks"
        hooks_dst = self.target_repo / ".git" / "hooks"

        if not hooks_src.exists():
            logger.warning("⚠️ No git-hooks directory found in source")
            return True  # Not critical

        logger.info("🪝 Installing git hooks...")

        try:
            for hook_file in hooks_src.iterdir():
                if hook_file.is_file() and not hook_file.name.endswith('.sample'):
                    dst_hook = hooks_dst / hook_file.name
                    shutil.copy2(hook_file, dst_hook)
                    dst_hook.chmod(0o755)  # Make executable
                    logger.info(f"   Installed hook: {hook_file.name}")

            logger.info("✅ Git hooks installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install git hooks: {e}")
            return False

    def install_scripts_directory(self) -> bool:
        """Install scripts with safe file tracking."""
        scripts_src = self.source_dir / "scripts"
        scripts_dst = self.target_repo / "scripts"

        if not scripts_src.exists():
            logger.warning("⚠️ No scripts directory found in source")
            return True

        logger.info("📂 Installing scripts directory...")

        try:
            # Create scripts directory
            if not scripts_dst.exists():
                scripts_dst.mkdir(parents=True, exist_ok=True)
                self.file_tracker.track_directory_creation("scripts")

            # Copy all files with tracking
            for src_file in scripts_src.rglob("*"):
                if src_file.is_file():
                    rel_path = src_file.relative_to(scripts_src)
                    dst_file = scripts_dst / rel_path

                    # Ensure parent directory exists
                    dst_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    shutil.copy2(src_file, dst_file)

                    # Track the file
                    relative_to_repo = f"scripts/{rel_path}"
                    self.file_tracker.track_file_creation(relative_to_repo, "scripts")
                    logger.info(f"   + {relative_to_repo}")

            logger.info("✅ Scripts directory installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install scripts: {e}")
            return False

    def install_documentation(self) -> bool:
        """Install documentation with safe file tracking."""
        docs_src = self.source_dir / "docs"
        docs_dst = self.target_repo / "docs" / "githooks"

        if not docs_src.exists():
            logger.warning("⚠️ No docs directory found in source")
            return True

        logger.info("📚 Installing documentation...")

        try:
            # Create docs directories
            docs_parent = self.target_repo / "docs"
            if not docs_parent.exists():
                docs_parent.mkdir(parents=True, exist_ok=True)
                self.file_tracker.track_directory_creation("docs")
            
            if not docs_dst.exists():
                docs_dst.mkdir(parents=True, exist_ok=True)
                self.file_tracker.track_directory_creation("docs/githooks")

            # Copy documentation files
            for src_file in docs_src.rglob("*"):
                if src_file.is_file():
                    rel_path = src_file.relative_to(docs_src)
                    dst_file = docs_dst / rel_path

                    # Ensure parent directory exists
                    dst_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    shutil.copy2(src_file, dst_file)

                    # Track the file
                    relative_to_repo = f"docs/githooks/{rel_path}"
                    self.file_tracker.track_file_creation(relative_to_repo, "docs")
                    logger.info(f"   + {relative_to_repo}")

            logger.info("✅ Documentation installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install documentation: {e}")
            return False

    def install_developer_setup(self) -> bool:
        """Install complete developer setup with safe file tracking."""
        setup_src = self.source_dir / "developer-setup"
        setup_dst = self.target_repo / "developer-setup"

        if not setup_src.exists():
            logger.warning("⚠️ No developer-setup directory found in source")
            return True

        logger.info("👨‍💻 Installing developer setup...")

        try:
            # Create developer-setup directory
            if not setup_dst.exists():
                setup_dst.mkdir(parents=True, exist_ok=True)
                self.file_tracker.track_directory_creation("developer-setup")

            # Copy entire developer-setup structure
            for src_item in setup_src.iterdir():
                if src_item.is_dir():
                    dst_dir = setup_dst / src_item.name
                    dir_existed = dst_dir.exists()
                    if dir_existed:
                        shutil.rmtree(dst_dir)
                    shutil.copytree(src_item, dst_dir)

                    # Track directory only if it didn't exist before
                    if not dir_existed:
                        self.file_tracker.track_directory_creation(f"developer-setup/{src_item.name}")
                    for file_path in dst_dir.rglob("*"):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(self.target_repo)
                            self.file_tracker.track_file_creation(str(rel_path), "developer-setup")

                    logger.info(f"   + developer-setup/{src_item.name}/")

                elif src_item.is_file():
                    dst_file = setup_dst / src_item.name
                    shutil.copy2(src_item, dst_file)

                    rel_path = f"developer-setup/{src_item.name}"
                    self.file_tracker.track_file_creation(rel_path, "developer-setup")
                    logger.info(f"   + {rel_path}")

            logger.info("✅ Developer setup installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install developer setup: {e}")
            return False

    def create_shell_wrappers(self) -> bool:
        """Create cross-platform shell wrapper scripts."""
        logger.info("🔧 Creating shell wrapper scripts...")

        try:
            # Linux/macOS wrapper
            sh_wrapper = self.target_repo / "setup-githooks.sh"
            sh_content = '''#!/bin/bash
# Git hooks setup wrapper script
# Auto-generated by safe git hooks installer

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if developer-setup exists
if [ ! -d "$DIR/developer-setup" ]; then
    echo "Error: developer-setup directory not found!"
    echo "Please run the safe git-hooks-installer first."
    exit 1
fi

# Run the Python setup script
if command -v python3 &> /dev/null; then
    python3 "$DIR/developer-setup/setup_githooks.py" "$@"
elif command -v python &> /dev/null; then
    python "$DIR/developer-setup/setup_githooks.py" "$@"
else
    echo "Error: Python not found! Please install Python 3."
    exit 1
fi
'''

            with open(sh_wrapper, 'w', newline='\n') as f:
                f.write(sh_content)
            sh_wrapper.chmod(0o755)
            self.file_tracker.track_file_creation("setup-githooks.sh", "shell-wrapper")
            logger.info("   + setup-githooks.sh")

            # Windows PowerShell wrapper
            ps1_wrapper = self.target_repo / "setup-githooks.ps1"
            ps1_content = '''# Git hooks setup wrapper script for Windows
# Auto-generated by safe git hooks installer

# Get the directory of this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if developer-setup exists
if (-not (Test-Path "$scriptPath\\developer-setup")) {
    Write-Host "Error: developer-setup directory not found!" -ForegroundColor Red
    Write-Host "Please run the safe git-hooks-installer first."
    exit 1
}

# Run the Python setup script
if (Get-Command python -ErrorAction SilentlyContinue) {
    python "$scriptPath\\developer-setup\\setup_githooks.py" $args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 "$scriptPath\\developer-setup\\setup_githooks.py" $args
} else {
    Write-Host "Error: Python not found! Please install Python 3." -ForegroundColor Red
    exit 1
}
'''

            with open(ps1_wrapper, 'w', newline='\r\n') as f:
                f.write(ps1_content)
            self.file_tracker.track_file_creation("setup-githooks.ps1", "shell-wrapper")
            logger.info("   + setup-githooks.ps1")

            logger.info("✅ Shell wrapper scripts created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create shell wrappers: {e}")
            return False

    def save_version_info(self) -> bool:
        """Save version and installation information."""
        logger.info("📋 Saving version information...")

        try:
            version_dir = self.target_repo / "docs" / "githooks"
            version_dir.mkdir(parents=True, exist_ok=True)

            version_file = version_dir / ".githooks-version.json"
            version_data = {
                "version": "1.0.0",
                "installed": datetime.now().isoformat(),
                "installer": "git-hooks-installer",
                "branch": self.branch_name,
                "original_branch": self.original_branch,
                "repository_validated": True,
                "installation_summary": self.file_tracker.get_summary()
            }

            import json
            with open(version_file, 'w') as f:
                json.dump(version_data, f, indent=2)

            rel_path = str(version_file.relative_to(self.target_repo))
            self.file_tracker.track_file_creation(rel_path, "version")
            logger.info(f"   + {rel_path}")

            logger.info("✅ Version information saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save version info: {e}")
            return False

    def commit_tracked_changes(self) -> bool:
        """Commit only tracked files with detailed message."""
        logger.info("💾 Committing tracked changes...")

        try:
            # Add only tracked files (without validation yet)
            if not self.file_tracker.safe_add_tracked_files(skip_validation=True):
                return False

            # Generate manifest
            manifest_path = self.file_tracker.save_manifest()
            
            # Add the manifest file to staging
            manifest_rel_path = manifest_path.relative_to(self.target_repo)
            self.git.add_file(str(manifest_rel_path).replace('\\', '/'))  # nosec B602 - Using SecureGitWrapper
            logger.info(f"📄 Added manifest to staging: {manifest_rel_path}")

            # NOW validate that everything is staged correctly (with debug info)
            if not self.file_tracker.validate_staging_area(debug=True):
                logger.error("❌ Final staging validation failed")
                return False

            # Create detailed commit message
            commit_message = self.file_tracker.create_detailed_commit_message()

            # Commit changes using secure wrapper
            self.git.commit(commit_message)  # nosec B602 - Using SecureGitWrapper

            summary = self.file_tracker.get_summary()
            logger.info(f"✅ Committed {summary['total_files']} files successfully")
            logger.info(f"   📄 Files created: {summary['files_created']}")
            logger.info(f"   📄 Files modified: {summary['files_modified']}")
            logger.info(f"   📁 Directories created: {summary['directories_created']}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit changes: {e}")
            return False

    def push_feature_branch(self) -> bool:
        """Push feature branch to origin (if remote exists)."""
        try:
            # Ensure we have a branch name
            if not self.branch_name:
                logger.error("No feature branch name available for push")
                return False
                
            # Check if remote exists using secure wrapper
            result = self.git.run("remote", "get-url", "origin", check=False)  # nosec B602

            if result.returncode != 0:
                logger.info("ℹ️ No remote 'origin' configured - skipping push")
                return True

            logger.info(f"📤 Pushing feature branch: {self.branch_name}")

            self.git.push_branch(self.branch_name)  # nosec B602 - Using SecureGitWrapper

            logger.info("✅ Feature branch pushed successfully")
            return True

        except (subprocess.CalledProcessError, SecureGitError) as e:
            logger.error(f"Failed to push feature branch: {e}")
            logger.info("You can push manually with:")
            logger.info(f"  git push origin {self.branch_name}")
            return False  # Non-critical failure

    def check_installation_status(self) -> bool:
        """Check and report current installation status."""
        logger.info("🔍 Checking git hooks installation status...")
        logger.info("")
        
        status_items = []
        all_good = True
        
        # Check if it's a git repository
        if not (self.target_repo / ".git").exists():
            logger.error("❌ Not a git repository")
            return False
            
        # Check git hooks
        hooks_dir = self.target_repo / ".git" / "hooks"
        post_commit = hooks_dir / "post-commit"
        
        if post_commit.exists():
            logger.info("✅ Post-commit hook: INSTALLED")
            # Check if it's executable
            if post_commit.stat().st_mode & 0o111:
                logger.info("   └─ Executable: YES")
            else:
                logger.warning("   └─ Executable: NO (may not work)")
                all_good = False
        else:
            logger.info("❌ Post-commit hook: NOT INSTALLED")
            all_good = False
            
        # Check scripts directory
        scripts_dir = self.target_repo / "scripts" / "post-commit"
        if scripts_dir.exists():
            logger.info("✅ Scripts directory: INSTALLED")
            script_files = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
            logger.info(f"   └─ Found {len(script_files)} script files")
        else:
            logger.info("❌ Scripts directory: NOT INSTALLED")
            all_good = False
            
        # Check developer setup
        dev_setup = self.target_repo / "developer-setup"
        if dev_setup.exists():
            logger.info("✅ Developer setup: INSTALLED")
        else:
            logger.info("❌ Developer setup: NOT INSTALLED")
            all_good = False
            
        # Check shell wrappers
        sh_wrapper = self.target_repo / "setup-githooks.sh"
        ps1_wrapper = self.target_repo / "setup-githooks.ps1"
        
        if sh_wrapper.exists():
            logger.info("✅ Shell wrapper (sh): INSTALLED")
        else:
            logger.info("❌ Shell wrapper (sh): NOT INSTALLED")
            all_good = False
            
        if ps1_wrapper.exists():
            logger.info("✅ PowerShell wrapper (ps1): INSTALLED")
        else:
            logger.info("❌ PowerShell wrapper (ps1): NOT INSTALLED")
            all_good = False
            
        # Check docs directory
        docs_dir = self.target_repo / "docs"
        if docs_dir.exists():
            logger.info("✅ Documentation directory: EXISTS")
            commit_logs = docs_dir / "commit-logs"
            if commit_logs.exists():
                branches = list(commit_logs.iterdir())
                logger.info(f"   └─ Commit logs for {len(branches)} branches")
            else:
                logger.info("   └─ No commit logs yet")
        else:
            logger.info("ℹ️ Documentation directory: NOT CREATED (will be created on first commit)")
            
        logger.info("")
        if all_good:
            logger.info("🎉 Git hooks installation: COMPLETE")
            logger.info("ℹ️ Ready to automatically document commits!")
        else:
            logger.warning("⚠️ Git hooks installation: INCOMPLETE")
            logger.info("💡 Run without --check to install missing components")
            
        return all_good

    def generate_pr_instructions(self) -> None:
        """Generate pull request instructions."""
        logger.info("")
        logger.info("🎉 Installation completed successfully!")
        logger.info("")
        logger.info("📋 NEXT STEPS - Manual Review Required:")
        logger.info(f"   1. Review changes in branch: {self.branch_name}")
        logger.info(f"   2. Create pull request: {self.branch_name} → {self.original_branch}")
        logger.info("   3. Have team member review the changes")
        logger.info("   4. Merge after approval and testing")
        logger.info("")

        # Try to generate platform-specific PR URL
        try:
            result = self.git.run("remote", "get-url", "origin", check=False)  # nosec B602

            if result.returncode == 0:
                remote_url = result.stdout.strip()

                # Convert SSH to HTTPS URL
                if remote_url.startswith('git@github.com:'):
                    remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
                if remote_url.endswith('.git'):
                    remote_url = remote_url[:-4]

                if 'github.com' in remote_url:
                    pr_url = f"{remote_url}/compare/{self.original_branch}...{self.branch_name}"
                    logger.info("")
                    logger.info("=" * 70)
                    logger.info("🚨 ACTION REQUIRED: CREATE PULL REQUEST 🚨")
                    logger.info("=" * 70)
                    logger.info("")
                    logger.info("👉 Click here to create PR:")
                    logger.info(f"   {pr_url}")
                    logger.info("")
                    logger.info("=" * 70)
                elif 'gitlab' in remote_url:
                    pr_url = f"{remote_url}/-/merge_requests/new?merge_request[source_branch]={self.branch_name}&merge_request[target_branch]={self.original_branch}"
                    logger.info("")
                    logger.info("=" * 70)
                    logger.info("🚨 ACTION REQUIRED: CREATE MERGE REQUEST 🚨")
                    logger.info("=" * 70)
                    logger.info("")
                    logger.info("👉 Click here to create MR:")
                    logger.info(f"   {pr_url}")
                    logger.info("")
                    logger.info("=" * 70)

        except Exception:
            pass  # Non-critical

        logger.info("")
        logger.info("🛡️ SECURITY GUARANTEES:")
        logger.info("   ✅ Repository state validated before installation")
        logger.info("   ✅ Only installer-created files committed")
        logger.info("   ✅ No user secrets or work-in-progress included")
        logger.info("   ✅ Manual review required via pull request")
        logger.info("   ✅ No direct commits to main branch")
        logger.info("")
        logger.info("⚠️ Remember: The pull request won't create itself!")
        logger.info("   Use the link above to create it now.")

    def cleanup_on_failure(self) -> None:
        """Clean up if installation fails."""
        try:
            logger.info("🧹 Cleaning up after failure...")

            # First, reset any staged changes
            try:
                self.git.run("reset", "HEAD")  # nosec B602
                logger.info("✅ Reset staged changes")
            except Exception as e:
                logger.warning(f"Failed to reset staged changes: {e}")

            # Remove tracked files that were created
            tracked_files = self.file_tracker.get_all_tracked_files()
            for file_path in tracked_files:
                full_path = self.target_repo / file_path
                if full_path.exists():
                    try:
                        full_path.unlink()
                        logger.debug(f"Removed tracked file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove {file_path}: {e}")

            # Remove tracked directories (in reverse order for nested dirs)
            for dir_path in reversed(sorted(self.file_tracker.created_directories)):
                full_path = self.target_repo / dir_path
                if full_path.exists() and full_path.is_dir():
                    try:
                        # Only remove if empty
                        full_path.rmdir()
                        logger.debug(f"Removed tracked directory: {dir_path}")
                    except Exception as e:
                        # Directory might not be empty, that's okay
                        pass

            # Switch back to original branch and delete feature branch
            if self.branch_name and self.original_branch:
                # Switch back to original branch using secure wrapper
                if self.original_branch:  # Type guard for mypy
                    try:
                        self.git.checkout_branch(self.original_branch)  # nosec B602
                    except:
                        pass  # Best effort

                # Delete the failed branch using secure wrapper
                if self.branch_name:  # Type guard for mypy
                    try:
                        self.git.delete_branch(self.branch_name)  # nosec B602
                    except:
                        pass  # Best effort

            logger.info("✅ Cleanup completed")

        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    def install(self) -> bool:
        """Run complete installation process."""
        logger.info("🚀 Starting Git Hooks Installation")
        logger.info("=" * 50)

        try:
            # Phase 1: Pre-flight safety checks
            if not self.pre_flight_checks():
                return False

            # Phase 2: Create safe feature branch
            if not self.create_safe_feature_branch():
                return False

            # Phase 3: Install components with tracking
            installation_steps = [
                ("Git Hooks", self.install_git_hooks),
                ("Scripts", self.install_scripts_directory),
                ("Documentation", self.install_documentation),
                ("Developer Setup", self.install_developer_setup),
                ("Shell Wrappers", self.create_shell_wrappers),
                ("Version Info", self.save_version_info),
            ]

            for step_name, step_func in installation_steps:
                if not step_func():
                    logger.error(f"❌ Installation failed at step: {step_name}")
                    self.cleanup_on_failure()
                    return False

            # Phase 4: Commit and push
            if not self.commit_tracked_changes():
                self.cleanup_on_failure()
                return False

            # Push feature branch (non-critical if fails)
            self.push_feature_branch()

            # Phase 5: Generate PR instructions
            self.generate_pr_instructions()

            return True

        except Exception as e:
            logger.error(f"Unexpected error during installation: {e}")
            self.cleanup_on_failure()
            return False


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Install/update git hooks, scripts, and documentation in a Git repository.",
        epilog="""
Examples:
  %(prog)s                              # Install in current directory
  %(prog)s /path/to/project             # Install in specific git repository
  %(prog)s -c                           # Check installation status
  %(prog)s -f                           # Force reinstall
  %(prog)s -v /path/to/project          # Verbose installation in specific repo
  %(prog)s -d --no-ci                   # Debug mode, skip CI files
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("target", type=str, nargs='?', default=".",
                        help="Path to the target Git repository where hooks will be installed (default: current directory)")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force reinstall even if up-to-date")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--no-ci", action="store_true",
                        help="Skip CI/CD file installation")
    parser.add_argument("-c", "--check", action="store_true",
                        help="Check current installation status")

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # Resolve target path
    target_repo = Path(args.target).resolve()
    
    # Auto-detect source directory (where this installer is located)
    installer_path = Path(__file__).resolve()
    source_dir = installer_path.parent  # git-hooks-installer/ directory

    # Validate paths
    if not target_repo.exists():
        logger.error(f"Target repository does not exist: {target_repo}")
        sys.exit(1)

    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        sys.exit(1)

    logger.info(f"Target repository: {target_repo}")
    logger.info(f"Source directory: {source_dir}")

    # Create installer
    installer = GitHooksInstaller(target_repo, source_dir, force=args.force, no_ci=args.no_ci)

    # Handle check option
    if args.check:
        if installer.check_installation_status():
            sys.exit(0)  # All good
        else:
            sys.exit(1)  # Issues found
    
    # Run installation
    if installer.install():
        logger.info("🎉 Installation completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Installation failed - see errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()