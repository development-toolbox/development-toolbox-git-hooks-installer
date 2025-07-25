# Git Hooks Installer - Security-First Implementation

This is a **secure git hooks installer** that automates commit logging and documentation while maintaining comprehensive security guarantees. It implements User Story-driven requirements and requires manual review via pull requests.

---

## ✅ Overview

The secure git hooks installer provides automated commit logging with safety-first approach:

- **Security-first**: Comprehensive validation and secure subprocess operations
- **PR-only workflow**: Never auto-merges, always requires manual review  
- **File tracking**: Only commits installer-created files, never user secrets
- **Repository validation**: Pre-flight checks ensure repository is ready
- **User Story driven**: Implements business requirements (US-001 through US-005)

### 🔒 Security Guarantees

- ✅ Never commits user files or secrets
- ✅ Always requires PR review (no auto-merge)
- ✅ Validates repository state before operations
- ✅ Tracks only installer-created files
- ✅ Fails safely with clear error messages

---

## 🏗️ Architecture

### Core Components

1. **Main Installer** (`git-hooks-installer.py`)
   - Security-first implementation with comprehensive safety checks
   - Creates timestamped feature branches: `feat/safe-githooks-installation-<timestamp>`
   - Implements User Story-driven requirements (US-001 through US-005)

2. **Security Package** (`security/`)
   - `secure_git_wrapper.py`: Secure subprocess wrapper with command whitelisting
   - `file_tracker.py`: Tracks installer-created files for safe commits
   - `repository_validator.py`: Pre-flight safety validations
   - `__init__.py`: Clean package imports

3. **Utilities Package** (`utils/`)
   - `commit_file.py`: Commit processing utilities
   - `debug_commit_log.py`: Debug and logging helpers
   - `manage_gitignore.py`: Gitignore management utilities

4. **Archived Components** (`archived/`)
   - Legacy installer versions for reference
   - **Do not use**: These are kept for historical reference only

---

## 🚀 Installation

### Quick Start
```bash
# Install git hooks with security validation and PR workflow
python git-hooks-installer.py /path/to/target/repo

# Or with source directory specified
python git-hooks-installer.py --source /path/to/source /path/to/target/repo
```

### For Developers
```bash
# Manual setup for developers (no PR required)
python developer-setup/setup_githooks.py
```

---

## 🔧 Package Structure

The installer follows Python packaging standards:

```python
# Package-level imports (recommended)
from security import SecureGitWrapper, SafeFileTracker, RepositoryValidator

# Individual module imports
from security.secure_git_wrapper import SecureGitWrapper, SecureGitError
from security.file_tracker import SafeFileTracker
from security.repository_validator import RepositoryValidator
```

---

## 🧪 Testing

### Docker-based Testing
```bash
# Run comprehensive security tests across multiple OS
./run_docker-tests.sh

# Run User Story validation tests
docker-compose -f tests/docker/docker-compose.user-story-tests.yml up --build --abort-on-container-exit
```

### User Story Tests
The installer validates against 5 key User Stories:
- **US-001**: Safe installation for developers with secrets
- **US-002**: Team lead code quality control via PR workflow
- **US-003**: Developer work-in-progress protection  
- **US-004**: Cross-platform developer setup
- **US-005**: Repository administrator branch protection

---

## 🛡️ Security Features

### SecureGitWrapper
- **Command whitelisting**: Only approved Git commands allowed
- **Argument validation**: Each command has whitelisted allowed arguments
- **Path sanitization**: Prevents path traversal attacks
- **Branch name validation**: Prevents injection via malicious branch names
- **Timeout protection**: 30-second timeout prevents hanging operations

### File Tracking System
- **Explicit tracking**: Only installer-created files are committed
- **Staging validation**: Ensures only tracked files are staged
- **Manifest generation**: Complete audit trail for all operations
- **Safety checks**: Pre-commit validation of file contents

### Repository Validation
- **Working tree checks**: Ensures clean repository state
- **Branch validation**: Prevents conflicts with existing branches
- **Remote validation**: Checks for proper remote configuration
- **Pre-flight safety**: Comprehensive validation before any operations

---

## 📋 Workflow

1. **Pre-flight Checks**: Validates repository state and requirements
2. **Feature Branch**: Creates timestamped branch for installation
3. **Safe Installation**: Installs components with comprehensive tracking
4. **Commit & Push**: Commits only tracked files with detailed messages
5. **PR Generation**: Provides instructions for manual review process

---

## 🔗 Integration

### CI/CD Support
- Automatically detects GitHub Actions / GitLab CI
- Installs appropriate workflow files
- Maintains compatibility across platforms

### Cross-Platform
- **Linux/macOS**: Shell wrapper scripts (`setup-githooks.sh`)
- **Windows**: PowerShell scripts (`setup-githooks.ps1`)
- **Docker**: Multi-OS testing (Ubuntu, AlmaLinux 9/10)

---

## 📖 Documentation

- **Security Implementation**: See `SECURITY-ENHANCEMENTS.md` for complete security details
- **Framework Guide**: `docs/SECURITY-IMPLEMENTATION-FRAMEWORK.md` for reusable patterns
- **Project Memory**: `../CLAUDE.md` for development context

---

## 🤝 Contributing

1. Follow **Conventional Commits** standard for all commits
2. Use the safe installer for any hook-related changes  
3. All changes require PR review (no direct commits to main)
4. Run tests before submitting: `./run_docker-tests.sh`

### Commit Message Format
```
<type>(scope): <description>

Examples:
feat(security): add path validation to SecureGitWrapper
fix(installer): resolve branch creation issue
docs(readme): update installation instructions
```

---

## ✅ Maintained by

- **Johan Sörell**  
- **GitHub:** [J-SirL](https://github.com/J-SirL)  
- **LinkedIn:** [Johan Sörell](https://se.linkedin.com/in/johansorell)  

This secure git hooks installer is part of the [development-toolbox](https://github.com/development-toolbox/development-toolbox-git-hooks-installer) ecosystem.