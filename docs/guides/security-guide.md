# Security Guide

Comprehensive security guidance for the Git Hooks Installer, covering threat model, security controls, and best practices.

## Security Overview

The Git Hooks Installer is designed with security as a first-class concern, implementing multiple layers of protection to ensure safe operation in production environments.

### Security Guarantees

✅ **Repository State Validation** - Pre-flight checks prevent unsafe installations  
✅ **File Tracking** - Only installer-created files are committed, never user data  
✅ **No Secret Leakage** - User secrets and work-in-progress are never included  
✅ **Mandatory Review** - All installations require pull request review  
✅ **Branch Protection** - No direct commits to main/protected branches  

## Threat Model

### Threats Addressed

| Threat | Risk Level | Mitigation |
|--------|------------|------------|
| Command Injection | High | Secure command validation and whitelisting |
| Path Traversal | High | Realpath validation and directory containment |
| Secret Exposure | High | File tracking and .gitignore respect |
| Resource Exhaustion | Medium | File limits and timeout controls |
| Race Conditions | Medium | Atomic operations with file locking |
| Information Disclosure | Medium | Sanitized error messages |

### Attack Vectors Considered

1. **Malicious Repository Paths** - Attempts to access files outside repository
2. **Branch Name Injection** - Special characters in branch names for command injection
3. **Large File DoS** - Overwhelming system with large files or many files
4. **Concurrent Access** - Race conditions during installation
5. **Network MITM** - Interception of GitHub API communications
6. **Token Theft** - Unauthorized access to GitHub authentication tokens

## Security Architecture

### Defense in Depth

The installer implements multiple security layers:

```
┌─────────────────────────────────────────┐
│           User Input Layer              │
│  • Input validation                     │
│  • Argument sanitization               │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│       Repository Validation Layer       │
│  • Pre-flight safety checks            │
│  • Repository state validation         │
│  • Sensitive file detection            │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Command Execution Layer         │
│  • SecureGitWrapper                     │
│  • Command whitelisting                 │
│  • Argument validation                  │
│  • Timeout protection                   │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          File Operations Layer          │
│  • FileTracker class                    │
│  • Atomic operations                    │
│  • File locking                         │
│  • Resource limits                      │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Network Security Layer          │
│  • HTTPS enforcement                    │
│  • Token-based authentication          │
│  • Error sanitization                   │
└─────────────────────────────────────────┘
```

## Security Controls

### Input Validation

#### Branch Name Validation
```python
# Only allow safe characters in branch names
BRANCH_NAME_PATTERN = r'^[a-zA-Z0-9/_.-]+$'

# Prevent injection through branch names
if not re.match(BRANCH_NAME_PATTERN, branch_name):
    raise SecurityError("Invalid branch name")
```

#### Path Validation
```python
# Prevent path traversal attacks
def validate_path(path, base_path):
    real_path = os.path.realpath(path)
    real_base = os.path.realpath(base_path)
    
    # Ensure path is within base directory
    if not real_path.startswith(real_base):
        raise SecurityError("Path traversal attempt detected")
```

#### File Extension Filtering
```python
# Exclude dangerous and cache files
EXCLUDED_PATTERNS = [
    '__pycache__',
    '*.pyc', '*.pyo', '*.pyd',
    '.*',  # Hidden files
    '*.tmp', '*.temp',
    'node_modules',
]
```

### Command Security

#### SecureGitWrapper
The installer uses a secure Git wrapper that:

- **Whitelists Commands**: Only allows approved Git operations
- **Validates Arguments**: Checks each argument against known patterns
- **Prevents Shell Injection**: Uses `shell=False` for all subprocess calls
- **Enforces Timeouts**: 30-second timeout for all Git operations
- **Sanitizes Output**: Removes sensitive information from error messages

```python
# Example secure command execution
class SecureGitWrapper:
    ALLOWED_COMMANDS = [
        'status', 'branch', 'checkout', 'add', 'commit', 
        'push', 'remote', 'diff', 'log'
    ]
    
    def run(self, command, *args, **kwargs):
        if command not in self.ALLOWED_COMMANDS:
            raise SecurityError(f"Command not allowed: {command}")
        
        # Validate all arguments
        for arg in args:
            if not self._validate_argument(arg):
                raise SecurityError(f"Invalid argument: {arg}")
        
        # Execute with security controls
        return subprocess.run(
            ['git', command] + list(args),
            shell=False,  # Prevent shell injection
            timeout=30,   # Prevent hanging
            **kwargs
        )
```

### Resource Protection

#### File Limits
```python
# Prevent resource exhaustion
MAX_FILES = 1000
MAX_DIRECTORIES = 100
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB
```

#### Race Condition Prevention
```python
# Atomic file operations with locking
import fcntl

def safe_file_operation(file_path):
    with open(file_path, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        # Perform atomic operation
        # Lock automatically released when file closes
```

### Network Security

#### HTTPS Enforcement
- All GitHub API calls use HTTPS
- SSL certificate validation enabled
- No fallback to HTTP connections

#### Token Protection
```python
# Secure token handling
def sanitize_error_message(error_msg, token):
    # Remove token from error messages
    if token and token in error_msg:
        return error_msg.replace(token, '***REDACTED***')
    return error_msg
```

## Authentication Security

### GitHub Token Security

#### Token Requirements
- **Scope**: Minimum `repo` scope only
- **Expiration**: Set appropriate expiration (30-90 days)
- **Rotation**: Regular token rotation recommended
- **Storage**: Environment variables or secure .env files only

#### Token Best Practices
```bash
# ✅ Good: Environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ✅ Good: .env file (gitignored)
echo "GITHUB_TOKEN=ghp_xxx" >> .env
echo ".env" >> .gitignore

# ❌ Bad: Hardcoded in scripts
GITHUB_TOKEN="ghp_xxx"  # Never do this!

# ❌ Bad: Committed to repository
git add .env && git commit  # Dangerous!
```

