# Development Toolbox - Git Hooks Installer

A **git commit documentation automation system** that installs post-commit hooks to automatically generate detailed commit logs, timeline reports, and branch documentation after every commit. Features security-first installation with PR-only workflow and comprehensive safety validations.

[![Security](https://img.shields.io/badge/Security-First-green)](./git-hooks-installer/SECURITY-ENHANCEMENTS.md)
[![Testing](https://img.shields.io/badge/Testing-Multi--OS-blue)](./tests/)
[![Framework](https://img.shields.io/badge/Framework-Reusable-orange)](./docs/SECURITY-IMPLEMENTATION-FRAMEWORK.md)

---

## 🎯 Project Overview

This project provides a comprehensive git commit documentation automation system with three main components:

1. **📋 Post-Commit Documentation** - Automatically generates commit logs, timeline reports, and branch documentation after every commit
2. **🔒 PR-Only Installer** - Creates feature branch and requires manual review before merging
3. **🛡️ Reusable Security Framework** - For other projects requiring secure git operations

---

## 🚀 Quick Start

### Install Git Hooks
```bash
# Clone the repository
git clone https://github.com/development-toolbox/development-toolbox-git-hooks-installer.git
cd development-toolbox-git-hooks-installer

# Install commit documentation hooks
python git-hooks-installer/git-hooks-installer.py /path/to/your/project

# Help and options
python git-hooks-installer/git-hooks-installer.py -h
```

**Help Output:**
```
usage: git-hooks-installer.py [-h] [-f] [-v] [-d] [--no-ci] [-c] [target]

Install/update git hooks, scripts, and documentation in a Git repository.

positional arguments:
  target         Path to the target Git repository where hooks will be
                 installed (default: current directory)

options:
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

### Check Installation Status
```bash
# Check if git hooks are already installed
python git-hooks-installer/git-hooks-installer.py -c
# or use long flag
python git-hooks-installer/git-hooks-installer.py --check
```

### For Developers (Manual Setup)
```bash
# Direct setup without PR workflow
python git-hooks-installer/developer-setup/setup_githooks.py
```

---

## ✅ What It Does

- **Installs post-commit hooks** that automatically generate commit documentation
- **Creates feature branch** for installation (never commits directly to main)
- **Requires manual PR review** before changes are merged
- **Validates repository state** before installation
- **Only commits installer files** (never user files or secrets)

---

## 🏗️ Project Structure

```
📁 development-toolbox-git-hooks-installer/
├── 📄 README.md                          # This file
├── 📄 CLAUDE.md                          # Project memory
├── 📁 git-hooks-installer/               # Main installer package
│   ├── 📄 git-hooks-installer.py        # Security-first installer
│   ├── 📁 security/                     # Security framework
│   │   ├── 📄 secure_git_wrapper.py    # Secure subprocess wrapper
│   │   ├── 📄 file_tracker.py          # file tracking
│   │   └── 📄 repository_validator.py  # Pre-flight validation
│   ├── 📁 utils/                        # Utility functions
│   ├── 📁 developer-setup/              # Manual setup tools
│   └── 📁 archived/                     # Legacy versions
├── 📁 docs/                             # Documentation
│   ├── 📄 SECURITY-IMPLEMENTATION-FRAMEWORK.md  # Reusable patterns
│   └── 📁 commit-logs/                  # Generated commit logs
├── 📁 tests/                            # Multi-OS testing
│   ├── 📁 docker/                       # Docker configurations
│   ├── 📁 user-stories/                 # Business requirement tests
│   └── 📁 results/                      # Test results
└── 📁 code-style-tutorial/              # HTML tutorials (in development)
```

---

## 🧪 Testing & Validation

### Multi-OS Testing
```bash
# Run comprehensive security tests across Ubuntu, AlmaLinux 9/10
./run_docker-tests.sh

# Run User Story validation tests
docker-compose -f tests/docker/docker-compose.user-story-tests.yml up --build --abort-on-container-exit
```

### User Story Requirements
The installer validates against 5 key business requirements:
- **US-001**: Testing "safe" installation for developers with secrets
- **US-002**: Team lead code quality control via PR workflow
- **US-003**: Developer work-in-progress protection
- **US-004**: Cross-platform developer setup
- **US-005**: Repository administrator branch protection

---

## 🛡️ Security Framework

### Core Security Components

1. **SecureGitWrapper** (`security/secure_git_wrapper.py`)
   - Command whitelisting - only approved Git commands
   - Argument validation - prevents flag injection
   - Path sanitization - prevents traversal attacks
   - Timeout protection - prevents hanging operations

2. **FileTracker** (`security/file_tracker.py`)
   - Explicit file tracking - only installer files committed
   - Staging validation - ensures clean commits
   - Audit trails - comprehensive operation logging

3. **RepositoryValidator** (`security/repository_validator.py`)
   - Pre-flight checks - validates repository state
   - Branch validation - prevents conflicts
   - Working tree validation - ensures clean state

### Framework Usage
```python
# Import the security framework
from security import SecureGitWrapper, FileTracker, RepositoryValidator

# Use secure Git operations
git = SecureGitWrapper("/path/to/repo")
git.create_branch("feat/new-feature")  # Validated and secure
```

---

## 📋 What Gets Installed

When you run the installer, it sets up:

### 🪝 Git Hooks
- **post-commit**: Generates detailed commit logs automatically
- **lock files**: Prevents recursive execution
- **branch-specific**: Organizes logs by branch

### 📊 Documentation System
- **Conventional Commits**: Standardized commit message format
- **Automated logs**: Generated in `docs/commit-logs/`
- **Timeline reports**: Comprehensive project history
- **Branch tracking**: Separate logs per branch

### 🔧 Developer Tools
- **Cross-platform scripts**: Shell (Linux/macOS) and PowerShell (Windows)
- **Manual setup**: `developer-setup/setup_githooks.py`
- **CI/CD integration**: GitHub Actions and GitLab CI support

---

## 🔄 Workflow

### Automated Installation Process
1. **Pre-flight Checks** - Validates repository state and requirements
2. **Feature Branch** - Creates timestamped branch: `feat/githooks-installation-<timestamp>`
3. **Installation** - Installs components with comprehensive file tracking
4. **Commit & Push** - Commits only tracked files with detailed audit messages
5. **PR Instructions** - Provides platform-specific PR creation links
6. **Manual Review** - Team member reviews and approves changes

### After Installation
1. **Make commits** using Conventional Commits format
2. **Automatic documentation** generated after each commit
3. **Timeline reports** updated with project history
4. **Branch-specific logs** maintain clear audit trails

---

## 📖 Documentation

- **📋 Installation Guide**: [git-hooks-installer/README.md](./git-hooks-installer/README.md)
- **🔒 Security Details**: [git-hooks-installer/SECURITY-ENHANCEMENTS.md](./git-hooks-installer/SECURITY-ENHANCEMENTS.md)
- **🛡️ Framework Guide**: [docs/SECURITY-IMPLEMENTATION-FRAMEWORK.md](./docs/SECURITY-IMPLEMENTATION-FRAMEWORK.md)
- **💭 Project Memory**: [CLAUDE.md](./CLAUDE.md)
- **🧪 Test Results**: [tests/user-stories/USER-STORY-TEST-RESULTS.md](./tests/user-stories/USER-STORY-TEST-RESULTS.md)

---

## 📖 Conventional Commits

This project follows the **Conventional Commits** standard for clear, automated commit history.

### Commit Format
```
<type>(scope): <description>

Examples:
feat(installer): add secure subprocess wrapper
fix(security): resolve path validation issue
docs(readme): update installation instructions
test(user-stories): add US-001 validation test
```

### Commit Types
- **feat**: New features
- **fix**: Bug fixes
- **docs**: Documentation updates
- **test**: Testing improvements
- **refactor**: Code improvements
- **style**: Code style changes
- **chore**: Maintenance tasks

👉 **Learn more**: [conventionalcommits.org](https://www.conventionalcommits.org)

---

## 🤝 Contributing

1. **Follow Conventional Commits** standard for all commit messages
2. **Use the secure installer** for any hook-related changes
3. **All changes require PR review** - no direct commits to main
4. **Run tests before submitting**: `./run_docker-tests.sh`
5. **Update documentation** when adding features

### Development Setup
```bash
# Clone and setup
git clone https://github.com/development-toolbox/development-toolbox-git-hooks-installer.git
cd development-toolbox-git-hooks-installer

# Install hooks for this project
python git-hooks-installer/git-hooks-installer.py .

# Run tests
./run_docker-tests.sh
```

---

## 📦 Framework Reusability

The security framework can be used in other projects:

1. **Copy security package**: `security/` folder with all components
2. **Adapt imports**: `from security import SecureGitWrapper, FileTracker`
3. **Implement User Stories**: Define business requirements as testable stories
4. **Set up testing**: Docker-based multi-OS validation
5. **Documentation**: Use `SECURITY-ENHANCEMENTS.md` template

See [SECURITY-IMPLEMENTATION-FRAMEWORK.md](./docs/SECURITY-IMPLEMENTATION-FRAMEWORK.md) for complete implementation guide.

---

## ✅ Maintained by

- **Johan Sörell**
- **GitHub**: [J-SirL](https://github.com/J-SirL)
- **LinkedIn**: [Johan Sörell](https://se.linkedin.com/in/johansorell)

---

## 📄 License

This project is part of the [development-toolbox](https://github.com/development-toolbox) ecosystem.

**🔗 Repository**: https://github.com/development-toolbox/development-toolbox-git-hooks-installer