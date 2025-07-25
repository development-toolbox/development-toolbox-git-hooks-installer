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
    
    # Detect template directory robustly
    script_dir = Path(__file__).resolve().parent
    candidate_dirs = []

    if args.template_dir:
        candidate_dirs.append(args.template_dir)
    # 1. developer-setup/templates relative to script location
    candidate_dirs.append(script_dir / "templates")
    # 2. developer-setup/templates relative to repo root
    candidate_dirs.append(repo_root / "developer-setup" / "templates")
    # 3. templates at repo root
    candidate_dirs.append(repo_root / "templates")
    # 4. scripts/git-hooks at repo root
    candidate_dirs.append(repo_root / "scripts" / "git-hooks")

    template_dir = None
    checked_dirs = []
    for d in candidate_dirs:
        checked_dirs.append(str(d))
        if d.exists() and d.is_dir():
            template_dir = d
            break

    if not template_dir:
        print_color("❌ Error: No hook template directory found", Colors.RED)
        print("Looked in:")
        for d in checked_dirs:
            print(f"  - {d}")
        print_color("Please ensure your template directory exists in one of the above locations or specify with --template-dir.", Colors.YELLOW)
        return 1

    # Copy all hook templates from the found directory
    hook_templates = list(template_dir.glob("*"))
    if not hook_templates:
        print_color(f"❌ Error: No hook templates found in {template_dir}", Colors.RED)
        return 1

    if args.check_only:
        # DRY-RUN: No changes will be made below this line!
        print_color("🔍 --check-only: Dry-run, showing what would happen (no changes will be made)", Colors.YELLOW)
        # Hooks
        for template_path in hook_templates:
            hook_name = template_path.name
            hook_path = hooks_dir / hook_name
            status = check_hook_version(hook_path)
            if status == 0:
                print_color(f"✅ {hook_name} is up-to-date (v{INSTALLER_VERSION}) - would keep", Colors.GREEN)
            elif status == 1:
                print_color(f"⚠️  {hook_name} exists but is a different version - would update", Colors.YELLOW)
            else:
                print_color(f"❌ {hook_name} is not installed - would install", Colors.RED)
        # Git config
        print_color("⚙️  Checking git config...", Colors.GREEN)
        # Simulate git user.name
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if not result.stdout.strip():
            print_color("   No git user.name set - would prompt to set", Colors.YELLOW)
        else:
            print_color(f"   ✅ Git user: {result.stdout.strip()} (would keep)", Colors.GREEN)
        # Simulate git user.email
        result = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
        if not result.stdout.strip():
            print_color("   No git user.email set - would prompt to set", Colors.YELLOW)
        else:
            print_color(f"   ✅ Git email: {result.stdout.strip()} (would keep)", Colors.GREEN)
        # Python
        print_color("🐍 Checking Python installation...", Colors.GREEN)
        python_found = False
        for cmd in ["python3", "python"]:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print_color(f"   ✅ {cmd} found: {result.stdout.strip()} (would use)", Colors.GREEN)
                    python_found = True
                    break
            except FileNotFoundError:
                continue
        if not python_found:
            print_color("   ❌ Python not found! Would prompt to install Python 3", Colors.RED)
        # Dependencies
        req_file = repo_root / "requirements.txt"
        if not req_file.exists():
            print_color("📦 No requirements.txt found in project (would skip dependency install)", Colors.YELLOW)
        else:
            print_color("📦 Project has requirements.txt (would prompt to install dependencies)", Colors.GREEN)
        # Final summary
        print()
        print_color("=== Check-Only Mode Complete ===", Colors.GREEN)
        print()
        print_color("No changes were made. This was a dry-run (--check-only).", Colors.YELLOW)
        print("To actually install or update hooks, run this script without --check-only.")
        print()
        return 0
    else:
        hook_status = None  # Track hook status for later use
        for template_path in hook_templates:
            hook_name = template_path.name
            hook_path = hooks_dir / hook_name
            # Check current hook version before installing
            current_status = check_hook_version(hook_path)
            if current_status == 2:
                hook_installed = True
            elif current_status == 1:
                hook_updated = True
            elif current_status == 0:
                hook_kept_existing = True
            hook_status = current_status  # Save last status for summary
            install_hook_from_template(template_path, hook_path)
            print_color(f"✅ Installed {hook_name} hook from template", Colors.GREEN)
    
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