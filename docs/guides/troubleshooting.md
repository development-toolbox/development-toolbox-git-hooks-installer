# Troubleshooting Guide

Solutions for common issues when installing and using the Git Hooks Installer.

## Installation Issues

### Repository Has Uncommitted Changes {#uncommitted-changes}

**Error:**
```
❌ Repository validation failed:
   Repository has uncommitted changes:
  Modified: file1.txt
  Added: file2.txt
   Please commit or stash changes before installation.
```

**Solution:**
```bash
# Option 1: Commit your changes
git add .
git commit -m "feat: save current work before hooks installation"

# Option 2: Stash your changes
git stash push -m "temporary stash before hooks installation"

# Option 3: Check what's uncommitted
git status
git diff
```

**Prevention:**
Always run the installer on a clean working tree to avoid conflicts.

### Permission Denied Errors {#permission-errors}

**Error:**
```
PermissionError: [Errno 13] Permission denied: '.git/hooks/post-commit'
```

**Solutions:**

#### Check Repository Permissions
```bash
# Verify you own the repository directory
ls -la .git/hooks/

# Fix ownership if needed (Linux/macOS)
sudo chown -R $USER:$USER .git/

# Check if hooks directory is writable
chmod u+w .git/hooks/
```

#### Windows-Specific Issues
```powershell
# Run PowerShell as Administrator
# Check file permissions
Get-Acl .git\hooks | Format-List

# Fix permissions
icacls .git\hooks /grant "$env:USERNAME:(F)" /T
```

#### Corporate/Shared Systems
```bash
# Check if .git directory is on a network drive
df -h .git/

# If on network drive, ensure proper mount options
mount | grep "$(dirname "$(pwd)")"
```

### GitHub Authentication Failed {#github-auth-failed}

**Error:**
```
⚠️ Could not create PR: 401 Unauthorized
```

**Solutions:**

#### Verify Token
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Test token validity
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Check token scopes
curl -H "Authorization: token $GITHUB_TOKEN" -I https://api.github.com/user
# Look for X-OAuth-Scopes header
```

#### Token Issues
```bash
# Generate new token with correct scopes
# Required: repo (Full control of private repositories)
# URL: https://github.com/settings/tokens

# Update token
export GITHUB_TOKEN=ghp_new_token_here
```

#### GitHub CLI Issues
```bash
# Check authentication
gh auth status

# Re-authenticate if needed
gh auth logout
gh auth login

# Verify permissions
gh repo view $(git remote get-url origin)
```

### Python Version Compatibility {#python-version}

**Error:**
```
SyntaxError: invalid syntax
  return (method, credential) where method is 'token', 'gh', or None
                               ^^^^^
```

**Solution:**
This error indicates Python version is too old (< 3.8). The installer requires Python 3.9+.

```bash
# Check current Python version
python3 --version

# Install newer Python (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12

# Install newer Python (CentOS/RHEL)
sudo dnf install python3.12

# Install newer Python (macOS)
brew install python@3.12

# Use specific Python version
python3.12 git-hooks-installer/git-hooks-installer.py .
```

### Remote Origin Not Found

**Error:**
```
❌ Pre-flight checks failed:
   No remote 'origin' configured
```

**Solution:**
```bash
# Add remote origin
git remote add origin https://github.com/username/repository.git

# Or set existing remote
git remote set-url origin https://github.com/username/repository.git

# Verify remote
git remote -v
```

### Branch Already Exists

**Error:**
```
fatal: A branch named 'feat/githooks-installation-20240816-123456' already exists.
```

**Solution:**
```bash
# Delete existing branch
git branch -D feat/githooks-installation-20240816-123456

# Or force reinstall
python git-hooks-installer.py --force .
```

## Runtime Issues

### Post-commit Hook Not Executing

**Symptoms:**
- No documentation generated after commits
- Hook appears installed but doesn't run

**Debugging:**
```bash
# Check if hook exists and is executable
ls -la .git/hooks/post-commit

# Make hook executable if needed
chmod +x .git/hooks/post-commit

# Test hook manually
.git/hooks/post-commit

# Check for errors in hook
cat .git/hooks/post-commit
```

**Common Fixes:**
```bash
# Fix Python path in hook
which python3
# Update shebang in .git/hooks/post-commit if needed

# Check Python modules
python3 -c "import sys; print(sys.path)"

# Test scripts directory
ls -la scripts/post-commit/
python3 scripts/post-commit/generate_git_timeline.py
```

### Documentation Not Generated

**Symptoms:**
- Hook runs but no files created in `docs/commit-logs/`

**Debugging:**
```bash
# Check if docs directory exists
ls -la docs/

# Check permissions
ls -la docs/commit-logs/

# Test script manually
cd scripts/post-commit/
python3 generate_git_timeline.py

# Check for import errors
python3 -c "from githooks_utils import *"
```

**Solutions:**
```bash
# Create docs directory if missing
mkdir -p docs/commit-logs/$(git branch --show-current)

# Fix permissions
chmod -R u+w docs/

# Reinstall with force
python git-hooks-installer.py --force .
```

### Infinite Loop or Recursive Hooks

**Symptoms:**
- Hook triggers itself repeatedly
- System becomes unresponsive during commits

**Immediate Fix:**
```bash
# Disable hook temporarily
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Kill any running processes
ps aux | grep git-hooks
kill -9 <process_id>
```

**Permanent Solution:**
```bash
# Check for lock file mechanism
cat .git/hooks/post-commit | grep -i lock

