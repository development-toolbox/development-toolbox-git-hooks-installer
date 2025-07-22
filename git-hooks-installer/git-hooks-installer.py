#!/usr/bin/env python3
# githooks-install.py
# version 0.5
# Author: Johan Sörell
# First version Date: 2025-05-30
# Updated: 2025-07-22
# Bugfixes and improvements
# - will fix that the merge branch is always the branch we are currently on
# - will fix that the branch name is always the same, even if we force update

# License: MIT License
"""
This script sets up git hooks, scripts, and documentation in a specified Git repository.
It copies the hooks from a source directory and makes them executable,
and also copies scripts and docs while checking for changes. If changes are detected, 
it creates a new branch, commits them, and optionally pushes/merges.
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
        self.version_info = {}
        
    def calculate_directory_hash(self, directory: Path) -> str:
        """Calculate a hash of all files in a directory to detect changes."""
        if not directory.exists():
            return ""
            
        hash_md5 = hashlib.md5()
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                # Include relative path and content in hash
                rel_path = file_path.relative_to(directory)
                hash_md5.update(str(rel_path).encode())
                
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def load_version_info(self) -> dict:
        """Load version information from target repository."""
        # Try new location first (in docs/githooks/)
        version_file = self.target_repo / "docs" / "githooks" / self.VERSION_FILE
        
        # Fallback to old location (root)
        if not version_file.exists():
            version_file = self.target_repo / self.VERSION_FILE
        
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load version info: {e}")
        
        return {}
    
    def save_version_info(self, scripts_hash: str, docs_hash: str, 
                         managed_scripts: list, managed_docs: list) -> Path:
        """Save version information to track what we've installed."""
        version_info = {
            "version": "2.1",
            "last_updated": datetime.now().isoformat(),
            "scripts_hash": scripts_hash,
            "docs_hash": docs_hash,
            "managed_files": {
                "scripts": sorted(managed_scripts),
                "docs": sorted(managed_docs)
            },
            "installer": "githooks-install.py"
        }
        
        # Save in docs/githooks/ directory
        version_dir = self.target_repo / "docs" / "githooks"
        version_dir.mkdir(parents=True, exist_ok=True)
        version_file = version_dir / self.VERSION_FILE
        
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        return version_file
    
    def get_managed_files(self, category: str) -> set:
        """Get list of files that we previously installed for a category."""
        version_info = self.load_version_info()
        
        # Handle old format (list) and new format (dict with categories)
        managed = version_info.get("managed_files", {})
        if isinstance(managed, list):
            # Old format - assume all files are scripts
            return set(managed) if category == "scripts" else set()
        else:
            # New format
            return set(managed.get(category, []))
    
    def copy_files_safely(self, src: Path, dst: Path, category: str) -> list:
        """
        Safely copy files without deleting existing files.
        Only updates files that are part of the git hooks installation.
        Returns list of files that were copied.
        """
        if not src.exists():
            logger.debug(f"Source {category} directory {src} does not exist.")
            return []
        
        # Create destination if it doesn't exist
        dst.mkdir(parents=True, exist_ok=True)
        
        copied_files = []
        
        # Get list of files we're managing
        managed_files = self.get_managed_files(category)
        new_managed_files = []
        
        logger.debug(f"Previously managed {category} files: {managed_files}")
        logger.debug(f"Scanning source directory: {src}")
        
        # Copy only our files
        for item in src.rglob('*'):
            if item.is_file() and not item.name.startswith('.'):
                relative = item.relative_to(src)
                target = dst / relative
                relative_str = str(relative)
                
                logger.debug(f"Checking {category} file: {relative_str}")
                
                # Check if file exists and if we should update it
                should_copy = False
                
                if not target.exists():
                    # New file
                    should_copy = True
                    logger.info(f"📄 New {category} file to install: {relative}")
                elif relative_str in managed_files:
                    # We manage this file, check if it changed
                    if not filecmp.cmp(item, target, shallow=False):
                        should_copy = True
                        logger.info(f"🔄 Updating managed {category} file: {relative}")
                    else:
                        logger.debug(f"✓ Managed {category} file unchanged: {relative}")
                else:
                    # File exists but we don't manage it
                    logger.warning(f"⚠️  {category.capitalize()} file exists but not managed by githooks: {relative}")
                    logger.warning(f"   Skipping to avoid overwriting your file!")
                    continue
                
                if should_copy:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
                    if category == "scripts":
                        target.chmod(0o755)
                    copied_files.append(relative_str)
                
                new_managed_files.append(relative_str)
        
        # Warn about files we previously managed but are no longer in source
        orphaned_files = set(managed_files) - set(new_managed_files)
        if orphaned_files:
            logger.warning(f"⚠️  Previously managed {category} files no longer in source:")
            for file in orphaned_files:
                logger.warning(f"   - {file}")
            logger.warning("   These files were NOT deleted. Remove manually if needed.")
        
        self.managed_files[category] = set(new_managed_files)
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
        scripts_need_update = current_scripts_hash != version_info.get("scripts_hash", "") if scripts_src.exists() else False
        docs_need_update = current_docs_hash != version_info.get("docs_hash", "") if docs_src.exists() else False
        
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

