# API Reference

Internal API documentation for the Git Hooks Installer components.

## Overview

The Git Hooks Installer is built with a modular architecture consisting of several key components. This document provides technical reference for developers who need to understand, extend, or integrate with the installer.

## Core Classes

### GitHooksInstaller

**File:** `git-hooks-installer.py`  
**Description:** Main installer class that orchestrates the installation process

#### Constructor

```python
class GitHooksInstaller:
    def __init__(self, target_repo: Path, source_dir: Path, force: bool = False, no_ci: bool = False):
        """
        Initialize the installer.
        
        Args:
            target_repo (Path): Path to target repository
            source_dir (Path): Path to installer source directory  
            force (bool): Force reinstall even if up-to-date
            no_ci (bool): Skip CI/CD file installation
        """
```

#### Public Methods

##### install() → bool
```python
def install(self) -> bool:
    """
    Run complete installation process.
    
    Returns:
        bool: True if installation succeeded, False otherwise
        
    Raises:
        SecurityError: If security validation fails
        RepositoryError: If repository validation fails
    """
```

##### check_installation_status() → bool
```python
def check_installation_status(self) -> bool:
    """
    Check and report current installation status.
    
    Returns:
        bool: True if installation is complete, False otherwise
    """
```

##### pre_flight_checks() → bool
```python
def pre_flight_checks(self) -> bool:
    """
    Run comprehensive pre-flight safety checks.
    
    Returns:
        bool: True if all checks pass, False otherwise
    """
```

#### Private Methods

##### _create_safe_feature_branch() → bool
```python
def create_safe_feature_branch(self) -> bool:
    """
    Create feature branch for safe installation.
    
    Returns:
        bool: True if branch created successfully
    """
```

##### _install_git_hooks() → bool
```python
def install_git_hooks(self) -> bool:
    """
    Install git hooks to .git/hooks/ directory.
    
    Returns:
        bool: True if hooks installed successfully
    """
```

##### _commit_tracked_changes() → bool
```python
def commit_tracked_changes(self) -> bool:
    """
    Commit only tracked files with detailed message.
    
    Returns:
        bool: True if commit succeeded
    """
```

## Security Components

### SecureGitWrapper

**File:** `security/secure_git_wrapper.py`  
**Description:** Secure wrapper for Git operations with command validation

#### Constructor

```python
class SecureGitWrapper:
    def __init__(self, repo_path: Path):
        """
        Initialize secure Git wrapper.
        
        Args:
            repo_path (Path): Path to Git repository
        """
```

#### Methods

##### run(command: str, *args, **kwargs) → subprocess.CompletedProcess
```python
def run(self, command: str, *args, **kwargs) -> subprocess.CompletedProcess:
    """
    Execute Git command with security validation.
    
    Args:
        command (str): Git subcommand (must be whitelisted)
        *args: Command arguments
        **kwargs: Additional subprocess options
        
    Returns:
        subprocess.CompletedProcess: Command execution result
        
    Raises:
        SecureGitError: If command is not allowed or validation fails
    """
```

##### get_current_branch() → str
```python
def get_current_branch(self) -> str:
    """
    Get current Git branch name securely.
    
    Returns:
        str: Current branch name
        
    Raises:
        SecureGitError: If branch detection fails
    """
```

##### create_branch(branch_name: str) → None
```python
def create_branch(self, branch_name: str) -> None:
    """
    Create and checkout new branch securely.
    
    Args:
        branch_name (str): Name of branch to create (validated)
        
    Raises:
        SecureGitError: If branch name is invalid or creation fails
    """
```

##### add_file(file_path: str) → None
```python
def add_file(self, file_path: str) -> None:
    """
    Add file to Git staging area securely.
    
    Args:
        file_path (str): Path to file (validated for path traversal)
        
    Raises:
        SecureGitError: If path is invalid or add fails
    """
```

##### commit(message: str) → None
```python
def commit(self, message: str) -> None:
    """
    Create Git commit securely.
    
    Args:
        message (str): Commit message (sanitized)
        
    Raises:
        SecureGitError: If commit fails
    """
```

#### Security Features

- **Command Whitelisting**: Only approved Git commands allowed
- **Argument Validation**: All arguments validated against patterns
- **Path Sanitization**: Prevents path traversal attacks
- **Timeout Protection**: 30-second timeout on all operations
- **Shell Injection Prevention**: Uses `shell=False` for all subprocess calls

### FileTracker

**File:** `security/file_tracker.py`  
**Description:** Tracks installer-created files for safe Git operations

#### Constructor

