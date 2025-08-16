# CLI Options Reference

Complete command-line interface reference for the Git Hooks Installer.

## Synopsis

```bash
python git-hooks-installer.py [OPTIONS] [TARGET]
```

## Arguments

### TARGET

**Description:** Path to the target Git repository where hooks will be installed

**Type:** String (path)  
**Default:** `.` (current directory)  
**Required:** No

**Examples:**
```bash
# Install in current directory
python git-hooks-installer.py

# Install in current directory (explicit)
python git-hooks-installer.py .

# Install in specific directory
python git-hooks-installer.py /path/to/repository

# Install in relative path
python git-hooks-installer.py ../other-project

# Install in home directory project
python git-hooks-installer.py ~/projects/myapp
```

**Validation:**
- Must be an existing directory
- Must contain a `.git` directory (valid Git repository)
- Must have write permissions

## Options

### -c, --check

**Description:** Check current installation status without making changes

**Type:** Flag (boolean)  
**Default:** False

**Usage:**
```bash
# Check installation status
python git-hooks-installer.py -c
python git-hooks-installer.py --check

# Check specific repository
python git-hooks-installer.py --check /path/to/repo
```

**Output Example:**
```
🔍 Checking git hooks installation status...

✅ Post-commit hook: INSTALLED
   └─ Executable: YES
✅ Scripts directory: INSTALLED  
   └─ Found 4 script files
✅ Developer setup: INSTALLED
✅ Shell wrapper (sh): INSTALLED
✅ PowerShell wrapper (ps1): INSTALLED
✅ Documentation directory: EXISTS
   └─ Commit logs for 3 branches

🎉 Git hooks installation: COMPLETE
ℹ️ Ready to automatically document commits!
```

### -f, --force

**Description:** Force reinstall even if installation is up-to-date

**Type:** Flag (boolean)  
**Default:** False

**Usage:**
```bash
# Force reinstall
python git-hooks-installer.py -f
python git-hooks-installer.py --force

# Force reinstall specific repository
python git-hooks-installer.py --force /path/to/repo
```

**Behavior:**
- Skips version checks
- Overwrites existing files
- Creates new feature branch even if current installation is latest version
- Useful for fixing corrupted installations or testing

### -v, --verbose

**Description:** Enable verbose logging output

**Type:** Flag (boolean)  
**Default:** False

**Usage:**
```bash
# Verbose output
python git-hooks-installer.py -v
python git-hooks-installer.py --verbose

# Combine with other options
python git-hooks-installer.py --verbose --check
```

**Output Level:** INFO and above  
**Additional Information:**
- File operations details
- Git command execution
- Authentication method used
- Detailed progress messages

### -d, --debug

**Description:** Enable debug logging output (most verbose)

**Type:** Flag (boolean)  
**Default:** False

**Usage:**
```bash
# Debug output
python git-hooks-installer.py -d
python git-hooks-installer.py --debug

# Debug with force reinstall
python git-hooks-installer.py --debug --force
```

**Output Level:** DEBUG and above  
**Additional Information:**
- Internal function calls
- Variable states
- Detailed error information
- File validation steps
- Network request/response details

### --no-ci

**Description:** Skip CI/CD file installation

**Type:** Flag (boolean)  
**Default:** False

**Usage:**
```bash
# Skip CI/CD files
python git-hooks-installer.py --no-ci

# Useful for repositories without CI/CD
python git-hooks-installer.py --no-ci /path/to/simple-repo
```

**Behavior:**
- Skips detection and installation of CI/CD configuration files
- Reduces installation time
- Useful for repositories that don't use automated CI/CD

### -h, --help

**Description:** Show help message and exit

**Type:** Flag (boolean)

**Usage:**
```bash
python git-hooks-installer.py -h
python git-hooks-installer.py --help
```

**Output:**
```
usage: git-hooks-installer.py [-h] [-f] [-v] [-d] [--no-ci] [-c] [target]

Install/update git hooks, scripts, and documentation in a Git repository.

positional arguments:
  target         Path to the target Git repository where hooks will be
                 installed (default: current directory)

optional arguments:
  -h, --help     show this help message and exit
  -f, --force    Force reinstall even if up-to-date
  -v, --verbose  Enable verbose logging
  -d, --debug    Enable debug logging
  --no-ci        Skip CI/CD file installation
  -c, --check    Check current installation status

Examples:
  git-hooks-installer.py                              # Install in current directory
  git-hooks-installer.py /path/to/project             # Install in specific git repository
  git-hooks-installer.py -c                           # Check installation status
  git-hooks-installer.py -f                           # Force reinstall
  git-hooks-installer.py -v /path/to/project          # Verbose installation in specific repo
  git-hooks-installer.py -d --no-ci                   # Debug mode, skip CI files
```

## Option Combinations

### Common Combinations

