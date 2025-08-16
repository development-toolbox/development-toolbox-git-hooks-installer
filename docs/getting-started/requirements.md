# System Requirements

Complete requirements for running the Git Hooks Installer.

## Minimum Requirements

### Operating System
- **Linux** - Any modern distribution (Ubuntu 18.04+, CentOS 7+, AlmaLinux 9+)
- **macOS** - 10.14+ (Mojave or later)
- **Windows** - Windows 10+ or Windows Server 2019+

### Python
- **Minimum**: Python 3.9+
- **Recommended**: Python 3.12+
- **Modules**: Standard library only (no additional pip packages required)

### Git
- **Minimum**: Git 2.20+
- **Recommended**: Git 2.30+
- **Repository**: Must be a valid Git repository with remote origin

### Hardware
- **RAM**: 512MB available memory
- **Storage**: 50MB free disk space for installation
- **CPU**: Any modern processor (minimal CPU usage)

## Software Dependencies

### Required
- **Python 3.9+** - Core interpreter
- **Git** - Version control system
- **Shell** - bash/zsh (Linux/macOS) or PowerShell (Windows)

### Optional (for enhanced features)
- **GitHub CLI (gh)** - For automatic PR creation
- **curl** - For GitHub API calls (usually pre-installed)
- **jq** - For JSON processing (recommended but not required)

## Repository Requirements

### Git Repository State
- Must be a **valid Git repository** (`.git` directory present)
- Must have **remote origin** configured
- **Clean working tree** (no uncommitted changes)
- **Write permissions** to the repository

### Remote Repository
- **GitHub repository** (for automatic PR creation)
- **Push access** to create feature branches
- **Pull request permissions** (for team collaboration)

### Branch Protection (Recommended)
- **Protected main branch** (prevents direct commits)
- **Require PR reviews** (enforces team review process)
- **Status checks** (optional but recommended)

## Platform-Specific Requirements

### Linux
```bash
# Check Python version
python3 --version

# Check Git version  
git --version

# Install dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3 git curl

# Install dependencies (RHEL/CentOS/AlmaLinux)
sudo yum install python3 git curl
# or
sudo dnf install python3 git curl
```

### macOS
```bash
# Check Python version
python3 --version

# Check Git version
git --version

# Install via Homebrew (recommended)
brew install python git

# Install GitHub CLI (optional)
brew install gh
```

### Windows
```powershell
# Check Python version
python --version

# Check Git version
git --version

# Install via Chocolatey
choco install python git

# Install via winget
winget install Python.Python.3.12
winget install Git.Git

# Install GitHub CLI (optional)
winget install GitHub.cli
```

## Authentication Requirements

### For Automatic PR Creation

Choose one of these options:

#### GitHub Personal Access Token
- **Scope**: `repo` (full repository access)
- **Type**: Classic personal access token
- **Expiration**: Set according to your security policy
- **Storage**: Environment variable `GITHUB_TOKEN` or `GH_TOKEN`

#### GitHub CLI Authentication
- **Installation**: GitHub CLI (`gh`) installed and authenticated
- **Authentication**: `gh auth login` completed successfully
- **Permissions**: Same account permissions as token method

### Environment Variables
```bash
# Required for token-based authentication
export GITHUB_TOKEN=ghp_your_token_here

# Alternative token variable name
export GH_TOKEN=ghp_your_token_here

# Optional: Custom installation path
export GITHOOKS_INSTALLER_PATH=/custom/path
```

## Network Requirements

### Internet Access
- **GitHub API**: `api.github.com` (port 443)
- **GitHub Git**: `github.com` (port 22 for SSH, 443 for HTTPS)
- **Optional**: Package repositories for dependency installation

### Firewall Configuration
```bash
# Required outbound connections
# HTTPS to GitHub API
443/tcp -> api.github.com

# SSH to GitHub (if using SSH remotes)
22/tcp -> github.com

# HTTPS to GitHub (if using HTTPS remotes)  
443/tcp -> github.com
```

### Proxy Configuration
If behind a corporate proxy:

```bash
# Set proxy for Git
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# Set proxy for Python requests
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080

# Set proxy for GitHub CLI
gh config set http_proxy http://proxy.company.com:8080
```

## Performance Requirements

### Resource Usage
- **CPU**: Minimal usage during installation (<5% for 1-2 minutes)
- **Memory**: ~50MB RAM during installation
- **Disk I/O**: Minimal (copying small text files)
- **Network**: ~1MB download for authentication and API calls

### Scalability Limits
- **File limit**: 1000 files per installation (safety limit)
- **Size limit**: 100MB total installation size (safety limit)
- **Timeout**: 30 seconds per Git operation (safety limit)

## Security Requirements

### File System Permissions
- **Read access**: Source installer directory
- **Write access**: Target repository directory
- **Execute access**: Python interpreter and Git binary

### Repository Security
- **No secrets**: Repository should not contain hardcoded secrets
- **Clean history**: No sensitive data in Git history
- **Access control**: Proper GitHub repository permissions

## Validation Script

Use this script to verify your system meets all requirements:

```bash
#!/bin/bash
echo "Git Hooks Installer - Requirements Check"
echo "========================================"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python: Not found"
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    echo "✅ Git: $GIT_VERSION"
else
    echo "❌ Git: Not found"
fi

# Check GitHub CLI (optional)
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -1 | cut -d' ' -f3)
    echo "✅ GitHub CLI: $GH_VERSION"
else
    echo "⚠️ GitHub CLI: Not found (optional)"
fi

# Check Git repository
if git rev-parse --git-dir &> /dev/null; then
    echo "✅ Git repository: Valid"
else
    echo "❌ Git repository: Not found"
fi

# Check remote origin
if git remote get-url origin &> /dev/null; then
    ORIGIN=$(git remote get-url origin)
    echo "✅ Remote origin: $ORIGIN"
else
    echo "❌ Remote origin: Not configured"
fi

# Check GitHub authentication
if [ -n "$GITHUB_TOKEN" ] || [ -n "$GH_TOKEN" ]; then
    echo "✅ GitHub token: Set"
elif gh auth status &> /dev/null; then
    echo "✅ GitHub CLI: Authenticated"
else
    echo "⚠️ GitHub auth: Not configured (manual PR creation required)"
fi

echo "========================================"
echo "Requirements check complete"
```

Save as `check-requirements.sh`, make executable with `chmod +x check-requirements.sh`, and run with `./check-requirements.sh`.