```python
class FileTracker:
    def __init__(self, repo_path: Path):
        """
        Initialize file tracker for repository.
        
        Args:
            repo_path (Path): Path to Git repository
        """
```

#### Methods

##### track_file_creation(file_path: str, category: str = "general") → None
```python
def track_file_creation(self, file_path: str, category: str = "general") -> None:
    """
    Track a file created by the installer.
    
    Args:
        file_path (str): Relative path to tracked file
        category (str): Category for organization
        
    Raises:
        ValueError: If resource limits exceeded
    """
```

##### track_directory_creation(dir_path: str) → None
```python
def track_directory_creation(self, dir_path: str) -> None:
    """
    Track a directory created by the installer.
    
    Args:
        dir_path (str): Relative path to tracked directory
        
    Raises:
        ValueError: If resource limits exceeded
    """
```

##### safe_add_tracked_files(skip_validation: bool = False) → bool
```python
def safe_add_tracked_files(self, skip_validation: bool = False) -> bool:
    """
    Add only tracked files to Git staging area.
    
    Args:
        skip_validation (bool): Skip final validation step
        
    Returns:
        bool: True if all files added successfully
    """
```

##### validate_staging_area(debug: bool = False) → bool
```python
def validate_staging_area(self, debug: bool = False) -> bool:
    """
    Ensure staging area contains only tracked files.
    
    Args:
        debug (bool): Enable debug output
        
    Returns:
        bool: True if validation passes
    """
```

##### create_detailed_commit_message() → str
```python
def create_detailed_commit_message(self) -> str:
    """
    Create detailed commit message documenting installer actions.
    
    Returns:
        str: Formatted commit message
    """
```

#### Resource Limits

```python
# Class constants
MAX_FILES = 1000              # Maximum tracked files
MAX_DIRECTORIES = 100         # Maximum tracked directories  
MAX_FILE_SIZE = 10 * 1024 * 1024    # 10MB per file
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB total
```

### RepositoryValidator

**File:** `security/repository_validator.py`  
**Description:** Validates repository state and safety before installation

#### Constructor

```python
class RepositoryValidator:
    def __init__(self, repo_path: Path):
        """
        Initialize repository validator.
        
        Args:
            repo_path (Path): Path to repository to validate
        """
```

#### Methods

##### validate_all(branch_name: str) → bool
```python
def validate_all(self, branch_name: str) -> bool:
    """
    Run all validation checks.
    
    Args:
        branch_name (str): Proposed branch name for installation
        
    Returns:
        bool: True if all validations pass
    """
```

##### validate_repository_structure() → bool
```python
def validate_repository_structure(self) -> bool:
    """
    Validate basic repository structure.
    
    Returns:
        bool: True if repository structure is valid
    """
```

##### validate_working_tree() → bool
```python
def validate_working_tree(self) -> bool:
    """
    Validate working tree is clean.
    
    Returns:
        bool: True if working tree is clean
    """
```

##### detect_sensitive_files() → List[str]
```python
def detect_sensitive_files(self) -> List[str]:
    """
    Detect potentially sensitive files in repository.
    
    Returns:
        List[str]: List of potentially sensitive file paths
    """
```

## Utility Functions

### Authentication Utilities

#### check_github_auth() → Tuple[str, str]
```python
def check_github_auth(self) -> Tuple[str, str]:
    """
    Check available GitHub authentication methods.
    
    Returns:
        Tuple[str, str]: (method, credential) where method is 'token', 'gh', or None
    """
```

#### setup_github_auth() → Tuple[str, str]
```python
def setup_github_auth(self) -> Tuple[str, str]:
    """
    Interactively help user set up GitHub authentication.
    
    Returns:
        Tuple[str, str]: (method, credential) or (None, None) if skipped
    """
```

#### create_pull_request() → bool
```python
def create_pull_request(self) -> bool:
    """
    Create pull request automatically using GitHub API or gh CLI.
    
    Returns:
        bool: True if PR created successfully
    """
```

### File System Utilities

#### copy_with_exclusions(src: Path, dst: Path, exclusions: List[str]) → None
```python
def copy_with_exclusions(src: Path, dst: Path, exclusions: List[str]) -> None:
    """
    Copy directory tree with file exclusions.
    
    Args:
        src (Path): Source directory
        dst (Path): Destination directory
        exclusions (List[str]): Patterns to exclude
    """
```

#### is_excluded_file(file_path: Path, exclusions: List[str]) → bool
```python
def is_excluded_file(file_path: Path, exclusions: List[str]) -> bool:
    """
    Check if file should be excluded based on patterns.
    
    Args:
        file_path (Path): File path to check
        exclusions (List[str]): Exclusion patterns
        
    Returns:
        bool: True if file should be excluded
    """
```

