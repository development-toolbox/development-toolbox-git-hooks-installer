# Security Enhancements for Git Operations

## Overview

The safe git hooks installer uses a **SecureGitWrapper** to provide additional security measures for all subprocess Git operations. This addresses security concerns raised by static analysis tools while maintaining functionality.

## Security Features

### 1. Command Whitelisting
- Only approved Git commands can be executed
- Prevents arbitrary command injection
- Currently allowed commands: `status`, `branch`, `checkout`, `add`, `commit`, `push`, `remote`, `init`, `config`, `show-ref`, `log`, `diff`, `ls-files`, `reset`, `clean`

### 2. Argument Validation
- Each command has a whitelist of allowed arguments
- Prevents injection of malicious flags
- Example: `checkout` only allows `-b` and `--quiet` flags

### 3. Path Sanitization
- All file paths are validated before use
- Prevents path traversal attacks (e.g., `../../../etc/passwd`)
- Ensures paths stay within the repository

### 4. Branch Name Validation
- Branch names must match pattern: `^[a-zA-Z0-9/_-]+$`
- Maximum length: 255 characters
- Prevents special characters that could be interpreted as commands

### 5. Timeout Protection
- Default 30-second timeout for all Git operations
- Prevents hanging on network operations or prompts
- Configurable per instance

### 6. No Shell Execution
- `shell=False` is enforced on all subprocess calls
- Commands are passed as lists, not strings
- Prevents shell metacharacter interpretation

### 7. Git Prompt Disabled
- Sets `GIT_TERMINAL_PROMPT=0` environment variable
- Prevents hanging on authentication prompts
- Forces operations to fail fast if credentials needed

### 8. Type Safety
- Proper null checks for optional values
- Type guards prevent None values reaching Git commands
- Mypy/Pylance compatible type hints

## Usage Example

```python
# Updated import path - now in security package
from security.secure_git_wrapper import SecureGitWrapper, SecureGitError
# OR use package import
from security import SecureGitWrapper, SecureGitError

# Initialize wrapper with repository path
git = SecureGitWrapper("/path/to/repo")

# All operations are validated before execution
try:
    # Check if working tree is clean
    if git.status_clean():
        # Create and checkout new branch
        git.create_branch("feat/new-feature")
        
        # Add files (paths are sanitized)
        git.add_file("src/main.py")
        
        # Commit with message
        git.commit("feat: add new feature")
        
        # Push to remote
        git.push_branch("feat/new-feature")
        
except SecureGitError as e:
    # Handle validation errors
    logger.error(f"Git operation failed validation: {e}")
except subprocess.CalledProcessError as e:
    # Handle Git command failures
    logger.error(f"Git command failed: {e}")
```

## Bandit Compliance

All subprocess calls using SecureGitWrapper can be marked with:
```python
# nosec B602 - Using SecureGitWrapper with validation
```

This is justified because:
1. All inputs are validated against whitelists
2. No user input reaches subprocess without sanitization
3. Shell execution is disabled
4. Timeouts prevent resource exhaustion

## Fallback Support

The implementation gracefully falls back to direct subprocess calls if SecureGitWrapper is not available, maintaining backwards compatibility while still validating inputs where possible.

## Future Enhancements

1. **Audit Logging** - Log all Git operations for security monitoring
2. **Rate Limiting** - Prevent rapid-fire Git operations
3. **Custom Validators** - Allow project-specific validation rules
4. **Caching** - Cache validation results for performance
5. **Integration with GitPython** - Optional backend switch

## Security Guarantees

- ✅ No shell injection possible
- ✅ No path traversal attacks
- ✅ No command injection via branch names
- ✅ No hanging on prompts
- ✅ No arbitrary command execution
- ✅ Type-safe operations
- ✅ Comprehensive error handling