# Contributing Guide

Guidelines for contributing to the Git Hooks Installer project.

## Welcome Contributors

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or enhancing security, your contributions help make this tool better for everyone.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.12+** (recommended, minimum 3.9)
- **Git** (version 2.20+)
- **GitHub account** with SSH keys or personal access token
- **Code editor** with Python support
- **Testing tools** (pytest, coverage)

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone git@github.com:your-username/git-hooks-installer.git
   cd git-hooks-installer
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify Setup**
   ```bash
   # Run tests to ensure everything works
   pytest tests/
   
   # Run linting
   black --check git-hooks-installer/
   flake8 git-hooks-installer/
   mypy git-hooks-installer/
   ```

## Development Workflow

### Branch Strategy

We use a Git flow-inspired branching model:

```
main (protected, production-ready)
├── development (integration branch)
│   ├── feature/your-feature-name
│   ├── bugfix/issue-description
│   ├── security/security-fix-name
│   └── docs/documentation-update
```

### Creating a Feature Branch

```bash
# Start from development branch
git checkout development
git pull origin development

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Commit with conventional commits format
git add .
git commit -m "feat(component): add new functionality"

# Push branch
git push origin feature/your-feature-name
```

### Commit Message Format

We use [Conventional Commits](https://conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `security`: Security improvements
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add GitHub CLI authentication support
fix(security): prevent path traversal in file operations
docs(readme): update installation instructions
test(security): add penetration tests for command injection
security(git): implement command whitelisting
```

## Contributing Areas

### 1. Bug Fixes

#### Finding Bugs
- Check the [Issues](../../issues) page for reported bugs
- Look for issues labeled `bug`, `security`, or `help wanted`
- Test the installer in different environments to discover issues

#### Bug Fix Process
1. **Reproduce the Bug**
   ```bash
   # Create a test case that reproduces the issue
   python -m pytest tests/test_bug_reproduction.py::test_specific_bug -v
   ```

2. **Fix the Issue**
   - Write the minimal fix needed
   - Ensure fix doesn't introduce new vulnerabilities
   - Add or update tests to prevent regression

3. **Test Thoroughly**
   ```bash
   # Run full test suite
   pytest tests/ -v
   
   # Run security tests
   pytest tests/security/ -v
   
   # Test on multiple platforms (if applicable)
   ./run_docker-tests.sh
   ```

### 2. New Features

#### Feature Development Process

1. **Discuss First**
   - Open an issue to discuss the feature
   - Ensure it aligns with project goals
   - Get feedback from maintainers

2. **Design Document**
   - For significant features, create a design document
   - Include security considerations
   - Consider backward compatibility

3. **Implementation**
   - Follow existing code patterns
   - Maintain security-first approach
   - Include comprehensive tests

#### Feature Guidelines

- **Security First**: All features must maintain security guarantees
- **Backward Compatibility**: Avoid breaking existing functionality
- **Documentation**: Include documentation updates
- **Testing**: Comprehensive test coverage required

### 3. Security Improvements

Security contributions are especially welcome and receive priority review.

#### Security Focus Areas
- Input validation and sanitization
- Command injection prevention
- Path traversal protection
- Resource exhaustion protection
- Authentication security
- Error message sanitization

#### Security Contribution Process
1. **Security Review**
   - All security changes undergo thorough review
   - May require multiple reviewer approval
   - Security team involvement for significant changes

2. **Vulnerability Disclosure**
   - Report security vulnerabilities privately first
   - Use GitHub Security Advisories for coordination
   - Public disclosure after fix is available

### 4. Documentation

#### Documentation Types
- **User Documentation**: Installation, usage, troubleshooting
- **API Documentation**: Internal APIs and extension points
- **Architecture Documentation**: System design and security model
- **Contributing Documentation**: Development and contribution guides

#### Documentation Standards
- **Clear and Concise**: Write for your audience
- **Examples**: Include practical examples
- **Up-to-Date**: Keep documentation current with code changes
- **Accessible**: Use clear language and proper formatting

### 5. Testing

#### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Security Tests**: Penetration and vulnerability testing
- **End-to-End Tests**: Complete workflow testing

#### Writing Tests
```python
import pytest
from git_hooks_installer.security import SecureGitWrapper

class TestSecureGitWrapper:
    def test_command_whitelisting(self):
        """Test that only whitelisted commands are allowed."""
        wrapper = SecureGitWrapper("/fake/repo")
        
        # Should allow whitelisted commands
        assert wrapper._is_command_allowed("status")
        assert wrapper._is_command_allowed("commit")
        
        # Should reject non-whitelisted commands
        assert not wrapper._is_command_allowed("rm")
        assert not wrapper._is_command_allowed("format")
    
    def test_argument_validation(self):
        """Test argument validation prevents injection."""
        wrapper = SecureGitWrapper("/fake/repo")
        
        # Valid arguments should pass
        assert wrapper._validate_argument("main")
        assert wrapper._validate_argument("feature/test")
        
        # Invalid arguments should fail
        assert not wrapper._validate_argument("; rm -rf /")
        assert not wrapper._validate_argument("$(evil_command)")
```

## Code Quality Standards

### Code Style

We use automated code formatting and linting:

```bash
# Format code
black git-hooks-installer/
isort git-hooks-installer/

# Check style
flake8 git-hooks-installer/
pylint git-hooks-installer/

# Type checking
mypy git-hooks-installer/
```

### Configuration Files

**setup.cfg** (project configuration):
```ini
[flake8]
max-line-length = 100
exclude = __pycache__,venv,.git
ignore = E203,W503

[mypy]
python_version = 3.9
strict = True
ignore_missing_imports = True

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Security Standards

#### Secure Coding Practices
- **Input Validation**: Validate all user inputs
- **Sanitization**: Sanitize data before use
- **Least Privilege**: Use minimal required permissions
- **Defense in Depth**: Multiple security layers
- **Fail Securely**: Secure failure modes

#### Security Tools
```bash
# Static security analysis
bandit -r git-hooks-installer/ -f json

# Dependency vulnerability scanning
safety check --json

# Security testing
pytest tests/security/ -v
```

### Performance Standards

#### Performance Guidelines
- **Minimize Resource Usage**: Keep memory and CPU usage low
- **Efficient Algorithms**: Use appropriate data structures
- **Async Where Appropriate**: Use async for I/O operations
- **Resource Limits**: Implement and respect limits

#### Performance Testing
```bash
# Memory profiling
python -m memory_profiler git-hooks-installer.py

# Performance benchmarks
pytest tests/performance/ -v --benchmark-only
```

## Pull Request Process

### Before Submitting

1. **Code Quality Checks**
   ```bash
   # Run all linters and formatters
   black git-hooks-installer/
   isort git-hooks-installer/
   flake8 git-hooks-installer/
   pylint git-hooks-installer/
   mypy git-hooks-installer/
   
   # Run security tools
   bandit -r git-hooks-installer/
   safety check
   ```

2. **Test Coverage**
   ```bash
   # Run tests with coverage
   pytest tests/ --cov=git-hooks-installer --cov-report=html
   
   # Aim for >90% coverage for new code
   ```

3. **Documentation Updates**
   - Update relevant documentation
   - Include docstrings for new functions
   - Update API documentation if needed

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Security improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Security tests added/updated
- [ ] Manual testing completed

## Security Considerations
- [ ] No new security vulnerabilities introduced
- [ ] Security review completed (for security-related changes)
- [ ] Input validation added/updated
- [ ] Error handling reviewed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new linting errors
- [ ] Commit messages follow conventional format
```

### Review Process

1. **Automated Checks**
   - CI pipeline runs automatically
   - All tests must pass
   - Code quality checks must pass
   - Security scans must pass

2. **Peer Review**
   - At least one reviewer approval required
   - Security changes require security team review
   - Architecture changes require architect review

3. **Merge Requirements**
   - All CI checks passing
   - Required approvals obtained
   - No merge conflicts
   - Up-to-date with target branch

## Development Guidelines

### Architecture Principles

1. **Security First**
   - Every feature must maintain security guarantees
   - Use secure-by-design principles
   - Implement defense in depth

2. **Modularity**
   - Keep components loosely coupled
   - Use clear interfaces between modules
   - Enable easy testing and extension

3. **Reliability**
   - Handle errors gracefully
   - Implement proper cleanup
   - Provide clear error messages

### Design Patterns

We use established design patterns:

- **Facade Pattern**: Main installer class
- **Strategy Pattern**: Different authentication methods
- **Command Pattern**: Git operations
- **Observer Pattern**: File tracking
- **Factory Pattern**: Component creation

### Error Handling

```python
class SecureGitWrapper:
    def run(self, command: str, *args) -> subprocess.CompletedProcess:
        """Execute Git command with proper error handling."""
        try:
            self._validate_command(command, args)
            result = self._execute_command(command, args)
            return result
        except ValidationError as e:
            logger.error(f"Command validation failed: {e}")
            raise SecureGitError(f"Invalid command: {command}") from e
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {command}")
            raise SecureGitError(f"Command timed out: {command}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise SecureGitError(f"Command failed: {command}") from e
```

## Testing Guidelines

### Test Structure

```python
class TestFeature:
    """Test class for specific feature."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_repo = create_test_repository()
        self.installer = GitHooksInstaller(self.temp_repo)
    
    def test_normal_case(self):
        """Test normal successful operation."""
        result = self.installer.some_method()
        assert result is True
    
    def test_edge_case(self):
        """Test edge case handling."""
        # Test with edge case inputs
        pass
    
    def test_error_handling(self):
        """Test error condition handling."""
        with pytest.raises(ExpectedError):
            self.installer.some_method_that_should_fail()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        cleanup_test_repository(self.temp_repo)
```

### Security Testing

```python
class TestSecurity:
    """Security-focused tests."""
    
    def test_command_injection_prevention(self):
        """Test that command injection is prevented."""
        malicious_input = "; rm -rf /"
        wrapper = SecureGitWrapper("/fake/repo")
        
        with pytest.raises(SecureGitError):
            wrapper.run("status", malicious_input)
    
    def test_path_traversal_prevention(self):
        """Test that path traversal is prevented."""
        malicious_path = "../../../etc/passwd"
        tracker = FileTracker("/fake/repo")
        
        with pytest.raises(SecurityError):
            tracker.track_file_creation(malicious_path)
```

## Documentation Guidelines

### Docstring Format

We use Google-style docstrings:

```python
def complex_function(param1: str, param2: int = 0) -> bool:
    """Brief description of function.
    
    Longer description if needed, explaining the purpose and behavior
    of the function in more detail.
    
    Args:
        param1: Description of first parameter.
        param2: Description of second parameter with default value.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: Description of when this exception is raised.
        SecurityError: Description of security-related exceptions.
        
    Example:
        Basic usage example:
        
        >>> result = complex_function("test", 42)
        >>> assert result is True
    """
```

### API Documentation

For public APIs, include comprehensive documentation:

```python
class PublicAPI:
    """Public API class for extensions.
    
    This class provides a stable API for extending the installer
    functionality. All methods in this class are considered public
    API and maintain backward compatibility.
    
    Attributes:
        version: API version for compatibility checking.
        
    Example:
        Basic usage:
        
        >>> api = PublicAPI()
        >>> api.register_validator(custom_validator)
    """
```

## Release Process

### Version Management

We use semantic versioning (SemVer):
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Checklist

1. **Pre-Release**
   - [ ] All tests passing
   - [ ] Security scan clean
   - [ ] Documentation updated
   - [ ] Changelog updated
   - [ ] Version bumped

2. **Release**
   - [ ] Create release branch
   - [ ] Final testing
   - [ ] Create GitHub release
   - [ ] Update documentation
   - [ ] Notify users

3. **Post-Release**
   - [ ] Monitor for issues
   - [ ] Update dependencies
   - [ ] Plan next release

## Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

- **Be respectful**: Treat all community members with respect
- **Be inclusive**: Welcome contributors from all backgrounds
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Help newcomers learn and contribute

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions
- **Documentation**: In-repo documentation

### Getting Help

- **Documentation**: Check docs/ directory first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Use private disclosure for security issues

Thank you for contributing to the Git Hooks Installer! Your contributions help make development workflows more secure and efficient for everyone.