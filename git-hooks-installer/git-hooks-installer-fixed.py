#!/usr/bin/env python3
# githooks-install.py
# version 0.6 - FIXED VERSION
# Author: Johan Sörell
# Updated: 2025-01-24 - Major fixes for installation issues

# License: MIT License
"""
This script sets up git hooks, scripts, and documentation in a specified Git repository.
Fixed version that properly installs all components including scripts/, docs/, and developer-setup.
"""
import os
import shutil
import subprocess
from pathlib import Path
import filecmp
import argparse
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import json
from typing import List, Optional

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class GitHooksInstaller:
    """Main installer class with version tracking and safe file management."""

    VERSION_FILE = ".githooks-version.json"

    def __init__(self, target_repo: Path, source_dir: Path):
        self.target_repo = target_repo
        self.source_dir = source_dir
        self.managed_files = {
            "scripts": set(),
            "docs": set()
        }

    def load_version_info(self) -> dict:
        """Load version information from target repository."""
        version_file = self.target_repo / "docs" / "githooks" / self.VERSION_FILE
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load version file: {e}")
        return {}

    def save_version_info(self, scripts_hash: str, docs_hash: str, hooks_hash: str):
        """Save version information to target repository."""
        # Ensure directory exists
        version_dir = self.target_repo / "docs" / "githooks"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        version_data = {
            "version": "0.6",
            "updated": datetime.now().isoformat(),
            "scripts_hash": scripts_hash,
            "docs_hash": docs_hash,
            "hooks_hash": hooks_hash,
            "managed_files": {
                "scripts": list(self.managed_files["scripts"]),
                "docs": list(self.managed_files["docs"])
            }
        }
        
        # Write version file
        version_file = version_dir / self.VERSION_FILE
        try:
            with open(version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
            logger.info(f"✅ Saved version info to {version_file}")
        except Exception as e:
            logger.error(f"Failed to save version info: {e}")

    def calculate_directory_hash(self, directory: Path) -> str:
        """Calculate hash of all files in a directory."""
        if not directory.exists():
            return ""
        
        hasher = hashlib.sha256()
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith('.'):
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        return hasher.hexdigest()

    def copy_directory_improved(self, src: Path, dst: Path, category: str) -> List[str]:
        """
        Improved directory copy that maintains structure and tracks files.
        
        This is the FIXED version that properly creates directory structures.
        """
        copied_files = []
        
        # Always create the destination directory
        dst.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created directory: {dst}")
        
        # Load existing managed files
        version_info = self.load_version_info()
        existing_managed = set(version_info.get("managed_files", {}).get(category, []))
        new_managed_files = set()
        
        if not src.exists():
            logger.warning(f"Source directory does not exist: {src}")
            return copied_files
        
        # Special handling for scripts to maintain post-commit structure
        if category == "scripts" and src.name == "scripts":
            post_commit_src = src / "post-commit"
            if post_commit_src.exists():
                post_commit_dst = dst / "post-commit"
                post_commit_dst.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created scripts/post-commit directory")
                
                # Copy all files from post-commit
                for src_file in post_commit_src.iterdir():
                    if src_file.is_file() and not src_file.name.startswith('.'):
                        dst_file = post_commit_dst / src_file.name
                        rel_path = dst_file.relative_to(self.target_repo)
                        
                        # Copy if new or changed
                        if not dst_file.exists() or not filecmp.cmp(src_file, dst_file, shallow=False):
                            shutil.copy2(src_file, dst_file)
                            # Make scripts executable
                            if src_file.suffix in ['.sh', '.py']:
                                dst_file.chmod(0o755)
                            copied_files.append(str(rel_path))
                            logger.info(f"📄 {'New' if not dst_file.exists() else 'Updated'} {category} file: {rel_path}")
                        
                        new_managed_files.add(str(rel_path))
        else:
            # Normal directory copy for docs
            for src_file in src.iterdir():
                if src_file.is_file() and not src_file.name.startswith('.'):
                    dst_file = dst / src_file.name
                    rel_path = dst_file.relative_to(self.target_repo)
                    
                    # Copy if new or changed
                    if not dst_file.exists() or not filecmp.cmp(src_file, dst_file, shallow=False):
                        shutil.copy2(src_file, dst_file)
                        copied_files.append(str(rel_path))
                        logger.info(f"📄 {'New' if not dst_file.exists() else 'Updated'} {category} file: {rel_path}")
                    
                    new_managed_files.add(str(rel_path))
        
        # Check for orphaned files
        orphaned = existing_managed - new_managed_files
        if orphaned:
            logger.warning(f"⚠️  Found orphaned {category} files (no longer in source): {orphaned}")
        
        self.managed_files[category] = new_managed_files
        return copied_files

    def check_if_update_needed(self, hooks_dst: Path) -> tuple[bool, bool, bool]:
        """
        Check if hooks, scripts, or docs need updating.
        Returns (hooks_need_update, scripts_need_update, docs_need_update)
        """
        version_info = self.load_version_info()
        
        # Check paths
        hooks_src = self.source_dir / "git-hooks"
        scripts_src = self.source_dir / "scripts"
        docs_src = self.source_dir / "docs"
        
        # Check hooks by comparing actual files
        hooks_need_update = False
        if hooks_src.exists():
            hooks_need_update = not compare_hooks(hooks_src, hooks_dst)
        
        # Calculate hashes for scripts and docs
        current_scripts_hash = self.calculate_directory_hash(scripts_src)
        current_docs_hash = self.calculate_directory_hash(docs_src)
        
        # Compare with stored hashes
        scripts_need_update = False
        docs_need_update = False
        
        if scripts_src.exists():
            scripts_need_update = current_scripts_hash != version_info.get("scripts_hash", "")
        if docs_src.exists():
            docs_need_update = current_docs_hash != version_info.get("docs_hash", "")
        
        if not hooks_need_update and not scripts_need_update and not docs_need_update:
            logger.debug("No updates needed - all components are up-to-date")
        else:
            if hooks_need_update:
                logger.info("🔄 Git hooks need updating")
            if scripts_need_update:
                logger.info("🔄 Scripts need updating")
            if docs_need_update:
                logger.info("🔄 Documentation needs updating")
        
        return hooks_need_update, scripts_need_update, docs_need_update


def is_git_repo(repo_path: Path) -> bool:
    """Check if the given path is a valid Git repository."""
    try:
        subprocess.run(["git", "-C", str(repo_path), "rev-parse", "--is-inside-work-tree"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def check_git_config(repo_path: Path) -> bool:
    """Check if git user.name and user.email are configured."""
    try:
        result_name = subprocess.run(
            ["git", "-C", str(repo_path), "config", "user.name"],
            capture_output=True, text=True, check=True
        )
        result_email = subprocess.run(
            ["git", "-C", str(repo_path), "config", "user.email"],
            capture_output=True, text=True, check=True
        )
        return bool(result_name.stdout.strip()) and bool(result_email.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def run_git_command(repo_path: Path, cmd: list, check: bool = True):
    """Run a git command in the context of the target repository."""
    full_cmd = ["git", "-C", str(repo_path)] + cmd
    logger.debug(f"Running: {' '.join(full_cmd)}")
    return subprocess.run(full_cmd, check=check, capture_output=True, text=True)


def get_current_branch(repo_path: Path) -> str:
    """Get the current branch name."""
    result = run_git_command(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    return result.stdout.strip()


def get_default_branch(repo_path: Path) -> str:
    """Get the default branch name (main or master)."""
    # Try to get the default branch from remote
    result = run_git_command(repo_path, ["symbolic-ref", "refs/remotes/origin/HEAD"], check=False)
    if result.returncode == 0:
        # Extract branch name from refs/remotes/origin/main
        return result.stdout.strip().split('/')[-1]
    
    # Fallback: check if main or master exists
    result = run_git_command(repo_path, ["branch", "-l", "main"], check=False)
    if result.stdout.strip():
        return "main"
    
    result = run_git_command(repo_path, ["branch", "-l", "master"], check=False)
    if result.stdout.strip():
        return "master"
    
    return "main"  # Default to main


def has_uncommitted_changes(repo_path: Path) -> bool:
    """Check if there are uncommitted changes in the repository."""
    result = run_git_command(repo_path, ["status", "--porcelain"])
    return bool(result.stdout.strip())


def has_remote(repo_path: Path) -> bool:
    """Check if the repository has a remote configured."""
    result = run_git_command(repo_path, ["remote", "-v"], check=False)
    return bool(result.stdout.strip())


def detect_git_platform(repo_path: Path) -> Optional[str]:
    """
    Detect if repository uses GitHub or GitLab based on remote URL.
    
    Returns:
        'github', 'gitlab', or None if cannot determine
    """
    result = run_git_command(repo_path, ["remote", "get-url", "origin"], check=False)
    if result.returncode != 0:
        return None
    
    remote_url = result.stdout.strip().lower()
    
    if 'github.com' in remote_url:
        return 'github'
    elif 'gitlab.com' in remote_url or 'gitlab' in remote_url:
        return 'gitlab'
    
    return None


def install_ci_cd_files(target_repo: Path, source_dir: Path, platform: str) -> List[str]:
    """
    Install appropriate CI/CD files based on platform.
    
    Returns:
        List of files that were installed/updated
    """
    installed_files = []
    
    if platform == 'github':
        # Source and destination for GitHub Actions
        ci_source = source_dir / "ci-cd" / "github-actions-update-timeline.yml"
        ci_dest_dir = target_repo / ".github" / "workflows"
        ci_dest = ci_dest_dir / "update-timeline.yml"
        
        if ci_source.exists():
            # Create .github/workflows directory
            ci_dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if file needs updating
            if not ci_dest.exists() or not filecmp.cmp(ci_source, ci_dest, shallow=False):
                shutil.copy2(ci_source, ci_dest)
                logger.info("📄 Installed GitHub Actions workflow")
                installed_files.append(".github/workflows/update-timeline.yml")
            else:
                logger.debug("GitHub Actions workflow already up-to-date")
    
    elif platform == 'gitlab':
        # Source for GitLab CI
        ci_source = source_dir / "ci-cd" / "gitlab-ci-update-timeline.yml"
        gitlab_ci = target_repo / ".gitlab-ci.yml"
        
        if ci_source.exists():
            # Read the template
            with open(ci_source, 'r') as f:
                ci_template = f.read()
            
            # Check if .gitlab-ci.yml exists
            if gitlab_ci.exists():
                with open(gitlab_ci, 'r') as f:
                    existing = f.read()
                
                # Check if our job already exists
                if 'update-git-timeline:' not in existing:
                    # Append our job
                    with open(gitlab_ci, 'a') as f:
                        f.write('\n\n# Auto-generated by git-hooks-installer\n')
                        f.write(ci_template)
                    logger.info("📄 Added GitLab CI job to existing .gitlab-ci.yml")
                    installed_files.append(".gitlab-ci.yml")
                else:
                    logger.debug("GitLab CI job already exists")
            else:
                # Create new .gitlab-ci.yml
                with open(gitlab_ci, 'w') as f:
                    f.write(ci_template)
                logger.info("📄 Created .gitlab-ci.yml with update job")
                installed_files.append(".gitlab-ci.yml")
    
    return installed_files


def install_developer_setup_improved(target_repo: Path, source_dir: Path) -> List[str]:
    """
    FIXED: Install complete developer setup maintaining folder structure.
    
    Returns:
        List of files that were installed/updated
    """
    installed_files = []
    setup_source_dir = source_dir / "developer-setup"
    
    if not setup_source_dir.exists():
        logger.debug("No developer-setup directory found")
        return installed_files
    
    # Create developer-setup directory in target
    developer_setup_dst = target_repo / "developer-setup"
    developer_setup_dst.mkdir(parents=True, exist_ok=True)
    logger.info("📁 Created developer-setup directory")
    
    # Copy entire structure
    for item in setup_source_dir.iterdir():
        if item.is_dir():
            # Copy subdirectories (like templates/)
            dst_dir = developer_setup_dst / item.name
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(item, dst_dir)
            logger.info(f"📁 Copied directory: developer-setup/{item.name}")
            # Add all files in the directory
            for file in item.rglob("*"):
                if file.is_file():
                    rel_path = file.relative_to(setup_source_dir)
                    installed_files.append(f"developer-setup/{rel_path}")
        else:
            # Copy individual files
            dst_file = developer_setup_dst / item.name
            shutil.copy2(item, dst_file)
            installed_files.append(f"developer-setup/{item.name}")
            logger.info(f"📄 Copied: developer-setup/{item.name}")
    
    # Create convenience shell scripts in root
    create_shell_wrappers(target_repo)
    installed_files.extend(["setup-githooks.sh", "setup-githooks.ps1"])
    
    return installed_files


def create_shell_wrappers(target_repo: Path):
    """Create shell wrapper scripts for easy developer setup."""
    
    # Linux/macOS wrapper
    sh_wrapper = target_repo / "setup-githooks.sh"
    sh_content = '''#!/bin/bash
# Git hooks setup wrapper script
# Auto-generated by git-hooks-installer

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if developer-setup exists
if [ ! -d "$DIR/developer-setup" ]; then
    echo "Error: developer-setup directory not found!"
    echo "Please run the git-hooks-installer first."
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
    logger.info("📄 Created setup-githooks.sh")
    
    # Windows PowerShell wrapper
    ps1_wrapper = target_repo / "setup-githooks.ps1"
    ps1_content = '''# Git hooks setup wrapper script for Windows
# Auto-generated by git-hooks-installer

# Get the directory of this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if developer-setup exists
if (-not (Test-Path "$scriptPath\\developer-setup")) {
    Write-Host "Error: developer-setup directory not found!" -ForegroundColor Red
    Write-Host "Please run the git-hooks-installer first."
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
    logger.info("📄 Created setup-githooks.ps1")


def copy_git_hooks(src: Path, dst: Path) -> bool:
    """Copy git hooks from source to destination .git/hooks directory."""
    dst.mkdir(parents=True, exist_ok=True)
    
    hooks_copied = False
    for hook_file in src.iterdir():
        if hook_file.is_file() and not hook_file.name.endswith('.sample'):
            dst_hook = dst / hook_file.name
            shutil.copy2(hook_file, dst_hook)
            # Make executable
            dst_hook.chmod(0o755)
            logger.info(f"Copied and made executable: {hook_file.name}")
            hooks_copied = True
    
    return hooks_copied


def compare_hooks(src: Path, dst: Path) -> bool:
    """Compare hooks in source and destination directories."""
    for hook_file in src.iterdir():
        if hook_file.is_file() and not hook_file.name.endswith('.sample'):
            dst_hook = dst / hook_file.name
            if not dst_hook.exists() or not filecmp.cmp(hook_file, dst_hook, shallow=False):
                return False
    return True


def update_gitignore(repo_path: Path, source_dir: Path) -> bool:
    """Update .gitignore file with necessary patterns."""
    gitignore_manager = source_dir / "manage_gitignore.py"
    
    if not gitignore_manager.exists():
        logger.warning("⚠️  manage_gitignore.py not found, skipping .gitignore update")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(gitignore_manager), str(repo_path)],
                                capture_output=True, text=True, check=True)
        logger.info("✅ Updated .gitignore")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to update .gitignore: {e.stderr}")
        return False


def commit_changes(repo_path: Path, message: str, files_to_add: List[str]) -> bool:
    """Commit the specified files with the given message."""
    if not files_to_add:
        logger.debug("No files to commit")
        return True
    
    try:
        # Add specific files
        for file in files_to_add:
            run_git_command(repo_path, ["add", file])
        
        # Check if there are changes to commit
        result = run_git_command(repo_path, ["diff", "--cached", "--quiet"], check=False)
        if result.returncode == 0:
            logger.debug("No changes to commit")
            return True
        
        # Commit
        run_git_command(repo_path, ["commit", "-m", message])
        logger.info("✅ Changes committed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error committing changes: {e}")
        return False


def push_changes(repo_path: Path, branch: str) -> bool:
    """Push changes to remote repository."""
    try:
        run_git_command(repo_path, ["push", "origin", branch])
        logger.info(f"✅ Pushed changes to origin/{branch}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error pushing changes: {e}")
        return False


def temporarily_disable_hook(repo_path: Path, hook_name: str):
    """Temporarily disable a git hook by renaming it."""
    hook_path = repo_path / ".git" / "hooks" / hook_name
    disabled_path = repo_path / ".git" / "hooks" / f"{hook_name}.disabled"
    
    if hook_path.exists() and not disabled_path.exists():
        hook_path.rename(disabled_path)
        logger.debug(f"Temporarily disabled {hook_name} hook")
        return True
    return False

def re_enable_hook(repo_path: Path, hook_name: str):
    """Re-enable a temporarily disabled git hook."""
    hook_path = repo_path / ".git" / "hooks" / hook_name
    disabled_path = repo_path / ".git" / "hooks" / f"{hook_name}.disabled"
    
    if disabled_path.exists() and not hook_path.exists():
        disabled_path.rename(hook_path)
        logger.debug(f"Re-enabled {hook_name} hook")
        return True
    return False

def merge_branch(repo_path: Path, source_branch: str, target_branch: str) -> bool:
    """Merge source branch into target branch."""
    # Temporarily disable post-commit hook to avoid conflicts during merge
    hook_disabled = temporarily_disable_hook(repo_path, "post-commit")
    
    try:
        # Ensure we're on the target branch
        run_git_command(repo_path, ["checkout", target_branch])
        
        # Check for uncommitted changes before merging and handle them
        status_result = run_git_command(repo_path, ["status", "--porcelain"], check=False)
        if status_result.returncode == 0 and status_result.stdout.strip():
            logger.info(f"📋 Uncommitted changes detected on {target_branch}, handling them...")
            
            # Commit any uncommitted changes on main (likely from post-commit hooks)
            additional_files = []
            for line in status_result.stdout.strip().split('\n'):
                if line.startswith('??') or line.startswith('A ') or line.startswith('M '):
                    file_path = line[3:].strip()
                    additional_files.append(file_path)
                    logger.info(f"   Adding: {file_path}")
            
            if additional_files:
                # Add and commit the additional files
                for file in additional_files:
                    run_git_command(repo_path, ["add", file])
                run_git_command(repo_path, ["commit", "-m", f"docs: Auto-commit files created by post-commit hooks on {target_branch}"])
                logger.info(f"✅ Committed {len(additional_files)} uncommitted files on {target_branch}")
        
        # Perform the merge
        run_git_command(repo_path, ["merge", source_branch, "--no-ff", "-m", 
                                    f"Merge branch '{source_branch}' - Update git hooks and scripts"])
        logger.info(f"✅ Merged {source_branch} into {target_branch}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Merge failed: {e}")
        logger.error(f"❌ Git command stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
        
        # Check if this is a merge conflict
        status_result = run_git_command(repo_path, ["status", "--porcelain"], check=False)
        if status_result.returncode == 0 and "UU " in status_result.stdout:
            logger.error("❌ Merge conflict detected")
            logger.info("📋 Conflicted files:")
            for line in status_result.stdout.strip().split('\n'):
                if line.startswith('UU '):
                    logger.info(f"   {line}")
        
        # Try to abort the merge if it failed
        abort_result = run_git_command(repo_path, ["merge", "--abort"], check=False)
        if abort_result.returncode == 0:
            logger.info("✅ Merge aborted successfully")
        else:
            logger.warning("⚠️  Could not abort merge")
        
        return False
    finally:
        # Always re-enable the hook if we disabled it
        if hook_disabled:
            re_enable_hook(repo_path, "post-commit")


def setup_git_hooks(
        target_repo: Path,
        source_dir: Path,
        auto_merge: bool = False,
        push: bool = True,
        force: bool = False,
        no_ci: bool = False):
    """
    Main function to set up git hooks, scripts, and documentation.
    
    Args:
        target_repo (Path): Path to the target Git repository.
        source_dir (Path): Path to the source containing git-hooks/, scripts/, and docs/.
        auto_merge (bool): Whether to automatically merge the changes.
        push (bool): Whether to push changes to remote.
        force (bool): Force update even if versions match.
    """
    logger.info(f"🔍 Running from: {os.getcwd()}")
    logger.info(f"🎯 Target repository: {target_repo}")
    logger.info(f"📂 Source directory: {source_dir}")
    
    # Create installer instance
    installer = GitHooksInstaller(target_repo, source_dir)
    
    # Check if target is a git repository
    if not is_git_repo(target_repo):
        logger.error("❌ Error: Target is not a Git repository.")
        return False
    
    # Check git configuration
    if not check_git_config(target_repo):
        logger.warning("⚠️  Git user.name and/or user.email not configured.")
        logger.info("Please configure with:")
        logger.info('  git config user.name "Your Name"')
        logger.info('  git config user.email "your@email.com"')
    
    # Define paths
    hooks_src = source_dir / "git-hooks"
    hooks_dst = target_repo / ".git" / "hooks"
    scripts_src = source_dir / "scripts"
    scripts_dst = target_repo / "scripts"
    docs_src = source_dir / "docs"
    docs_dst = target_repo / "docs" / "githooks"
    
    # Check for updates
    logger.info("🔎 Checking for updates...")
    hooks_need_update, scripts_need_update, docs_need_update = installer.check_if_update_needed(hooks_dst)
    
    if not force and not hooks_need_update and not scripts_need_update and not docs_need_update:
        logger.info("✅ Everything is up-to-date! Use --force to reinstall anyway.")
        return True
    
    # Check for uncommitted changes
    original_branch = get_current_branch(target_repo)
    default_branch = get_default_branch(target_repo)
    
    logger.info(f"Current branch: {original_branch}, Default branch: {default_branch}")
    
    # Determine if we need to create a branch
    need_branch = (scripts_need_update or docs_need_update or force) and (
        original_branch == default_branch or 
        has_uncommitted_changes(target_repo)
    )
    
    branch_name = None
    if need_branch:
        logger.info("📄 Changes detected - will create a branch")
        if has_uncommitted_changes(target_repo):
            logger.error("❌ Error: Uncommitted changes detected.")
            logger.info("Please commit or stash your changes before running this script.")
            return False
        
        # Create a new branch
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"feat/update-githooks-installation-{timestamp}"
        run_git_command(target_repo, ["checkout", "-b", branch_name])
        logger.info(f"Created and switched to branch: {branch_name}")
    
    # Track files to commit
    files_to_commit = []
    
    # Install/update git hooks
    if hooks_need_update or force:
        logger.info("📄 Installing git hooks to .git/hooks/...")
        if hooks_src.exists() and copy_git_hooks(hooks_src, hooks_dst):
            # Git hooks in .git/hooks are not tracked by git
            pass
        else:
            logger.warning("⚠️  No git hooks found to install")
    
    # Update scripts
    scripts_copied = []
    if scripts_need_update or force:
        logger.info("📄 Updating scripts...")
        scripts_copied = installer.copy_directory_improved(scripts_src, scripts_dst, "scripts")
        files_to_commit.extend(scripts_copied)
    
    # Update documentation
    docs_copied = []
    if docs_need_update or force:
        logger.info("📄 Updating documentation...")
        docs_copied = installer.copy_directory_improved(docs_src, docs_dst, "docs")
        files_to_commit.extend(docs_copied)
    
    # Update .gitignore
    if update_gitignore(target_repo, source_dir):
        files_to_commit.append(".gitignore")
    
    # Install CI/CD files
    if not no_ci:
        platform = detect_git_platform(target_repo)
        if platform:
            logger.info(f"📄 Detected {platform.title()} repository")
            ci_files = install_ci_cd_files(target_repo, source_dir, platform)
            files_to_commit.extend(ci_files)
    else:
        logger.info("⏭️  Skipping CI/CD installation (--no-ci flag)")
    
    # Install developer setup files
    setup_files = install_developer_setup_improved(target_repo, source_dir)
    if setup_files:
        files_to_commit.extend(setup_files)
        logger.info("✅ Installed developer setup scripts")
    else:
        logger.debug("No developer setup files found or already up-to-date")
    
    # Save version info
    if need_branch and (scripts_copied or docs_copied or hooks_need_update or force):
        scripts_hash = installer.calculate_directory_hash(scripts_src)
        docs_hash = installer.calculate_directory_hash(docs_src)
        hooks_hash = installer.calculate_directory_hash(hooks_src)
        installer.save_version_info(scripts_hash, docs_hash, hooks_hash)
        files_to_commit.append("docs/githooks/.githooks-version.json")
    
    # Commit changes if we created a branch
    if branch_name and files_to_commit:
        commit_message = f"feat: Update git hooks installation - v0.6\n\n" \
                        f"- Updated git hooks to latest version\n" \
                        f"- {'Updated' if scripts_copied else 'Verified'} scripts\n" \
                        f"- {'Updated' if docs_copied else 'Verified'} documentation\n" \
                        f"- Installed developer setup with proper structure\n" \
                        f"- Added shell wrapper scripts\n" \
                        f"- Created version tracking file"
        
        if commit_changes(target_repo, commit_message, files_to_commit):
            logger.info("✅ Changes committed successfully")
            
            # Push if requested and remote exists
            if push and has_remote(target_repo):
                if push_changes(target_repo, branch_name):
                    logger.info(f"✅ Pushed branch '{branch_name}' to remote")
                    
                    # Generate PR URL for GitHub
                    platform = detect_git_platform(target_repo)
                    if platform == 'github':
                        result = run_git_command(target_repo, ["remote", "get-url", "origin"], check=False)
                        if result.returncode == 0:
                            remote_url = result.stdout.strip()
                            # Convert SSH to HTTPS URL
                            if remote_url.startswith('git@github.com:'):
                                remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
                            if remote_url.endswith('.git'):
                                remote_url = remote_url[:-4]
                            pr_url = f"{remote_url}/pull/new/{branch_name}"
                            logger.info(f"📝 Create a pull request at: {pr_url}")
    
    # Handle merging if we created a branch
    if branch_name and auto_merge:
        logger.info(f"🔀 Auto-merging to {original_branch}...")
        
        # First check if post-commit hook created any new files we need to commit
        status_result = run_git_command(target_repo, ["status", "--porcelain"], check=False)
        if status_result.returncode == 0 and status_result.stdout.strip():
            logger.info("📋 Post-commit hook created additional files, committing them...")
            additional_files = []
            for line in status_result.stdout.strip().split('\n'):
                if line.startswith('??') or line.startswith('A '):
                    file_path = line[3:].strip()
                    additional_files.append(file_path)
                    logger.info(f"   Adding: {file_path}")
            
            if additional_files:
                # Add and commit the additional files
                for file in additional_files:
                    run_git_command(target_repo, ["add", file])
                run_git_command(target_repo, ["commit", "-m", "docs: Add post-commit generated documentation"])
                logger.info("✅ Committed post-commit generated files")
        
        if merge_branch(target_repo, branch_name, original_branch):
            if push and has_remote(target_repo):
                push_changes(target_repo, original_branch)
        else:
            logger.warning(f"⚠️  Could not auto-merge. Please merge manually.")
            logger.info(f"   Run: git checkout {original_branch} && git merge {branch_name}")
    
    # Return to original branch if we didn't auto-merge
    if branch_name and not auto_merge:
        run_git_command(target_repo, ["checkout", original_branch])
        logger.info(f"↩️  Returned to original branch: {original_branch}")
        logger.info(f"ℹ️  Branch '{branch_name}' created with changes.")
        logger.info(f"   To merge manually: git checkout {original_branch}&& git merge {{branch_name}}")
    
    # Summary
    logger.info("✅ Git hooks installed to " + str(target_repo / ".git" / "hooks"))
    if scripts_copied:
        logger.info(f"✅ Scripts updated: {len(scripts_copied)} files")
    if docs_copied:
        logger.info(f"✅ Documentation updated: {len(docs_copied)} files in docs/githooks/")
    
    return True


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Install/update git hooks, scripts, and documentation in a Git repository."
    )
    parser.add_argument("target", type=str, nargs='?', default=".",
                        help="Path to the target Git repository (default: current directory)")
    parser.add_argument("--source", type=str, default=os.getenv("GITHOOKS_SOURCE", "."),
                        help="Path to the source directory containing git-hooks/,"
                             " scripts/, and docs/")
    parser.add_argument("--auto-merge", action="store_true",
                        help="Automatically merge the changes to the default branch")
    parser.add_argument("--no-push", action="store_true",
                        help="Don't push changes to remote")
    parser.add_argument("--force", action="store_true",
                        help="Force reinstall even if up-to-date")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--no-ci", action="store_true",
                        help="Skip CI/CD file installation")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    target_path = Path(args.target).resolve()
    source_path = Path(args.source).resolve()
    
    success = setup_git_hooks(
        target_path,
        source_path,
        auto_merge=args.auto_merge,
        push=not args.no_push,
        force=args.force,
        no_ci=args.no_ci
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()