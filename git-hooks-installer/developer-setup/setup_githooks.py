#!/usr/bin/env python3
"""
setup_githooks.py - Developer setup script for git hooks
Version: 0.5
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

# Version of this installer
INSTALLER_VERSION = "0.5"
INSTALLER_URL = "https://github.com/development-toolbox/development-toolbox-git-hooks-installer"
INSTALLER_ISSUES = "https://github.com/development-toolbox/development-toolbox-git-hooks-installer/issues"

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def print_color(message: str, color: str = Colors.NC):
    """Print message in color."""
    print(f"{color}{message}{Colors.NC}")

def check_git_repo():
    """Check if we're in a git repository."""
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_repo_root():
    """Get repository root directory."""
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return None

def check_hook_version(hook_path: Path):
    """
    Check if hook exists and what version.
    Returns: 
        0 - Current version
        1 - Different version
        2 - Not installed
    """
    if not hook_path.exists():
        return 2
    
    with open(hook_path, 'r') as f:
        content = f.read()
        if f"setup_githooks.py v{INSTALLER_VERSION}" in content:
            return 0
        else:
            return 1

def install_hook_from_template(template_path: Path, hook_path: Path):
    """Install hook from template file."""
    # Read template
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace version placeholder if exists
    hook_content = template.replace("{{VERSION}}", INSTALLER_VERSION)
    hook_content = hook_content.replace("{{INSTALLER}}", "setup_githooks.py")
    
    # Write hook
    with open(hook_path, 'w') as f:
        f.write(hook_content)
    
    # Make executable
    hook_path.chmod(0o755)

