#!/usr/bin/env python3
# githooks-utils.py
from pathlib import Path
import sys
import subprocess
import os


def run_git_command(command):
    """Run a git command and return the output as lines."""
    # Validate that command starts with 'git'
    if not command or command[0] != "git":
        print("❌ ERROR: Only git commands are allowed")
        sys.exit(1)
    
    # Add timeout to prevent hanging
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True,
            timeout=30,  # 30 second timeout
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable git prompts
        )
    except subprocess.TimeoutExpired:
        print(f"❌ Git command timed out: {' '.join(command)}")
        sys.exit(1)
    
    if result.returncode != 0:
        # Sanitize error output to prevent information disclosure
        sanitized_error = result.stderr[:500] if result.stderr else "Unknown error"
        print(f"❌ Git command failed: {' '.join(command)}")
        sys.exit(1)
    return result.stdout.strip().splitlines()


def get_repo_root():
    """Get the root of the current git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            capture_output=True, 
            text=True,
            timeout=10,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
        if result.returncode != 0:
            print("❌ ERROR: Not in a git repository")
            sys.exit(1)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Git command timed out")
        sys.exit(1)


def assert_inside_repo(path: Path, repo_root: Path, description: str = "path"):
    """Ensure that a path is inside the given repository root."""
    try:
        path_resolved = path.resolve()
        repo_resolved = repo_root.resolve()
        if not path_resolved.is_relative_to(repo_resolved):
            print(f"❌ ERROR: {description} ({path_resolved}) is outside repository root ({repo_resolved})")
            sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR while verifying path containment: {e}")
        sys.exit(1)


def get_repo_url():
    """Automatically detect the GitHub repository URL."""
    remote_urls = run_git_command(["git", "remote", "get-url", "origin"])
    if not remote_urls:
        return ""  # No remote configured
    
    remote_url = remote_urls[0]
    
    # Validate URL format to prevent injection
    import re
    if not re.match(r'^(https?://|git@)[\w.-]+(/|:)[\w.-]+/[\w.-]+(\.git)?$', remote_url):
        return ""  # Invalid URL format
    
    if remote_url.startswith("git@"):  # Convert SSH to HTTPS
        return remote_url.replace(":", "/").replace("git@", "https://").replace(".git", "")
    return remote_url.replace(".git", "")


def get_branches():
    """Fetch all branches with latest commit."""
    return run_git_command([
        "git", "branch", "--all", "--format=%(refname:short) | %(objectname:short) | %(authorname)"
    ])


def get_tags():
    """Fetch all tags with commit hash and messages."""
    return run_git_command([
        "git", "tag", "--sort=-taggerdate",
        "--format=%(refname:short) | %(objectname:short) | %(taggerdate)"
    ])


def get_pull_requests():
    """Simulating PR fetching. Real PRs require GitHub API integration."""
    return run_git_command([
        "git", "log", "--grep=Merge pull request",
        "--pretty=format:%h | %s | %ad", "--date=iso"
    ])


def get_commits():
    """Fetch the latest commits with exact date and time."""
    return run_git_command([
        "git", "log", "--all",
        "--pretty=format:%h | %s | %an | %ad", "--date=iso"
    ])
