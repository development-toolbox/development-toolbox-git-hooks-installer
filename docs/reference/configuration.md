# Configuration Reference

Complete configuration options and settings for the Git Hooks Installer.

## Configuration Overview

The Git Hooks Installer supports configuration through multiple methods:
- Environment variables
- Configuration files (.env)
- Command-line options
- Git configuration

Configuration is processed in order of precedence (highest to lowest):
1. Command-line options
2. Environment variables
3. .env files
4. Git configuration
5. Default values

## Environment Variables

### Authentication Configuration

#### GITHUB_TOKEN
**Type:** String  
**Required:** No (but recommended for automatic PR creation)  
**Format:** `ghp_` followed by 36 alphanumeric characters  
**Description:** GitHub Personal Access Token for API authentication

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Token Requirements:**
- **Scope:** `repo` (Full control of private repositories)
- **Expiration:** Set according to security policy (30-90 days recommended)
- **Permissions:** Write access to target repository

#### GH_TOKEN
**Type:** String  
**Required:** No  
**Description:** Alternative environment variable name for GitHub token  
**Priority:** Lower than GITHUB_TOKEN

```bash
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Installation Configuration

#### GITHOOKS_INSTALLER_VERSION
**Type:** String  
**Default:** Auto-detected from installer  
**Description:** Override version detection for the installer

```bash
export GITHOOKS_INSTALLER_VERSION=1.2.0
```

#### GITHOOKS_INSTALLER_SOURCE
**Type:** Path  
**Default:** Auto-detected from script location  
**Description:** Custom path to installer source directory

```bash
export GITHOOKS_INSTALLER_SOURCE=/custom/path/to/installer
```

#### GITHOOKS_BRANCH_PREFIX
**Type:** String  
**Default:** `feat/githooks-installation`  
**Description:** Prefix for generated feature branch names

```bash
export GITHOOKS_BRANCH_PREFIX=feature/install-hooks
# Results in: feature/install-hooks-20240816-123456
```

### Network Configuration

#### HTTP_PROXY / HTTPS_PROXY
**Type:** URL  
**Required:** No  
**Description:** Proxy server for HTTP/HTTPS requests

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
```

#### NO_PROXY
**Type:** Comma-separated list  
**Required:** No  
**Description:** Hosts that should bypass proxy

```bash
export NO_PROXY=localhost,127.0.0.1,github.com
```

### Security Configuration

#### GITHOOKS_STRICT_MODE
**Type:** Boolean (0/1, true/false, yes/no)  
**Default:** true  
**Description:** Enable strict security validation

```bash
export GITHOOKS_STRICT_MODE=true
```

**When enabled:**
- Enhanced input validation
- Stricter file permission checks
- Additional security logging
- Mandatory .gitignore validation

#### GITHOOKS_MAX_FILES
**Type:** Integer  
**Default:** 1000  
**Description:** Maximum number of files that can be tracked

```bash
export GITHOOKS_MAX_FILES=500
```

#### GITHOOKS_MAX_SIZE
**Type:** Integer (bytes)  
**Default:** 104857600 (100MB)  
**Description:** Maximum total size of tracked files

```bash
export GITHOOKS_MAX_SIZE=52428800  # 50MB
```

### Logging Configuration

#### GITHOOKS_LOG_LEVEL
**Type:** String  
**Values:** DEBUG, INFO, WARNING, ERROR, CRITICAL  
**Default:** INFO  
**Description:** Logging verbosity level

```bash
export GITHOOKS_LOG_LEVEL=DEBUG
```

#### GITHOOKS_LOG_FILE
**Type:** Path  
**Default:** None (logs to stdout/stderr)  
**Description:** File path for log output

```bash
export GITHOOKS_LOG_FILE=/var/log/git-hooks-installer.log
```

## Configuration Files

### .env File

The installer can read configuration from `.env` files in the target repository:

```bash
# .env file in target repository root
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHOOKS_STRICT_MODE=true
GITHOOKS_LOG_LEVEL=DEBUG
```