# Detect if the repository uses GitHub or GitLab based on remote URL
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

def install_developer_setup_files(target_repo: Path, source_dir: Path) -> List[str]:
    """
    Install developer setup scripts in repository root.
    
    Returns:
        List of files that were installed/updated
    """
    installed_files = []
    setup_source_dir = source_dir / "developer-setup"
    
    if not setup_source_dir.exists():
        logger.debug("No developer-setup directory found")
        return installed_files
    
    # Files to copy to repository root
    setup_files = [
        ("setup-githooks.sh", "setup-githooks.sh"),
        ("setup-githooks.ps1", "setup-githooks.ps1"),
        ("SETUP-GITHOOKS.md", "SETUP-GITHOOKS.md")
    ]
    
    for source_name, dest_name in setup_files:
        source_file = setup_source_dir / source_name
        dest_file = target_repo / dest_name
        
        if source_file.exists():
            # Check if update needed
            if not dest_file.exists() or not filecmp.cmp(source_file, dest_file, shallow=False):
                shutil.copy2(source_file, dest_file)
                # Make shell scripts executable
                if dest_name.endswith('.sh'):
                    dest_file.chmod(0o755)
                logger.info(f"📄 Installed developer setup: {dest_name}")
                installed_files.append(dest_name)
            else:
                logger.debug(f"Developer setup file already up-to-date: {dest_name}")
    
    return installed_files

# ADD HERE - After install_ci_cd_files function
def update_gitignore_file(repo_path: Path) -> None:
    """Update .gitignore with required patterns for git hooks."""
    try:
        # Import the GitIgnoreManager
        from manage_gitignore import update_gitignore
        
        logger.info("📝 Updating .gitignore file...")
        if update_gitignore(repo_path):
            logger.info("✅ Updated .gitignore with required patterns")
        else:
            logger.info("✅ .gitignore already contains all required patterns")
    except ImportError:
        logger.warning("⚠️  manage_gitignore.py not found, skipping .gitignore update")
    except Exception as e:
        logger.warning(f"⚠️  Failed to update .gitignore: {e}")

def compare_hooks(src: Path, dst: Path) -> bool:
    """
    Compare hooks in source and destination directories.
    Returns True if they are identical, False if they differ.
    """
    if not src.exists() or not dst.exists():
        return False
    
    src_files = {f.name for f in src.iterdir() if f.is_file()}
    dst_files = {f.name for f in dst.iterdir() if f.is_file() and not f.name.endswith('.sample')}
    
    # Check if all source files exist in destination
    for hook_name in src_files:
        src_hook = src / hook_name
        dst_hook = dst / hook_name
        
        if not dst_hook.exists():
            logger.debug(f"Hook missing in destination: {hook_name}")
            return False
        
        # Compare file contents
        if not filecmp.cmp(src_hook, dst_hook, shallow=False):
            logger.debug(f"Hook differs: {hook_name}")
            return False
    
    return True