# Ensure hook has proper guards
grep -n "recursive" .git/hooks/post-commit
```

## Network and Connectivity Issues

### API Rate Limiting

**Error:**
```
403 rate limit exceeded
```

**Solutions:**
```bash
# Wait for rate limit reset (usually 1 hour)
# Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Use authenticated requests (higher limits)
export GITHUB_TOKEN=your_token_here
```

### Proxy Configuration

**Corporate Network Issues:**
```bash
# Configure Git proxy
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# Configure environment proxy
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080

# Test connectivity
curl -I https://api.github.com
```

### SSL Certificate Issues

**Error:**
```
SSL certificate verify failed
```

**Solutions:**
```bash
# Update certificates (Linux)
sudo apt update && sudo apt install ca-certificates

# Update certificates (macOS)
brew install ca-certificates

# Temporary workaround (not recommended for production)
git config --global http.sslVerify false
```

## Platform-Specific Issues

### Windows Issues

#### PowerShell Execution Policy
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative: bypass for single script
powershell -ExecutionPolicy Bypass -File setup-githooks.ps1
```

#### Windows Defender Interference
```powershell
# Add exclusion for Git hooks
Add-MpPreference -ExclusionPath "C:\path\to\repository\.git\hooks"

# Check Windows Defender logs
Get-WinEvent -LogName "Microsoft-Windows-Windows Defender/Operational" -MaxEvents 50
```

#### Path Length Limitations
```powershell
# Enable long path support (Windows 10+)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Or use shorter paths
subst G: C:\very\long\path\to\repository
cd G:\
```

### macOS Issues

#### Gatekeeper Restrictions
```bash
# If Python scripts are blocked
xattr -r -d com.apple.quarantine /path/to/git-hooks-installer

# Check for quarantine attributes
xattr -l git-hooks-installer.py
```

#### Permission Issues with System Python
```bash
# Use Homebrew Python instead of system Python
brew install python@3.12
/opt/homebrew/bin/python3.12 git-hooks-installer.py .
```

### Linux Issues

#### SELinux Restrictions
```bash
# Check SELinux status
sestatus

# Allow Git hooks (CentOS/RHEL)
setsebool -P git_session_users 1

# Check context
ls -Z .git/hooks/post-commit

# Restore context if needed
restorecon -R .git/hooks/
```

#### AppArmor Issues
```bash
# Check AppArmor status
sudo apparmor_status

# Check for denials
sudo dmesg | grep -i apparmor | grep -i denied
```

## Performance Issues

### Slow Installation

**Causes and Solutions:**
```bash
# Large repository with many files
# Solution: Use --no-ci flag to skip CI file processing
python git-hooks-installer.py --no-ci .

# Slow network connection
# Solution: Use local installation without PR creation
unset GITHUB_TOKEN
python git-hooks-installer.py .

# Debug mode slowing things down
# Solution: Remove debug flags
python git-hooks-installer.py .  # No -d or --debug
```

### High Resource Usage

**Memory Issues:**
```bash
# Check available memory
free -h

# Monitor installer resource usage
top -p $(pgrep -f git-hooks-installer)

# Use resource limits
ulimit -v 1048576  # 1GB virtual memory limit
python git-hooks-installer.py .
```

## Recovery Procedures

### Complete Cleanup

If installation is severely broken:

```bash
# Remove all git hooks
rm -f .git/hooks/post-commit .git/hooks/pre-commit .git/hooks/*

# Remove installed files (be careful!)
rm -rf scripts/post-commit/
rm -rf docs/githooks/
rm -rf developer-setup/
rm -f setup-githooks.sh setup-githooks.ps1

# Reset to clean state
git reset --hard HEAD
git clean -fd

# Remove any feature branches
git branch -D $(git branch | grep feat/githooks-installation)
```

### Partial Recovery

If only some components are broken:

```bash
# Reinstall just the hooks
cp git-hooks-installer/git-hooks/post-commit .git/hooks/
chmod +x .git/hooks/post-commit

# Reinstall just the scripts
rm -rf scripts/post-commit/
python git-hooks-installer.py --force .
```

## Getting Help

### Debug Information Collection

When reporting issues, include:

```bash
# System information
uname -a
python3 --version
git --version

# Repository information
git remote -v
git status
git branch --show-current

# Installation attempt with debug
python git-hooks-installer.py --debug . > install-debug.log 2>&1

# Authentication status
echo "GITHUB_TOKEN set: $([ -n "$GITHUB_TOKEN" ] && echo "yes" || echo "no")"
gh auth status 2>/dev/null || echo "gh CLI not authenticated"
```

### Common Log Locations

```bash
# Installation logs
tail -f install-debug.log

# Git hooks logs
tail -f .git/hooks/post-commit.log

# System logs (Linux)
journalctl -u git* --since "1 hour ago"

# System logs (macOS)
log show --predicate 'process CONTAINS "git"' --last 1h
```

### Support Channels

1. **Check Documentation**: Review all docs in `docs/` directory
2. **Search Issues**: Look for similar problems in project issues
3. **Create Detailed Issue**: Include debug information and steps to reproduce
4. **Security Issues**: Report privately for security vulnerabilities

Remember: Most issues are configuration-related and can be resolved by carefully following the setup instructions.