# Git Hooks Installer

A security-hardened, automated git hooks installer that streamlines commit documentation and maintains code quality standards across development teams.

## Overview

The Git Hooks Installer automates the installation of post-commit hooks that generate detailed commit logs, timelines, and documentation following Conventional Commits standards. It features a secure, PR-only workflow with automatic pull request creation and comprehensive safety validations.

## Key Features

### 🔒 Security First
- **Command injection prevention** with validated git operations
- **Path traversal protection** with realpath validation  
- **Resource exhaustion safeguards** (1000 files, 100MB limits)
- **Atomic operations** with file locking to prevent race conditions

### 🚀 Developer Experience
- **Preserves workflow** - returns to your original branch after installation
- **Automatic PR creation** using GitHub token or gh CLI
- **Interactive setup** guides for missing authentication
- **No disruption** - works in background on feature branches

### 📝 Documentation Automation
- **Automated commit logs** generated after each commit
- **Timeline reports** tracking development progress
- **Conventional commits** support for standardized messaging
- **Cross-platform compatibility** with Linux, macOS, and Windows

## Quick Start

```bash
# Basic installation
python git-hooks-installer/git-hooks-installer.py /path/to/your/repo

# With automatic PR creation (GitHub CLI)
gh auth login
python git-hooks-installer/git-hooks-installer.py /path/to/your/repo

# Check installation status
python git-hooks-installer/git-hooks-installer.py -c
```

## What It Does

1. **Validates** your repository state for safety
2. **Creates** a feature branch for the installation  
3. **Installs** git hooks, scripts, and documentation
4. **Commits** only installer-created files (never your work)
5. **Creates** a pull request automatically (if authenticated)
6. **Returns** you to your original branch

## Documentation

### Getting Started
- [Installation Guide](getting-started/installation.md) - Complete setup instructions
- [Quick Start](getting-started/quick-start.md) - 5-minute setup
- [Requirements](getting-started/requirements.md) - System dependencies

### Guides  
- [Authentication Setup](guides/authentication.md) - GitHub token and CLI configuration
- [Troubleshooting](guides/troubleshooting.md) - Common issues and solutions
- [Security Guide](guides/security-guide.md) - Security best practices

### Reference
- [CLI Options](reference/cli-options.md) - Complete command reference
- [Configuration](reference/configuration.md) - All configuration options
- [API Reference](reference/api.md) - Internal API documentation

### Development
- [Architecture](development/architecture.md) - Technical implementation
- [Contributing](development/contributing.md) - How to contribute
- [Changelog](development/changelog.md) - Version history

## Current Version

**v1.2.0** - Enhanced with automatic PR creation, intelligent GitHub authentication, and improved developer workflow

## Requirements

- Python 3.12+ (recommended, works with 3.9+)
- Git repository
- For automatic PR creation: GitHub token or gh CLI

## Security Guarantees

✅ Repository state validated before installation  
✅ Only installer-created files committed  
✅ No user secrets or work-in-progress included  
✅ Manual review required via pull request  
✅ No direct commits to main/protected branches  

## Support

For issues, questions, or contributions:
- Check [Troubleshooting Guide](guides/troubleshooting.md)
- Review [Common Issues](guides/troubleshooting.md#common-issues)
- Open an issue in the project repository

---

*Git Hooks Installer v1.2.0 - Secure, automated, professional*