def check_python():
    """Check Python installation."""
    python_cmd = None
    
    # Check python3
    try:
        result = subprocess.run(["python3", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            python_cmd = "python3"
            print_color(f"   ✅ Python3 found: {result.stdout.strip()}", Colors.GREEN)
    except FileNotFoundError:
        pass
    
    # Check python if python3 not found
    if not python_cmd:
        try:
            result = subprocess.run(["python", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                python_cmd = "python"
                print_color(f"   ✅ Python found: {result.stdout.strip()}", Colors.GREEN)
        except FileNotFoundError:
            pass
    
    if not python_cmd:
        print_color("   ❌ Python not found! Please install Python 3", Colors.RED)
        print("   The git hooks require Python to run")
        
    return python_cmd

def check_git_config():
    """Check and set git configuration."""
    # Check user.name
    result = subprocess.run(["git", "config", "user.name"], 
                          capture_output=True, text=True)
    if not result.stdout.strip():
        print_color("   No git user.name set", Colors.YELLOW)
        name = input("   Enter your name: ")
        subprocess.run(["git", "config", "user.name", name])
    else:
        print_color(f"   ✅ Git user: {result.stdout.strip()}", Colors.GREEN)
    
    # Check user.email
    result = subprocess.run(["git", "config", "user.email"], 
                          capture_output=True, text=True)
    if not result.stdout.strip():
        print_color("   No git user.email set", Colors.YELLOW)
        email = input("   Enter your email: ")
        subprocess.run(["git", "config", "user.email", email])
    else:
        print_color(f"   ✅ Git email: {result.stdout.strip()}", Colors.GREEN)

def install_dependencies():
    """Install Python dependencies if requirements.txt exists in the project."""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print_color("📦 No requirements.txt found in project", Colors.YELLOW)
        return
    
    print_color("📦 Project has requirements.txt", Colors.GREEN)
    
    # Check if pip is available
    pip_cmd = None
    for cmd in ["pip3", "pip"]:
        if shutil.which(cmd):
            pip_cmd = cmd
            break
    
    if not pip_cmd:
        print_color("   ⚠️  pip not found!", Colors.YELLOW)
        print("   Please install pip to manage Python dependencies")
        return
    
    print("   To install project dependencies:")
    print(f"     {pip_cmd} install -r requirements.txt")
    print()
    print("   Or better, use a virtual environment:")
    print("     python3 -m venv .venv")
    if sys.platform == "win32":
        print("     .venv\\Scripts\\activate")
    else:
        print("     source .venv/bin/activate")
    print(f"     {pip_cmd} install -r requirements.txt")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description=f"Git Hooks Setup Script v{INSTALLER_VERSION}\n"
                    f"Install and manage git hooks for this repository.",
        epilog=f"For updates and help, visit: {INSTALLER_URL}\n"
               f"Report issues at: {INSTALLER_ISSUES}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {INSTALLER_VERSION}'
    )
    
    parser.add_argument(
        '--template-dir',
        type=Path,
        help='Directory containing hook templates (default: auto-detect)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check hook status without installing/updating'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update hooks without asking'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show project information and exit'
    )
    
    args = parser.parse_args()
    
    # Handle --info flag
    if args.info:
        print_color(f"Git Hooks Installer v{INSTALLER_VERSION}", Colors.GREEN)
        print(f"Project URL: {INSTALLER_URL}")
        print(f"Report issues: {INSTALLER_ISSUES}")
        print()
        print("This tool helps developers set up git hooks for:")
        print("  - Automatic commit logging")
        print("  - Git timeline generation")
        print("  - README updates")
        print("  - Commit message formatting")
        return 0

    print_color(f"=== Git Hooks Setup Script v{INSTALLER_VERSION} ===", Colors.GREEN)
    print("This script will install git hooks for this repository")
    print()
    
    # Track what was actually done
    hook_installed = False
    hook_updated = False
    hook_kept_existing = False
    
    # Check if in git repo
    if not check_git_repo():
        print_color("❌ Error: Not in a git repository", Colors.RED)
        print("Please run this script from the repository root")
        return 1
    
    # Get repo root
    repo_root = get_repo_root()
    if not repo_root:
        print_color("❌ Error: Could not determine repository root", Colors.RED)
        return 1
    
    # Change to repo root
    os.chdir(repo_root)
    print_color(f"📍 Repository root: {repo_root}", Colors.YELLOW)
    
    # Check if scripts exist
    scripts_dir = repo_root / "scripts" / "post-commit"
    if not scripts_dir.exists():
        print_color("❌ Error: scripts/post-commit directory not found", Colors.RED)
        print("This repository may not have git hooks set up yet")
        return 1
    
    # Create hooks directory
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for hook template
    if args.template_dir:
        # User specified template directory
        template_paths = [args.template_dir / "post-commit"]
    else:
        # Auto-detect template locations
        template_paths = [
            repo_root / "developer-setup" / "templates" / "post-commit",
            repo_root / "templates" / "post-commit",
            repo_root / "scripts" / "git-hooks" / "post-commit",
        ]
    
    template_path = None
    for path in template_paths:
        if path.exists():
            template_path = path
            break
    
    if not template_path:
        print_color("❌ Error: No hook template found", Colors.RED)
        print("Looked in:")
        for path in template_paths:
            print(f"  - {path}")
        return 1
    
    # Check existing hook
    hook_path = hooks_dir / "post-commit"
    hook_status = check_hook_version(hook_path)
    
    if hook_status == 0:
        print_color(f"✅ Git hooks already installed and up-to-date (v{INSTALLER_VERSION})", 
                   Colors.GREEN)
        hook_kept_existing = True
    elif hook_status == 1:
        print_color("⚠️  Git hooks exist but are a different version", Colors.YELLOW)
        print("   Your hook might have custom modifications or be outdated")
        if args.force:
            response = 'y'
        else:
            response = input(f"   Replace with standard hook v{INSTALLER_VERSION}? (y/N) ")

        if response.lower() == 'y':
            install_hook_from_template(template_path, hook_path)
            print_color(f"✅ Updated post-commit hook to v{INSTALLER_VERSION}", Colors.GREEN)
            hook_updated = True
        else:
            print("Keeping existing hook")
            hook_kept_existing = True
    else:
        print_color(f"📝 Installing post-commit hook v{INSTALLER_VERSION}...", Colors.YELLOW)
        install_hook_from_template(template_path, hook_path)
        print_color("✅ Installed post-commit hook", Colors.GREEN)
        hook_installed = True
    
    # Check other hooks
    print_color("🔍 Checking for other hooks...", Colors.GREEN)
    for hook_name in ["pre-commit", "prepare-commit-msg", "commit-msg", "pre-push"]:
        if (hooks_dir / hook_name).exists():
            print(f"   ✅ Found {hook_name} hook")
        else:
            print(f"   ⏭️  No {hook_name} hook")
    
    # Set up git config
    print_color("⚙️  Setting up git config...", Colors.GREEN)
    check_git_config()
    
    # Check Python
    print_color("🐍 Checking Python installation...", Colors.GREEN)
    check_python()
    
    # Check for project dependencies
    install_dependencies()
    
    # Final summary
    print()
    print_color("=== Setup Complete ===", Colors.GREEN)
    print()
    
    # Show appropriate message based on what happened
    if hook_installed:
        print("Git hooks have been installed. They will:")
    elif hook_updated:
        print("Git hooks have been updated. They will:")
    elif hook_kept_existing:
        print("Existing git hooks were kept. They should:")
    else:
        print("Git hooks are configured. They will:")
    
    print("  📝 Create commit logs in docs/commit-logs/")
    print("  📊 Generate git timeline reports")
    print("  🔄 Update README with latest commits")
    print("  🔒 Prevent recursive commits with lock files")
    print()
    
    if hook_kept_existing and hook_status == 1:
        print_color("⚠️  Note: Your hooks may be a different version than expected", Colors.YELLOW)
        print(f"   Run with 'y' to update to v{INSTALLER_VERSION} if you experience issues")
        print()
    
    print("Environment variables:")
    print("  GIT_AUTO_PUSH=true  - Enable automatic push after commits")
    print()
    print("To test the hooks, make a commit:")
    print("  git add .")
    print('  git commit -m "test: Testing git hooks"')
    print()
    print_color(f"Note: This is setup_githooks v{INSTALLER_VERSION}", Colors.YELLOW)
    print_color(f"Version: {INSTALLER_VERSION}", Colors.YELLOW)
    print_color(f"Updates: {INSTALLER_URL}", Colors.YELLOW)
    print_color(f"Issues:  {INSTALLER_ISSUES}", Colors.YELLOW)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())