**Security Requirements:**
- Must be added to `.gitignore`
- Should have restricted permissions (600)
- Never commit to version control

**Automatic Creation:**
The installer can create `.env` files interactively:
1. Run installer without GITHUB_TOKEN set
2. Choose "1. Set up GitHub token" from menu
3. Paste token when prompted
4. Installer saves to `.env` automatically

### Git Configuration

#### Repository-specific Configuration

```bash
# Set in target repository
git config githooks.installer.version "1.2.0"
git config githooks.installer.branch-prefix "feature/hooks"
git config githooks.installer.strict-mode true
```

#### Global Configuration

```bash
# Set globally for all repositories
git config --global githooks.installer.default-mode strict
git config --global githooks.installer.log-level info
```

#### Proxy Configuration

```bash
# HTTP proxy for Git operations
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# HTTPS-specific proxy
git config --global https.proxy https://secure-proxy.company.com:8443
```

## Runtime Configuration

### FileTracker Configuration

The FileTracker class can be configured through environment variables:

```bash
# Maximum tracked files
export GITHOOKS_MAX_FILES=2000

# Maximum file size (10MB)
export GITHOOKS_MAX_FILE_SIZE=10485760

# Maximum total size (200MB)
export GITHOOKS_MAX_TOTAL_SIZE=209715200

# Lock timeout in seconds
export GITHOOKS_LOCK_TIMEOUT=60
```

### SecureGitWrapper Configuration

```bash
# Git operation timeout (seconds)
export GITHOOKS_GIT_TIMEOUT=30

# Enable command logging
export GITHOOKS_LOG_GIT_COMMANDS=true

# Strict argument validation
export GITHOOKS_STRICT_GIT_ARGS=true
```

### Repository Validator Configuration

```bash
# Sensitive file patterns (comma-separated)
export GITHOOKS_SENSITIVE_PATTERNS="*.key,*.pem,*.p12,secrets.yml"

# Maximum repository size for validation (bytes)
export GITHOOKS_MAX_REPO_SIZE=1073741824  # 1GB

# Skip validation for specific paths
export GITHOOKS_SKIP_VALIDATION="node_modules,build,dist"
```

## GitHub API Configuration

### API Settings

```bash
# GitHub API base URL (for GitHub Enterprise)
export GITHUB_API_URL=https://api.github.company.com

# API timeout in seconds
export GITHUB_API_TIMEOUT=30

# Rate limit buffer (requests to reserve)
export GITHUB_RATE_LIMIT_BUFFER=100
```

### Pull Request Configuration

```bash
# Default PR title template
export GITHOOKS_PR_TITLE="feat: Install git hooks for automated documentation"

# PR body template file
export GITHOOKS_PR_TEMPLATE=/path/to/pr-template.md

# Auto-assign reviewers (comma-separated usernames)
export GITHOOKS_PR_REVIEWERS="team-lead,senior-dev"

# Add labels to PR (comma-separated)
export GITHOOKS_PR_LABELS="automation,git-hooks,documentation"
```

## Platform-Specific Configuration

### Linux/macOS Configuration

```bash
# Use system keyring for token storage
export GITHOOKS_USE_KEYRING=true

# System-specific Python path
export GITHOOKS_PYTHON_PATH=/usr/bin/python3.12

# Preferred shell for scripts
export GITHOOKS_SHELL=/bin/bash
```

### Windows Configuration

```powershell
# Use Windows Credential Manager
$env:GITHOOKS_USE_CREDENTIAL_MANAGER = "true"

# PowerShell execution policy override
$env:GITHOOKS_PS_EXECUTION_POLICY = "RemoteSigned"

# Windows-specific paths
$env:GITHOOKS_PYTHON_PATH = "C:\Python312\python.exe"
```

## Configuration Validation

### Validation Script

Use this script to validate your configuration:

```bash
#!/bin/bash
# validate-config.sh

echo "Git Hooks Installer - Configuration Validation"
echo "=============================================="

# Check authentication
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN: Set (length: ${#GITHUB_TOKEN})"
    if [[ $GITHUB_TOKEN =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
        echo "✅ GITHUB_TOKEN: Valid format"
    else
        echo "❌ GITHUB_TOKEN: Invalid format"
    fi
else
    echo "⚠️ GITHUB_TOKEN: Not set"
fi

# Check gh CLI
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    echo "✅ GitHub CLI: Authenticated"
else
    echo "⚠️ GitHub CLI: Not authenticated"
fi

# Check proxy settings
if [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
    echo "ℹ️ Proxy: Configured"
    echo "   HTTP_PROXY: ${HTTP_PROXY:-not set}"
    echo "   HTTPS_PROXY: ${HTTPS_PROXY:-not set}"
fi

# Check resource limits
echo "📊 Resource Limits:"
echo "   Max files: ${GITHOOKS_MAX_FILES:-1000 (default)}"
echo "   Max size: ${GITHOOKS_MAX_SIZE:-104857600 (default)} bytes"

# Check logging
echo "📝 Logging:"
echo "   Level: ${GITHOOKS_LOG_LEVEL:-INFO (default)}"
echo "   File: ${GITHOOKS_LOG_FILE:-stdout/stderr (default)}"

echo "=============================================="
echo "Configuration validation complete"
```

### Common Configuration Issues

#### Token Format Validation
```bash
# Valid token format
if [[ $GITHUB_TOKEN =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
    echo "Token format is valid"
else
    echo "Invalid token format"
fi
```

#### Path Validation
```bash
# Validate installer source path
if [ -d "$GITHOOKS_INSTALLER_SOURCE" ] && [ -f "$GITHOOKS_INSTALLER_SOURCE/git-hooks-installer.py" ]; then
    echo "Installer source path is valid"
else
    echo "Invalid installer source path"
fi
```

#### Network Connectivity
```bash
# Test GitHub API connectivity
if curl -s -f https://api.github.com/zen > /dev/null; then
    echo "GitHub API accessible"
else
    echo "Cannot reach GitHub API"
fi
```

## Configuration Examples

### Development Environment

```bash
# .env file for development
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHOOKS_LOG_LEVEL=DEBUG
GITHOOKS_STRICT_MODE=false
GITHOOKS_MAX_FILES=500
```

### Production Environment

```bash
# Production configuration
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export GITHOOKS_LOG_LEVEL=INFO
export GITHOOKS_STRICT_MODE=true
export GITHOOKS_LOG_FILE=/var/log/git-hooks-installer.log
export GITHOOKS_MAX_FILES=1000
export GITHOOKS_MAX_SIZE=104857600
```

### Corporate Environment

```bash
# Corporate proxy and security settings
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com
export GITHOOKS_STRICT_MODE=true
export GITHUB_API_URL=https://github.company.com/api/v3
```

### CI/CD Environment

```yaml
# GitHub Actions configuration
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  GITHOOKS_LOG_LEVEL: INFO
  GITHOOKS_STRICT_MODE: true
  GITHOOKS_MAX_FILES: 2000
```

## Configuration Troubleshooting

### Debug Configuration Loading

```bash
# Enable debug logging to see configuration loading
export GITHOOKS_LOG_LEVEL=DEBUG
python git-hooks-installer.py --debug .
```

### Configuration Override Testing

```bash
# Test configuration precedence
export GITHOOKS_LOG_LEVEL=ERROR
python git-hooks-installer.py --debug .
# --debug should override GITHOOKS_LOG_LEVEL
```

### Validate All Settings

```bash
# Dump all configuration (remove sensitive info)
env | grep GITHOOKS | sed 's/TOKEN=.*/TOKEN=***REDACTED***/'
git config --list | grep githooks
```

This configuration reference provides comprehensive control over all aspects of the Git Hooks Installer behavior.