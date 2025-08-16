# Installation Guide

Complete step-by-step instructions for installing the Git Hooks Installer in your repository.

## Prerequisites

Before installing, ensure you have:

- **Python 3.9+** (Python 3.12+ recommended)
- **Git repository** (local repository with remote origin)
- **Write access** to the target repository
- **Clean working tree** (no uncommitted changes)

## Installation Methods

### Method 1: Basic Installation

The simplest way to install git hooks without automatic PR creation:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Run the installer
python /path/to/git-hooks-installer/git-hooks-installer.py .
```

### Method 2: With GitHub Authentication (Recommended)

For automatic PR creation, set up GitHub authentication first:

#### Option A: GitHub Token
```bash
# Set up your GitHub token
export GITHUB_TOKEN=your_personal_access_token

# Run installer
python /path/to/git-hooks-installer/git-hooks-installer.py .
```

#### Option B: GitHub CLI
```bash
# Authenticate with GitHub CLI
gh auth login

# Run installer  
python /path/to/git-hooks-installer/git-hooks-installer.py .
```

### Method 3: Interactive Setup

Let the installer guide you through authentication setup:

```bash
# Run installer without pre-configured auth
python /path/to/git-hooks-installer/git-hooks-installer.py .

# Choose from interactive menu:
# 1. Set up GitHub token (saves to .env file)
# 2. Install and configure gh CLI
# 3. Skip automatic PR creation
```

## Installation Process

When you run the installer, it performs these steps:

### 1. Pre-flight Safety Checks
- Validates repository is a valid Git repository
- Checks for uncommitted changes
- Verifies no sensitive files would be overwritten
- Confirms repository has a remote origin

### 2. Branch Management
- Records your current branch (e.g., `main`, `development`)
- Creates a new feature branch: `feat/githooks-installation-YYYYMMDD-HHMMSS`
- Switches to the feature branch for installation

### 3. File Installation
- Installs post-commit hooks to `.git/hooks/`
- Copies scripts to `scripts/post-commit/`
- Adds documentation to `docs/githooks/`
- Creates developer setup tools in `developer-setup/`
- Generates shell wrapper scripts (`setup-githooks.sh`, `setup-githooks.ps1`)

### 4. Secure Tracking
- Uses FileTracker to record only installer-created files
- Excludes `__pycache__`, `.pyc`, and hidden files
- Validates no user files or secrets are included

### 5. Commit and Push
- Commits tracked files with detailed message
- Pushes feature branch to origin remote

### 6. Pull Request Creation (if authenticated)
- Creates pull request using GitHub API or gh CLI
- Includes detailed description of changes
- Provides link to the created PR

### 7. Branch Restoration
- Switches back to your original branch
- Leaves you exactly where you started

## Command Line Options

### Basic Options

```bash
# Check current installation status
python git-hooks-installer.py -c

# Force reinstall even if up-to-date
python git-hooks-installer.py -f

# Verbose output
python git-hooks-installer.py -v

# Debug output
python git-hooks-installer.py -d

# Skip CI/CD file installation
python git-hooks-installer.py --no-ci
```

### Target Repository

```bash
# Install in current directory
python git-hooks-installer.py .

# Install in specific directory
python git-hooks-installer.py /path/to/target/repo

# Install in parent directory
python git-hooks-installer.py ../other-project
```

## Verification

After installation, verify everything is working:

### 1. Check Installation Status
```bash
python git-hooks-installer.py -c
```

Expected output:
```
✅ Post-commit hook: INSTALLED
✅ Scripts directory: INSTALLED  
✅ Developer setup: INSTALLED
✅ Shell wrapper (sh): INSTALLED
✅ PowerShell wrapper (ps1): INSTALLED
🎉 Git hooks installation: COMPLETE
```

### 2. Test Post-commit Hook
```bash
# Make a test commit
echo "test" > test-file.txt
git add test-file.txt
git commit -m "test: verify git hooks installation"

# Check if documentation was generated
ls docs/commit-logs/$(git branch --show-current)/
```

### 3. Verify Branch Restoration
```bash
# Confirm you're back on your original branch
git branch --show-current
```

## Installed Files

The installer creates these files in your repository:

### Git Hooks
- `.git/hooks/post-commit` - Main hook that triggers documentation

### Scripts
- `scripts/post-commit/generate_git_timeline.py` - Timeline generation
- `scripts/post-commit/githooks_utils.py` - Utility functions
- `scripts/post-commit/commit-mess` - Commit message processing
- `scripts/post-commit/update-readme.sh` - README updates

### Documentation
- `docs/githooks/` - Examples and guides for the git hooks system

### Developer Setup
- `developer-setup/` - Tools for manual setup by other developers
- `setup-githooks.sh` - Linux/macOS setup script
- `setup-githooks.ps1` - Windows PowerShell setup script

## Next Steps

After successful installation:

1. **Review the Pull Request** - Check the automatically created PR
2. **Merge After Approval** - Have a team member review and merge
3. **Test Functionality** - Make commits to verify hooks work
4. **Share with Team** - Inform team members about the new git hooks

## Troubleshooting

If you encounter issues, see the [Troubleshooting Guide](../guides/troubleshooting.md) for common problems and solutions.

Common issues:
- [Repository has uncommitted changes](../guides/troubleshooting.md#uncommitted-changes)
- [Permission denied errors](../guides/troubleshooting.md#permission-errors)
- [GitHub authentication failed](../guides/troubleshooting.md#github-auth-failed)
- [Python version compatibility](../guides/troubleshooting.md#python-version)