#### Status Check with Verbose Output
```bash
python git-hooks-installer.py --check --verbose
```
Shows detailed status information including file paths and permissions.

#### Force Reinstall with Debug
```bash
python git-hooks-installer.py --force --debug
```
Useful for troubleshooting installation issues.

#### Quiet Installation (No CI)
```bash
python git-hooks-installer.py --no-ci /path/to/repo
```
Minimal installation for simple repositories.

#### Development Testing
```bash
python git-hooks-installer.py --debug --force --no-ci
```
Maximum verbosity, force reinstall, skip CI files for development testing.

### Incompatible Combinations

#### Check with Modifying Options
```bash
# ❌ Invalid: Check doesn't modify, force does
python git-hooks-installer.py --check --force

# ❌ Invalid: Check doesn't install CI files
python git-hooks-installer.py --check --no-ci
```

When `--check` is used, all other options except `--verbose` and `--debug` are ignored.

## Exit Codes

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| 0 | Success | Installation completed successfully |
| 1 | General Error | Installation failed (see error output) |
| 2 | Invalid Arguments | Invalid command-line arguments provided |
| 3 | Repository Error | Target is not a valid Git repository |
| 4 | Permission Error | Insufficient permissions for installation |
| 5 | Network Error | GitHub authentication or API failure |

**Usage in Scripts:**
```bash
#!/bin/bash
if python git-hooks-installer.py /path/to/repo; then
    echo "Installation successful"
else
    echo "Installation failed with exit code $?"
    exit 1
fi
```

## Environment Variables

### Authentication

#### GITHUB_TOKEN
**Description:** GitHub Personal Access Token for automatic PR creation  
**Format:** `ghp_` followed by 36 characters  
**Example:** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

```bash
export GITHUB_TOKEN=ghp_your_token_here
python git-hooks-installer.py .
```

#### GH_TOKEN
**Description:** Alternative name for GitHub token  
**Priority:** Lower than GITHUB_TOKEN

```bash
export GH_TOKEN=ghp_your_token_here
python git-hooks-installer.py .
```

### Configuration

#### GITHOOKS_INSTALLER_PATH
**Description:** Custom path to installer source directory  
**Default:** Auto-detected from script location

```bash
export GITHOOKS_INSTALLER_PATH=/custom/path/to/installer
python git-hooks-installer.py .
```

#### GIT_TERMINAL_PROMPT
**Description:** Disable Git interactive prompts (set by installer)  
**Value:** `0` (disabled)

This is automatically set by the installer to prevent hanging.

### Proxy Configuration

#### HTTP_PROXY / HTTPS_PROXY
**Description:** HTTP/HTTPS proxy for network requests

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
python git-hooks-installer.py .
```

## Configuration Files

### .env File Support

The installer can create and read `.env` files for token storage:

```bash
# .env file in target repository
GITHUB_TOKEN=ghp_your_token_here
```

**Security Note:** Always add `.env` to `.gitignore`!

### Git Configuration

The installer respects these Git configuration settings:

```bash
# Proxy settings
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# SSH vs HTTPS
git config --global url."https://github.com/".insteadOf git@github.com:
```

## Examples

### Basic Usage

```bash
# Simple installation
python git-hooks-installer.py

# Install in different directory
python git-hooks-installer.py ~/projects/my-app

# Check if already installed
python git-hooks-installer.py --check
```

### Advanced Usage

```bash
# Force reinstall with debug output
python git-hooks-installer.py --force --debug

# Install without CI files in verbose mode
python git-hooks-installer.py --no-ci --verbose /path/to/repo

# Check installation status with detailed output
python git-hooks-installer.py --check --verbose
```

### Automation Scripts

```bash
#!/bin/bash
# Batch installation script

REPOS=(
    "/path/to/repo1"
    "/path/to/repo2"
    "/path/to/repo3"
)

for repo in "${REPOS[@]}"; do
    echo "Installing hooks in $repo..."
    if python git-hooks-installer.py --verbose "$repo"; then
        echo "✅ Success: $repo"
    else
        echo "❌ Failed: $repo"
    fi
done
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Install Git Hooks
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python git-hooks-installer/git-hooks-installer.py \
      --verbose \
      --no-ci \
      .
```

## Performance Considerations

### Resource Usage by Option

| Option | CPU Impact | Memory Impact | Network Impact |
|--------|------------|---------------|----------------|
| Default | Low | Low | Medium (if authenticated) |
| --verbose | Low | Low | Medium |
| --debug | Medium | Medium | Medium |
| --force | Low | Low | Medium |
| --no-ci | Lower | Lower | Medium |
| --check | Minimal | Minimal | None |

### Timing

Typical execution times:
- **Check mode**: 1-2 seconds
- **Basic installation**: 10-30 seconds
- **With PR creation**: 15-45 seconds
- **Debug mode**: 20-60 seconds

Factors affecting performance:
- Repository size
- Network latency  
- GitHub API response time
- File system performance