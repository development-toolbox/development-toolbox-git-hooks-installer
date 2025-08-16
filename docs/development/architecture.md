# Architecture Documentation

Technical architecture and design documentation for the Git Hooks Installer.

## System Overview

The Git Hooks Installer is a security-first, modular system designed to safely install and manage git hooks across development teams. It implements a defense-in-depth security model with multiple validation layers and fail-safe mechanisms.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│  • Command Line Interface (CLI)                            │
│  • Interactive Setup Wizards                               │
│  • Environment Variable Configuration                       │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                  Application Logic Layer                    │
│  • GitHooksInstaller (Main Orchestrator)                   │
│  • Installation Flow Management                            │
│  • Error Handling and Recovery                             │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   Security Layer                           │
│  • RepositoryValidator                                      │
│  • SecureGitWrapper                                         │
│  • FileTracker                                             │
│  • Input Validation & Sanitization                         │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                 External Services Layer                     │
│  • GitHub API Integration                                   │
│  • GitHub CLI Integration                                   │
│  • Git Operations                                           │
│  • File System Operations                                   │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Core Components

#### 1. GitHooksInstaller (Main Orchestrator)

**Responsibility:** Central coordination of the installation process

**Key Features:**
- Orchestrates the complete installation workflow
- Manages state transitions and error recovery
- Coordinates between security, validation, and integration components
- Implements the PR-only workflow with automatic branch management

**Design Patterns:**
- **Facade Pattern**: Provides simplified interface to complex subsystems
- **Template Method**: Defines installation workflow skeleton
- **State Machine**: Manages installation phases and transitions

```python
class GitHooksInstaller:
    """Main installer class implementing the Facade pattern."""
    
    def __init__(self, target_repo, source_dir, force=False, no_ci=False):
        self.target_repo = target_repo
        self.validator = RepositoryValidator(target_repo)
        self.file_tracker = FileTracker(target_repo)
        self.git = SecureGitWrapper(target_repo)
        
    def install(self) -> bool:
        """Template method defining installation workflow."""
        return (
            self.pre_flight_checks() and
            self.create_safe_feature_branch() and
            self.install_components() and
            self.commit_and_push() and
            self.create_pull_request() and
            self.restore_original_branch()
        )
```

#### 2. Security Layer Components

##### RepositoryValidator

**Responsibility:** Pre-flight validation and safety checks

**Security Functions:**
- Repository structure validation
- Working tree cleanliness verification
- Sensitive file detection
- Branch conflict prevention
- Resource limit enforcement

**Design Patterns:**
- **Strategy Pattern**: Different validation strategies for different repository types
- **Chain of Responsibility**: Sequential validation checks

```python
class RepositoryValidator:
    """Implements Chain of Responsibility for validation."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.validation_chain = [
            self._validate_git_repository,
            self._validate_working_tree,
            self._validate_remote_origin,
            self._detect_sensitive_files,
            self._validate_branch_availability
        ]
    
    def validate_all(self, branch_name: str) -> bool:
        """Execute validation chain."""
        for validator in self.validation_chain:
            if not validator():
                return False
        return True
```

##### SecureGitWrapper

**Responsibility:** Secure Git operation execution

**Security Features:**
- Command whitelisting (only approved Git commands)
- Argument validation and sanitization
- Path traversal protection
- Timeout enforcement
- Shell injection prevention

**Design Patterns:**
- **Proxy Pattern**: Secure proxy for Git operations
- **Command Pattern**: Encapsulates Git commands with validation

```python
class SecureGitWrapper:
    """Secure proxy for Git operations."""
    
    ALLOWED_COMMANDS = ['status', 'branch', 'checkout', 'add', 'commit', 'push']
    TIMEOUT = 30
    
    def run(self, command: str, *args) -> subprocess.CompletedProcess:
        """Execute Git command with security controls."""
        if command not in self.ALLOWED_COMMANDS:
            raise SecureGitError(f"Command not allowed: {command}")
        
        validated_args = [self._validate_arg(arg) for arg in args]
        
        return subprocess.run(
            ['git', command] + validated_args,
            shell=False,  # Prevent shell injection
            timeout=self.TIMEOUT,
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
```

##### FileTracker

**Responsibility:** Track and manage installer-created files

**Key Features:**
- Atomic file operations with locking
- Resource limit enforcement (files, size, directories)
- Safe Git staging area management
- Installation manifest generation

**Design Patterns:**
- **Observer Pattern**: Tracks file system changes
- **Memento Pattern**: Creates installation manifests for rollback