def copy_and_make_executable(src: Path, dst: Path):
    """Copy all files from src to dst and make them executable."""
    if not src.exists():
        raise FileNotFoundError(f"Source directory {src} does not exist.")
    
    # Ensure destination directory exists
    dst.mkdir(parents=True, exist_ok=True)
    
    for item in src.iterdir():
        if item.is_file():
            dst_file = dst / item.name
            shutil.copy2(item, dst_file)  # Use copy2 to preserve metadata
            dst_file.chmod(0o755)
            logger.info(f"Copied and made executable: {item.name}")

def push_branch(repo_path: Path, branch_name: str) -> bool:
    """Push the branch to remote."""
    push_result = run_git_command(repo_path, ["push", "-u", "origin", branch_name], check=False)
    
    if push_result.returncode != 0:
        logger.error(f"Failed to push branch: {push_result.stderr}")
        return False
    
    logger.info(f"✅ Pushed branch '{branch_name}' to remote")
    return True

def create_pull_request_url(repo_path: Path, branch_name: str) -> str:
    """Try to generate a pull request URL based on the remote URL."""
    remote_result = run_git_command(repo_path, ["remote", "get-url", "origin"], check=False)
    if remote_result.returncode == 0:
        remote_url = remote_result.stdout.strip()
        
        # GitHub
        if "github.com" in remote_url:
            if remote_url.startswith("git@"):
                # Convert SSH to HTTPS
                remote_url = remote_url.replace("git@github.com:", "https://github.com/")
            remote_url = remote_url.replace(".git", "")
            return f"{remote_url}/pull/new/{branch_name}"
        
        # GitLab
        elif "gitlab.com" in remote_url:
            if remote_url.startswith("git@"):
                remote_url = remote_url.replace("git@gitlab.com:", "https://gitlab.com/")
            remote_url = remote_url.replace(".git", "")
            return f"{remote_url}/-/merge_requests/new?merge_request[source_branch]={branch_name}"
        
        # Bitbucket
        elif "bitbucket.org" in remote_url:
            if remote_url.startswith("git@"):
                remote_url = remote_url.replace("git@bitbucket.org:", "https://bitbucket.org/")
            remote_url = remote_url.replace(".git", "")
            return f"{remote_url}/pull-requests/new?source={branch_name}"
    
    return ""

def merge_branch(repo_path: Path, branch_name: str, target_branch: str) -> bool:
    """Merge the feature branch into the target branch."""
    # Switch to target branch
    checkout_result = run_git_command(repo_path, ["checkout", target_branch])
    if checkout_result.returncode != 0:
        logger.error(f"Failed to checkout {target_branch}: {checkout_result.stderr}")
        return False
    
    # Merge the feature branch
    merge_result = run_git_command(repo_path, ["merge", branch_name, "--no-ff", "-m", f"Merge branch '{branch_name}' - Update git hooks and scripts"])
    if merge_result.returncode != 0:
        logger.error(f"Failed to merge: {merge_result.stderr}")
        # Clean up any staged files
        logger.warning("⚠️  Merge failed, cleaning up...")
        run_git_command(repo_path, ["merge", "--abort"], check=False)
        return False
    
    logger.info(f"✅ Merged '{branch_name}' into '{target_branch}'")
    
    # Delete the feature branch
    delete_result = run_git_command(repo_path, ["branch", "-d", branch_name], check=False)
    if delete_result.returncode == 0:
        logger.info(f"✅ Deleted local branch '{branch_name}'")
    
    return True