## Error Classes

### Base Exceptions

#### GitHooksInstallerError
```python
class GitHooksInstallerError(Exception):
    """Base exception for all installer errors."""
    pass
```

#### SecurityError
```python
class SecurityError(GitHooksInstallerError):
    """Raised when security validation fails."""
    pass
```

#### RepositoryError
```python
class RepositoryError(GitHooksInstallerError):
    """Raised when repository validation fails."""
    pass
```

#### AuthenticationError
```python
class AuthenticationError(GitHooksInstallerError):
    """Raised when GitHub authentication fails."""
    pass
```

### Specific Exceptions

#### SecureGitError
```python
class SecureGitError(SecurityError):
    """Raised by SecureGitWrapper for Git operation failures."""
    pass
```

#### FileTrackingError
```python
class FileTrackingError(SecurityError):
    """Raised by FileTracker for tracking failures."""
    pass
```

#### ValidationError
```python
class ValidationError(RepositoryError):
    """Raised by RepositoryValidator for validation failures."""
    pass
```

## Configuration Constants

### File Patterns

```python
# Files excluded from installation
EXCLUDED_PATTERNS = [
    '__pycache__',
    '*.pyc', '*.pyo', '*.pyd',
    '.*',  # Hidden files
    '*.tmp', '*.temp',
    'node_modules',
    '.DS_Store',
    'Thumbs.db'
]

# Sensitive file patterns
SENSITIVE_PATTERNS = [
    '*.key', '*.pem', '*.p12',
    '*.pfx', '*.cer', '*.crt',
    'secrets.*', 'credentials.*',
    '.env', '.env.*',
    'id_rsa', 'id_ecdsa', 'id_ed25519'
]
```

### Git Settings

```python
# Whitelisted Git commands
ALLOWED_GIT_COMMANDS = [
    'status', 'branch', 'checkout', 'add', 'commit',
    'push', 'pull', 'fetch', 'remote', 'diff', 'log',
    'reset', 'clean', 'show', 'rev-parse'
]

# Branch name validation pattern
BRANCH_NAME_PATTERN = r'^[a-zA-Z0-9/_.-]+$'

# Git operation timeout (seconds)
GIT_TIMEOUT = 30
```

### Resource Limits

```python
# FileTracker limits
MAX_TRACKED_FILES = 1000
MAX_TRACKED_DIRECTORIES = 100
MAX_FILE_SIZE = 10 * 1024 * 1024      # 10MB
MAX_TOTAL_SIZE = 100 * 1024 * 1024    # 100MB

# Network timeouts
GITHUB_API_TIMEOUT = 30
GITHUB_CLONE_TIMEOUT = 300
```

## Extension Points

### Custom Validators

To add custom validation logic:

```python
class CustomValidator(RepositoryValidator):
    def validate_custom_rules(self) -> bool:
        """Add custom validation logic."""
        # Your validation code here
        return True
    
    def validate_all(self, branch_name: str) -> bool:
        # Call parent validation
        if not super().validate_all(branch_name):
            return False
        
        # Add custom validation
        return self.validate_custom_rules()
```

### Custom File Filters

To add custom file filtering:

```python
def custom_file_filter(file_path: Path) -> bool:
    """Custom logic to determine if file should be excluded."""
    # Your filtering logic here
    return False  # False = include, True = exclude

# Use in installer
installer.add_file_filter(custom_file_filter)
```

### Custom Authentication

To add custom authentication methods:

```python
class CustomAuthenticator:
    def check_auth(self) -> Tuple[str, str]:
        """Check for custom authentication."""
        # Your auth checking logic
        return ('custom', 'credentials')
    
    def create_pr(self, branch_name: str, title: str, body: str) -> str:
        """Create PR using custom method."""
        # Your PR creation logic
        return 'pr_url'
```

## Testing Interface

### Test Utilities

```python
class TestableGitHooksInstaller(GitHooksInstaller):
    """Test-friendly version of installer with mocking support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_git = False
        self.mock_github = False
    
    def enable_git_mocking(self):
        """Enable Git operation mocking for tests."""
        self.mock_git = True
    
    def enable_github_mocking(self):
        """Enable GitHub API mocking for tests."""
        self.mock_github = True
```

### Test Fixtures

```python
@pytest.fixture
def mock_repository(tmp_path):
    """Create mock Git repository for testing."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    # Initialize Git repository
    subprocess.run(['git', 'init'], cwd=repo_path, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True)
    
    return repo_path
```

This API reference provides comprehensive technical documentation for developers working with or extending the Git Hooks Installer.