```python
class FileTracker:
    """Tracks file changes with atomic operations."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.created_files = []
        self.lock_file = repo_path / ".git" / "installer.lock"
    
    def track_file_creation(self, file_path: str, category: str):
        """Track file creation with atomic locking."""
        with self._acquire_lock():
            self._validate_resource_limits()
            self.created_files.append((file_path, category))
            self._update_manifest()
```

### Integration Components

#### GitHub Integration

**Responsibility:** GitHub API and CLI integration for PR management

**Features:**
- Automatic PR creation using GitHub API or CLI
- Authentication method detection and setup
- Interactive authentication configuration
- Error handling and fallback mechanisms

**Design Patterns:**
- **Adapter Pattern**: Adapts different GitHub authentication methods
- **Factory Pattern**: Creates appropriate GitHub clients

```python
class GitHubIntegration:
    """Factory for GitHub clients."""
    
    @staticmethod
    def create_client(auth_method: str, credentials: str):
        if auth_method == 'token':
            return GitHubAPIClient(credentials)
        elif auth_method == 'gh':
            return GitHubCLIClient()
        else:
            raise AuthenticationError("No valid authentication method")

class GitHubAPIClient:
    """GitHub API client using token authentication."""
    
    def create_pull_request(self, title: str, body: str, head: str, base: str):
        """Create PR using GitHub API."""
        # Implementation using urllib.request

class GitHubCLIClient:
    """GitHub CLI client wrapper."""
    
    def create_pull_request(self, title: str, body: str, head: str, base: str):
        """Create PR using gh CLI."""
        # Implementation using subprocess
```

## Security Architecture

### Defense in Depth Model

The installer implements multiple security layers:

1. **Input Validation Layer**
   - Command-line argument validation
   - Environment variable sanitization
   - Path validation and normalization

2. **Repository Validation Layer**
   - Repository structure verification
   - Working tree state validation
   - Sensitive file detection

3. **Command Execution Layer**
   - Git command whitelisting
   - Argument validation
   - Shell injection prevention
   - Timeout enforcement

4. **File System Layer**
   - Atomic file operations
   - Resource limit enforcement
   - Path traversal protection

5. **Network Security Layer**
   - HTTPS enforcement
   - Token sanitization
   - Error message sanitization

### Threat Model Coverage

| Threat Category | Mitigation Strategy | Implementation |
|----------------|-------------------|----------------|
| Command Injection | Input validation + whitelisting | SecureGitWrapper |
| Path Traversal | Path normalization + containment | FileTracker |
| Resource Exhaustion | Limits + timeouts | FileTracker + SecureGitWrapper |
| Race Conditions | Atomic operations + locking | FileTracker |
| Information Disclosure | Error sanitization | All components |
| Privilege Escalation | Principle of least privilege | System design |

## Data Flow Architecture

### Installation Flow

```
User Input → Validation → Authentication → Installation → Commit → PR Creation → Cleanup
     ↓            ↓            ↓              ↓           ↓           ↓           ↓
CLI Args → Repository → GitHub → File → Git → GitHub → Branch
          Validator    Auth     Operations  Operations  API     Restoration
```

### Detailed Data Flow

1. **Input Processing**
   ```
   CLI Arguments → Argument Parser → Configuration Manager → Installer Instance
   ```

2. **Validation Phase**
   ```
   Repository Path → RepositoryValidator → Security Checks → Validation Result
   ```

3. **Authentication Phase**
   ```
   Environment Variables → GitHub Auth Detector → Interactive Setup → Auth Credentials
   ```

4. **Installation Phase**
   ```
   Source Files → File Filter → FileTracker → Destination Files
   ```

5. **Git Operations**
   ```
   File Changes → SecureGitWrapper → Git Commands → Repository State
   ```

6. **PR Creation**
   ```
   Branch Info → GitHub Integration → API/CLI Call → Pull Request
   ```

## Error Handling Architecture

### Error Hierarchy

```
GitHooksInstallerError (Base)
├── SecurityError
│   ├── SecureGitError
│   ├── FileTrackingError
│   └── ValidationError
├── RepositoryError
│   ├── InvalidRepositoryError
│   └── WorkingTreeError
├── AuthenticationError
│   ├── TokenError
│   └── CLIError
└── NetworkError
    ├── GitHubAPIError
    └── ConnectivityError
```

### Error Recovery Strategies

1. **Graceful Degradation**
   ```python
   def create_pull_request(self) -> bool:
       try:
           return self._create_pr_with_api()
       except AuthenticationError:
           try:
               return self._create_pr_with_cli()
           except CLIError:
               self._provide_manual_instructions()
               return False
   ```

2. **Atomic Rollback**
   ```python
   def install(self) -> bool:
       try:
           return self._perform_installation()
       except Exception as e:
           self.cleanup_on_failure()
           raise
   ```