### GitHub CLI Security

#### Authentication Verification
```bash
# Verify authentication before use
gh auth status

# Check token scopes
gh auth token | gh api user --header "Authorization: token @-"
```

#### Secure Configuration
```bash
# Use keyring for token storage (default)
gh auth login --web

# Avoid storing credentials in plain text
gh config set git_protocol https
```

## Deployment Security

### CI/CD Security

#### Secrets Management
```yaml
# GitHub Actions - Secure secret usage
name: Install Git Hooks
on: [push]
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Hooks
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Use secrets
        run: python git-hooks-installer.py .
```

#### Pipeline Isolation
- Use dedicated service accounts for automation
- Limit token permissions to minimum required
- Implement approval workflows for production deployments
- Use separate tokens for different environments

### Network Security

#### Firewall Configuration
```bash
# Required outbound connections
# GitHub API
443/tcp -> api.github.com

# GitHub Git operations
443/tcp -> github.com (HTTPS)
22/tcp -> github.com (SSH, optional)
```

#### Proxy Configuration
```bash
# Corporate proxy setup (if required)
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy https://proxy.company.com:8080

# Python requests proxy
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
```

## Monitoring and Auditing

### Security Logging

#### Installation Logs
```python
# Security-relevant events are logged
logger.info("Pre-flight validation started")
logger.info("Branch created: %s", sanitize_branch_name(branch))
logger.info("Files tracked: %d", file_count)
logger.warning("Authentication method: %s", auth_method)
```

#### Audit Trail
- All file operations are recorded in manifest
- Git commits provide complete change history
- Pull requests create review audit trail
- GitHub API calls are logged by GitHub

### Monitoring Indicators

#### Security Metrics
- Failed authentication attempts
- Invalid input attempts
- Resource limit violations
- Timeout occurrences
- Path traversal attempts

#### Alerting Recommendations
```bash
# Monitor for suspicious patterns
grep "SecurityError" /var/log/git-hooks-installer.log
grep "Path traversal" /var/log/git-hooks-installer.log
grep "Command not allowed" /var/log/git-hooks-installer.log
```

## Security Assessments

### Static Analysis

#### Bandit Security Scan
```bash
# Run security linter
bandit -r git-hooks-installer/ -f json

# Check for high-severity issues
bandit -r git-hooks-installer/ -ll
```

#### Dependency Scanning
```bash
# Check for vulnerable dependencies
safety check --json

# Audit Python packages
pip-audit
```

### Dynamic Testing

#### Penetration Testing
```bash
# Test injection vulnerabilities
python git-hooks-installer.py "; rm -rf /"
python git-hooks-installer.py "../../../etc/passwd"

# Test resource exhaustion
python -c "print('x' * 1000000)" | python git-hooks-installer.py /dev/stdin
```

#### Fuzzing
```bash
# Fuzz branch names
for i in {1..1000}; do
    random_branch=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 50)
    python git-hooks-installer.py --branch "$random_branch" . || true
done
```

## Incident Response

### Security Incident Procedures

#### Immediate Response
1. **Isolate**: Stop the installer if running
2. **Assess**: Determine scope of potential compromise
3. **Contain**: Revoke any potentially compromised tokens
4. **Investigate**: Analyze logs and system state

#### Recovery Steps
```bash
# Emergency cleanup
git reset --hard HEAD  # Remove uncommitted changes
git clean -fd          # Remove untracked files

# Revoke compromised tokens
gh auth logout
# Generate new token at https://github.com/settings/tokens

# Check for unauthorized changes
git log --oneline --since="1 hour ago"
git diff HEAD~5..HEAD
```

### Vulnerability Reporting

#### Security Contact
Report security vulnerabilities privately to the project maintainers before public disclosure.

#### Vulnerability Assessment
- **CVSS Scoring**: Use Common Vulnerability Scoring System
- **Impact Analysis**: Assess potential damage and scope
- **Remediation Timeline**: Prioritize based on severity

## Compliance and Standards

### Security Standards Alignment

#### OWASP Top 10
- **A03 - Injection**: Prevented through input validation and parameterized commands
- **A04 - Insecure Design**: Secure-by-design architecture with threat modeling
- **A07 - ID and Auth Failures**: Strong authentication requirements and token management
- **A08 - Software Integrity**: File tracking and manifest verification
- **A09 - Logging Failures**: Comprehensive security logging

#### CIS Controls
- **Control 3**: Data Protection through file tracking
- **Control 4**: Secure Configuration through validation
- **Control 6**: Audit Log Management through comprehensive logging
- **Control 11**: Data Recovery through Git history

### Regulatory Considerations

#### GDPR Compliance
- No personal data collection by installer
- Authentication tokens are user-controlled
- Data processing transparency through logging

#### SOX Compliance  
- Change management through pull request workflow
- Audit trail through Git history
- Segregation of duties through review requirements

## Security Checklist

### Pre-Installation Security Review

- [ ] Repository has no uncommitted secrets
- [ ] .gitignore includes sensitive files (.env, tokens, keys)
- [ ] Branch protection rules are configured
- [ ] Authentication method is properly configured
- [ ] Network access controls are in place
- [ ] Monitoring and logging are enabled

### Post-Installation Security Verification

- [ ] Pull request created and reviewed
- [ ] No sensitive data in committed files
- [ ] Git hooks execute without errors
- [ ] Authentication tokens remain secure
- [ ] Resource usage is within expected limits
- [ ] Audit logs capture all operations

This security guide should be reviewed regularly and updated as threats and mitigations evolve.