def get_conventional_branch_name(hooks_need_update: bool, 
                               scripts_need_update: bool, 
                               docs_need_update: bool,
                               force: bool = False) -> str:
    """
    Generate a branch name following conventional commits pattern.
    
    Args:
        hooks_need_update: Whether git hooks need to be updated
        scripts_need_update: Whether scripts need to be updated
        docs_need_update: Whether documentation needs to be updated
        force: Whether this is a forced reinstall
        
    Returns:
        Branch name in format: <type>/<description>-<timestamp>
        
    Examples:
        feat/install-githooks-20250623-210623
        feat/update-git-hooks-20250623-210623
        feat/update-hook-scripts-20250623-210623
        docs/update-githooks-docs-20250623-210623
        feat/update-githooks-installation-20250623-210623
        feat/force-update-githooks-20250623-210623
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    if force:
        return f"feat/force-update-githooks-{timestamp}"
    
    # Count how many components need updating
    updates = sum([hooks_need_update, scripts_need_update, docs_need_update])
    
    if updates == 0:
        # Nothing needs updating - this is a fresh install
        return f"feat/install-githooks-{timestamp}"
    elif updates == 1:
        # Only one component needs updating - use specific name
        if hooks_need_update:
            return f"feat/update-git-hooks-{timestamp}"
        elif scripts_need_update:
            return f"feat/update-hook-scripts-{timestamp}"
        elif docs_need_update:
            return f"docs/update-githooks-docs-{timestamp}"
        else:
            return f"feat/update-githooks-{timestamp}"
    else:
        # Multiple components need updating (updates > 1)
        # Use general name since we're updating the entire installation
        return f"feat/update-githooks-installation-{timestamp}"

def setup_git_hooks(target_repo: Path, source_dir: Path, auto_merge: bool = False, push: bool = True, force: bool = False, no_ci: bool = False):
    """
    Main function to set up git hooks in a target repository.

    Args:
        target_repo (Path): Path to the target Git repository.
        source_dir (Path): Path to the source containing git-hooks/, scripts/, and docs/.
        auto_merge (bool): Whether to automatically merge the changes.
        push (bool): Whether to push changes to remote.
        force (bool): Force update even if versions match.
    """
    logger.info(f"🔍 Running from: {Path.cwd()}")
    logger.info(f"🎯 Target repository: {target_repo}")
    logger.info(f"📂 Source directory: {source_dir}")

    # Validate target repository
    if not target_repo.exists():
        raise RuntimeError(f"Target repository path does not exist: {target_repo}")
    
    if not is_git_repo(target_repo):
        raise RuntimeError(f"{target_repo} is not a git repository.")
    
    # Check git configuration
    if not check_git_config(target_repo):
        logger.warning("⚠️  Git user.name and/or user.email not configured in target repository.")
        logger.warning("   This may cause commit to fail. Configure with:")
        logger.warning(f"   git -C {target_repo} config user.name 'Your Name'")
        logger.warning(f"   git -C {target_repo} config user.email 'your@email.com'")
    
    # Check for uncommitted changes
    if has_uncommitted_changes(target_repo):
        logger.error("❌ Target repository has uncommitted changes. Please commit or stash them first.")
        return False
    
    logger.info("🔎 Checking for updates...")
    
    # Initialize installer
    installer = GitHooksInstaller(target_repo, source_dir)
    
    # Validate source directories first
    hooks_src = source_dir / "git-hooks"
    scripts_src = source_dir / "scripts"
    docs_src = source_dir / "docs"
    
    if not hooks_src.exists():
        raise FileNotFoundError(f"Source hooks directory not found: {hooks_src}")
    
    # Define destination paths
    hooks_dst = target_repo / ".git" / "hooks"
    scripts_dst = target_repo / "scripts"
    docs_dst = target_repo / "docs" / "githooks"
    
    # 🔐 Security check: Prevent writing outside target repo structure
    if not scripts_dst.resolve().is_relative_to(target_repo.resolve()):
        raise ValueError(f"🚫 Unsafe target scripts directory: {scripts_dst}")
    if not hooks_dst.resolve().is_relative_to((target_repo / ".git" / "hooks").parent.resolve()):
        raise ValueError(f"🚫 Unsafe target hooks directory: {hooks_dst}")

    
    # Check if update is needed - BEFORE doing anything!
    hooks_need_update, scripts_need_update, docs_need_update = installer.check_if_update_needed(hooks_dst)
    
    if not force and not hooks_need_update and not scripts_need_update and not docs_need_update:
        logger.info("✅ Everything is already up-to-date!")
        logger.info("   No changes needed. Use --force to reinstall anyway.")
        return True
    
    # Get current branch and default branch
    original_branch = get_current_branch(target_repo)
    default_branch = get_default_branch(target_repo)
    logger.info(f"Current branch: {original_branch}, Default branch: {default_branch}")
    
    files_to_commit = []
    need_branch = False
    
    # Check if we need a branch (for ANY changes including hooks)
    if (hooks_need_update or scripts_need_update or docs_need_update or force):
        need_branch = True
        logger.info("📄 Changes detected - will create a branch")
    
    # If we need to make ANY changes, create branch first
    branch_name = None
    if need_branch:
        # Pull latest changes on current branch if remote exists
        if has_remote(target_repo):
            logger.info(f"📥 Pulling latest changes on {original_branch}...")
            pull_result = run_git_command(target_repo, ["pull"], check=False)
            if pull_result.returncode != 0:
                logger.warning(f"Pull failed (might be okay if no upstream): {pull_result.stderr}")
        

        # Create a branch name following conventional commits pattern
        branch_name = get_conventional_branch_name(
            hooks_need_update,
            scripts_need_update, 
            docs_need_update,
            force
        )
        
        # Create and checkout new branch
        create_result = run_git_command(target_repo, ["checkout", "-b", branch_name])
        if create_result.returncode != 0:
            logger.error(f"Failed to create branch: {create_result.stderr}")
            return False
        
        logger.info(f"Created and switched to branch: {branch_name}")
    
    # Now and ONLY now, after branch is created, we can copy files
    scripts_copied = []
    docs_copied = []
    
    # Copy hooks if needed (even though they go to .git/, we do this AFTER branch creation)
    if hooks_need_update or force:
        logger.info("📄 Installing git hooks to .git/hooks/...")
        copy_and_make_executable(hooks_src, hooks_dst)
    else:
        logger.info("✅ Git hooks already up-to-date")
    
    # Copy scripts if needed
    if scripts_src.exists() and (scripts_need_update or force):
        logger.info("📄 Updating scripts...")
        scripts_copied = installer.copy_files_safely(scripts_src, scripts_dst, "scripts")
        if scripts_copied:
            files_to_commit.append("scripts")
    
    # Copy docs if needed
    if docs_src.exists() and (docs_need_update or force):
        logger.info("📄 Updating documentation...")
        docs_copied = installer.copy_files_safely(docs_src, docs_dst, "docs")
        if docs_copied:
            files_to_commit.append("docs/githooks")

    # ADD THE GITIGNORE AND CI/CD INSTALLATION HERE
    # Update .gitignore if needed
    update_gitignore_file(target_repo)
    if (target_repo / ".gitignore").exists():
        files_to_commit.append(".gitignore")
    
    # Detect and install CI/CD files
    if not no_ci:
        platform = detect_git_platform(target_repo)
        if platform:
            logger.info(f"🔍 Detected {platform.title()} repository")
            ci_files = install_ci_cd_files(target_repo, source_dir, platform)
            if ci_files:
                files_to_commit.extend(ci_files)
        else:
            logger.debug("No GitHub/GitLab remote detected, skipping CI/CD setup")
    else:
        logger.info("⏭️  Skipping CI/CD installation (--no-ci flag)")

    # Install developer setup files
    setup_files = install_developer_setup_files(target_repo, source_dir)
    if setup_files:
        files_to_commit.extend(setup_files)
        logger.info("✅ Installed developer setup scripts")
    else:
        logger.debug("No developer setup files found or already up-to-date")
    
    # Save version info if we made changes
    if need_branch and (scripts_copied or docs_copied or hooks_need_update or force):
        scripts_hash = installer.calculate_directory_hash(scripts_src)
        docs_hash = installer.calculate_directory_hash(docs_src)
        
        version_file = installer.save_version_info(
            scripts_hash, docs_hash,
            list(installer.managed_files.get("scripts", [])),
            list(installer.managed_files.get("docs", []))
        )
        files_to_commit.append("docs/githooks/.githooks-version.json")
        
        # Commit the changes
        for file in files_to_commit:
            add_result = run_git_command(target_repo, ["add", file])
            if add_result.returncode != 0:
                logger.error(f"Failed to add file {file}: {add_result.stderr}")
        
        # Check if there are staged changes
        diff_result = run_git_command(target_repo, ["diff", "--cached", "--quiet"], check=False)
        
        if diff_result.returncode != 0:  # There are changes
            commit_message = "chore(githooks): Update git hooks installation\n\n"
            if hooks_need_update or force:
                commit_message += "- Updated hooks in .git/hooks\n"
            if scripts_copied:
                commit_message += f"- Updated {len(scripts_copied)} script files\n"
            if docs_copied:
                commit_message += f"- Updated {len(docs_copied)} documentation files\n"
            commit_message += "- Updated version tracking file\n"
            commit_message += "- Automated update by githooks-install.py"
            
            commit_result = run_git_command(target_repo, [
                "commit", "-m", commit_message
            ])
            
            if commit_result.returncode != 0:
                logger.error(f"Failed to commit: {commit_result.stderr}")
                # Try to restore original branch
                run_git_command(target_repo, ["checkout", original_branch], check=False)
                return False
            
            logger.info("✅ Changes committed successfully")
        else:
            logger.info("No changes to commit")
    
    # Push if requested and remote exists and we created a branch
    pushed = False
    if branch_name and push and has_remote(target_repo):
        pushed = push_branch(target_repo, branch_name)
        
        if pushed:
            pr_url = create_pull_request_url(target_repo, branch_name)
            if pr_url:
                logger.info(f"📝 Create a pull request at: {pr_url}")
    
    # Handle merging if we created a branch
    if branch_name and auto_merge:
        logger.info(f"🔀 Auto-merging to {original_branch}...")
        if merge_branch(target_repo, branch_name, original_branch):
            if push and has_remote(target_repo):
                push_result = run_git_command(target_repo, ["push"], check=False)
                if push_result.returncode == 0:
                    logger.info(f"✅ Pushed merged changes to remote {original_branch}")
                    # Delete remote branch if it was pushed
                    if pushed:
                        run_git_command(target_repo, ["push", "origin", "--delete", branch_name], check=False)
                else:
                    logger.warning("Failed to push merged changes")
    elif branch_name:
        logger.info(f"ℹ️  Branch '{branch_name}' created with changes.")
        logger.info(f"   To merge manually: git checkout {original_branch} && git merge {branch_name}")

    # Return to original branch if different from current
    if branch_name:
        current = get_current_branch(target_repo)
        if current != original_branch and original_branch != branch_name:
            run_git_command(target_repo, ["checkout", original_branch], check=False)
            logger.info(f"↩️  Returned to original branch: {original_branch}")
    
    # Final status messages
    if hooks_need_update or force:
        logger.info(f"✅ Git hooks installed to {hooks_dst}")
    if scripts_copied:
        logger.info(f"✅ Scripts updated: {len(scripts_copied)} files")
    elif scripts_src.exists() and (scripts_need_update or force):
        logger.info("✅ Scripts were already managed and up-to-date")
    if docs_copied:
        logger.info(f"✅ Documentation updated: {len(docs_copied)} files in docs/githooks/")
    elif docs_src.exists() and (docs_need_update or force):
        logger.info("✅ Documentation was already managed and up-to-date")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check and update git hooks, scripts, and documentation in a target Git repository.",
        epilog="Example: python githooks-install.py /path/to/repo --source /path/to/hooks-source"
    )
    parser.add_argument("target_repo", type=str, nargs='?', default=os.getenv("TARGET_REPO"),
                        help="Path to the target Git repository")
    parser.add_argument("--source", type=str, default=os.getenv("GITHOOKS_SOURCE", "."),
                        help="Path to the source directory containing git-hooks/, scripts/, and docs/")
    parser.add_argument("--auto-merge", action="store_true", 
                        help="Automatically merge the changes to the default branch")
    parser.add_argument("--no-push", action="store_true",
                        help="Don't push changes to remote")
    parser.add_argument("--force", action="store_true",
                        help="Force reinstall even if versions match")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-ci", action="store_true",
                    help="Skip CI/CD file installation")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.target_repo:
        parser.error("Target repository path is required either as an argument or via .env file")
    
    try:
        target_path = Path(args.target_repo).resolve()
        source_path = Path(args.source).resolve()
        
        success = setup_git_hooks(
            target_path, 
            source_path, 
            auto_merge=args.auto_merge,
            push=not args.no_push,
            force=args.force,
            no_ci=args.no_ci
        )
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    else:
        # Don't show success message if nothing was done
        sys.exit(0)