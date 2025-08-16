# GitHub Authentication Guide

Complete guide to setting up GitHub authentication for automatic pull request creation.

## Overview

The Git Hooks Installer can automatically create pull requests when it has proper GitHub authentication. This guide covers all authentication methods and their setup.

## Authentication Methods

### Method 1: GitHub Personal Access Token (Recommended for CI/CD)

Personal Access Tokens are ideal for automated environments and CI/CD pipelines.

#### Creating a GitHub Token

1. **Navigate to GitHub Settings**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"

2. **Configure Token Settings**
   - **Note**: `Git Hooks Installer - [Repository Name]`
   - **Expiration**: Choose based on your security policy (30-90 days recommended)
   - **Scopes**: Select `repo` (Full control of private repositories)

3. **Generate and Save Token**
   - Click "Generate token"
   - **Important**: Copy the token immediately (you won't see it again)
   - Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### Using the Token

##### Option A: Environment Variable
```bash
# Set for current session
export GITHUB_TOKEN=ghp_your_token_here

# Add to shell profile for persistence
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
source ~/.bashrc
```

##### Option B: .env File (Interactive Setup)
The installer can save your token to a `.env` file:
1. Run the installer without setting `GITHUB_TOKEN`
2. Choose option "1. Set up GitHub token"
3. Paste your token when prompted
4. The installer saves it to `.env` automatically

```bash
# The installer creates/updates .env with:
GITHUB_TOKEN=ghp_your_token_here
```

⚠️ **Important**: Add `.env` to your `.gitignore` to prevent committing secrets!

### Method 2: GitHub CLI (Recommended for Local Development)

GitHub CLI provides a user-friendly authentication experience for local development.

#### Installing GitHub CLI

##### macOS
```bash
# Using Homebrew
brew install gh

# Using MacPorts
sudo port install gh
```

##### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install gh

# RHEL/CentOS/Fedora
sudo dnf install gh

# Arch Linux
sudo pacman -S github-cli

# Manual installation
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
```

##### Windows
```powershell
# Using winget
winget install GitHub.cli

# Using Chocolatey
choco install gh

# Using Scoop
scoop install gh
```

#### Authenticating with GitHub CLI

```bash
# Start authentication process
gh auth login

# Follow the interactive prompts:
# 1. What account do you want to log into? → GitHub.com
# 2. What is your preferred protocol? → HTTPS (or SSH if you prefer)
# 3. Authenticate Git with your GitHub credentials? → Yes
# 4. How would you like to authenticate? → Login with a web browser

# Verify authentication
gh auth status
```

Expected output:
```
github.com
  ✓ Logged in to github.com account username (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo'
```

### Method 3: Interactive Setup (Guided Configuration)

If you run the installer without authentication, it will guide you through setup:

```bash
# Run installer without pre-configured auth
python git-hooks-installer/git-hooks-installer.py /path/to/repo

# The installer detects missing auth and shows:
🔐 GitHub authentication is needed to create pull requests automatically

Choose an option:
  1. Set up GitHub token (recommended for CI/CD)
  2. Install and configure gh CLI (recommended for local development)  
  3. Skip automatic PR creation

Enter your choice (1/2/3):
```

#### Option 1: Token Setup
- Provides step-by-step instructions for creating a token
- Prompts you to paste the token
- Saves token to `.env` file in your repository
- Reminds you to add `.env` to `.gitignore`

#### Option 2: CLI Setup  
- Provides installation instructions for your platform
- Guides you through `gh auth login`
- Verifies authentication after setup

#### Option 3: Skip
- Continues installation without authentication
- Creates feature branch and commits files
- Provides manual PR creation link

## Authentication Priority

The installer checks authentication in this order:

1. **Environment Variables**: `GITHUB_TOKEN` or `GH_TOKEN`
2. **GitHub CLI**: `gh auth status` verification
3. **Interactive Setup**: Prompts user if neither is available

```bash
# Priority 1: Environment token
export GITHUB_TOKEN=ghp_xxx
python git-hooks-installer.py .  # Uses token

# Priority 2: GitHub CLI (if no token)
unset GITHUB_TOKEN
gh auth login
python git-hooks-installer.py .  # Uses gh CLI

# Priority 3: Interactive (if neither available)
gh auth logout
unset GITHUB_TOKEN  
python git-hooks-installer.py .  # Prompts for setup
```

## Verification

### Verify Token Authentication
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Test token with curl
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Expected: JSON response with your user info
```

### Verify GitHub CLI Authentication
```bash
# Check authentication status
gh auth status

# Test with a simple API call
gh api user

# Expected: JSON response with your user info
```

### Test with Installer
```bash
# Dry run to check authentication
python git-hooks-installer.py --check

# Look for authentication confirmation in output
```

## Troubleshooting Authentication

### Token Issues

#### Invalid Token
```bash
# Error: "Bad credentials" or 401 Unauthorized
# Solution: Generate a new token with correct scopes

# Check token scopes
curl -H "Authorization: token $GITHUB_TOKEN" -I https://api.github.com/user
# Look for X-OAuth-Scopes header
```

#### Expired Token
```bash
# Error: "requires authentication" or token expired
# Solution: Generate new token and update environment

export GITHUB_TOKEN=new_token_here
```

#### Missing Scopes
```bash
# Error: "Resource not accessible by integration"
# Solution: Ensure token has 'repo' scope

# Create new token with these scopes:
# ✅ repo (Full control of private repositories)
# ✅ write:packages (optional, for package operations)
```

### GitHub CLI Issues

#### Not Authenticated
```bash
# Error: "To get started with GitHub CLI, please run: gh auth login"
# Solution: Authenticate with GitHub

gh auth login
```

#### Wrong Account
```bash
# Check current account
gh auth status

# Switch accounts
gh auth logout
gh auth login
```

#### Permission Issues
```bash
# Error: "insufficient privileges"
# Check repository permissions
gh repo view owner/repository
```

### Network Issues

#### Corporate Proxy
```bash
# Configure Git proxy
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# Configure GitHub CLI proxy
gh config set http_proxy http://proxy.company.com:8080
```

#### Firewall Restrictions
```bash
# Required outbound connections:
# api.github.com:443 (HTTPS)
# github.com:443 (HTTPS) or github.com:22 (SSH)

# Test connectivity
curl -I https://api.github.com
telnet github.com 443
```

## Security Best Practices

### Token Security
- **Never commit tokens** to version control
- **Use .env files** and add them to `.gitignore`
- **Set appropriate expiration** (30-90 days recommended)
- **Rotate tokens regularly** especially for production use
- **Use minimal scopes** (only `repo` scope needed)

### Environment Security
```bash
# Good: Environment variable
export GITHUB_TOKEN=ghp_xxx

# Good: .env file (gitignored)
echo "GITHUB_TOKEN=ghp_xxx" >> .env

# BAD: Never commit to repository
git add .env  # ❌ Don't do this!
```

### Access Control
- **Repository permissions**: Ensure token owner has write access
- **Organization policies**: Check if organization restricts token usage
- **Two-factor authentication**: Enable 2FA on your GitHub account

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/install-hooks.yml
name: Install Git Hooks
on: [push]
jobs:
  install-hooks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Git Hooks
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python git-hooks-installer/git-hooks-installer.py .
```

### GitLab CI
```yaml
# .gitlab-ci.yml
install-hooks:
  script:
    - export GITHUB_TOKEN=$GITHUB_TOKEN_SECRET
    - python git-hooks-installer/git-hooks-installer.py .
  variables:
    GITHUB_TOKEN_SECRET: $GITHUB_TOKEN
```

### Jenkins
```groovy
pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('github-token')
    }
    stages {
        stage('Install Hooks') {
            steps {
                sh 'python git-hooks-installer/git-hooks-installer.py .'
            }
        }
    }
}
```

## Alternative Methods

### SSH Keys (For Git Operations)
While the installer uses HTTPS for API calls, your repository might use SSH:

```bash
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and paste to: https://github.com/settings/ssh/new
```

### Fine-grained Personal Access Tokens (Beta)
GitHub's new fine-grained tokens provide more precise permissions:

1. Go to https://github.com/settings/personal-access-tokens/fine-grained
2. Select specific repositories instead of all repositories
3. Choose minimal permissions needed
4. Use same as classic tokens in environment variables

The installer works with both classic and fine-grained tokens.