3. **State Recovery**
   ```python
   def cleanup_on_failure(self):
       self._reset_git_state()
       self._remove_tracked_files()
       self._restore_original_branch()
   ```

## Performance Architecture

### Resource Management

1. **Memory Management**
   - Streaming file operations for large repositories
   - Lazy loading of components
   - Garbage collection of temporary objects

2. **CPU Optimization**
   - Parallel validation checks where safe
   - Efficient file filtering algorithms
   - Minimal subprocess overhead

3. **I/O Optimization**
   - Batch file operations
   - Atomic directory operations
   - Efficient Git command usage

### Performance Monitoring

```python
class PerformanceMonitor:
    """Monitor installer performance metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.phase_times = {}
        self.resource_usage = {}
    
    def start_phase(self, phase_name: str):
        self.phase_times[phase_name] = time.time()
    
    def end_phase(self, phase_name: str):
        duration = time.time() - self.phase_times[phase_name]
        logger.debug(f"Phase {phase_name} completed in {duration:.2f}s")
```

## Extension Architecture

### Plugin System Design

The installer is designed to support extensions through well-defined interfaces:

```python
class InstallerPlugin(ABC):
    """Base class for installer plugins."""
    
    @abstractmethod
    def pre_install_hook(self, context: InstallationContext) -> bool:
        """Called before installation begins."""
        pass
    
    @abstractmethod
    def post_install_hook(self, context: InstallationContext) -> bool:
        """Called after installation completes."""
        pass

class CustomValidator(RepositoryValidator):
    """Example custom validator plugin."""
    
    def validate_custom_rules(self) -> bool:
        """Add organization-specific validation rules."""
        return True
```

### Configuration Extension Points

1. **Custom File Filters**
   ```python
   def custom_exclude_filter(file_path: Path) -> bool:
       """Custom logic for excluding files."""
       return file_path.suffix in ['.secret', '.private']
   ```

2. **Custom Authentication**
   ```python
   class EnterpriseAuthenticator:
       """Enterprise-specific authentication."""
       
       def authenticate(self) -> Tuple[str, str]:
           # Custom enterprise auth logic
           return ('enterprise', 'credentials')
   ```

3. **Custom Validators**
   ```python
   class ComplianceValidator:
       """Compliance-specific validation rules."""
       
       def validate_compliance(self) -> bool:
           # Organization compliance checks
           return True
   ```

## Testing Architecture

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_installer.py
│   ├── test_security/
│   │   ├── test_git_wrapper.py
│   │   ├── test_file_tracker.py
│   │   └── test_validator.py
│   └── test_integration/
├── integration/             # Integration tests
│   ├── test_end_to_end.py
│   └── test_github_integration.py
├── security/               # Security-focused tests
│   ├── test_penetration.py
│   └── test_vulnerability_scanning.py
└── fixtures/               # Test fixtures and mock data
    ├── mock_repositories/
    └── test_configs/
```

### Test Patterns

1. **Dependency Injection for Testing**
   ```python
   class TestableInstaller(GitHooksInstaller):
       def __init__(self, mock_git=False, mock_github=False):
           super().__init__()
           if mock_git:
               self.git = MockGitWrapper()
           if mock_github:
               self.github = MockGitHubClient()
   ```

2. **Test Doubles**
   ```python
   class MockSecureGitWrapper:
       """Test double for SecureGitWrapper."""
       
       def __init__(self):
           self.commands_executed = []
       
       def run(self, command: str, *args):
           self.commands_executed.append((command, args))
           return MockCompletedProcess()
   ```

## Deployment Architecture

### Deployment Models

1. **Standalone Deployment**
   - Single Python script execution
   - Self-contained with minimal dependencies
   - Suitable for ad-hoc installations

2. **CI/CD Integration**
   - GitHub Actions workflow integration
   - Jenkins pipeline integration
   - GitLab CI integration

3. **Enterprise Deployment**
   - Centralized installer distribution
   - Configuration management integration
   - Monitoring and auditing

### Configuration Management

```python
class ConfigurationManager:
    """Manages configuration from multiple sources."""
    
    def __init__(self):
        self.config_sources = [
            EnvironmentVariableConfig(),
            DotEnvFileConfig(),
            GitConfigSource(),
            DefaultConfig()
        ]
    
    def get_config(self, key: str) -> Any:
        """Get configuration value with precedence."""
        for source in self.config_sources:
            if source.has_key(key):
                return source.get_value(key)
        raise ConfigurationError(f"Configuration key not found: {key}")
```

This architecture documentation provides a comprehensive technical overview of the Git Hooks Installer's design, enabling developers to understand, maintain, and extend the system effectively.