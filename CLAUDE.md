# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Git hooks installer system that automates commit logging and documentation. Installs post-commit hooks to generate detailed commit logs, timelines, and maintains documentation following Conventional Commits standards. 

**Security-Hardened (v1.1.0):** Features comprehensive security controls including command injection prevention, path traversal protection, race condition mitigation, and resource exhaustion safeguards. PR-only workflow with mandatory manual review.

## Commands

### Testing
```bash
# Run Docker-based multi-OS tests (Ubuntu 22.04, AlmaLinux 9, AlmaLinux 10)
./run_docker-tests.sh

# Run User Story validation tests for safe installer
docker-compose -f tests/docker/docker-compose.user-story-tests.yml up --build --abort-on-container-exit

# Test --check functionality
docker-compose -f tests/docker/docker-compose.check-tests.yml up --build --abort-on-container-exit

# Test all program options
docker-compose -f tests/docker/docker-compose.options-tests.yml up --build --abort-on-container-exit

# Test results are saved to tests/results/{OS_NAME}/

# Security Testing (NEW v1.1.0)
pytest tests/security/ -v --tb=short           # Run security unit tests
bandit -r git-hooks-installer/ -f json        # Static security analysis  
safety check --json                           # Vulnerability scanning
bash tests/security/run_penetration_tests.sh  # Penetration testing
```

### Installation
```bash
# Main installer with security validation and PR workflow
python git-hooks-installer/git-hooks-installer.py [target-repo]

# Check installation status
python git-hooks-installer/git-hooks-installer.py -c

# Options:
# -f, --force    Force reinstall even if up-to-date
# -v, --verbose  Enable verbose logging
# -d, --debug    Enable debug logging
# --no-ci        Skip CI/CD file installation
# -c, --check    Check current installation status

# Manual developer setup (bypasses PR workflow)
python git-hooks-installer/developer-setup/setup_githooks.py
```

### Code Quality
```bash
# Run individual linters (configured in setup.cfg)
black git-hooks-installer/
isort git-hooks-installer/
ruff git-hooks-installer/
flake8 git-hooks-installer/  # max-line-length: 100
pylint git-hooks-installer/  # max-line-length: 100
mypy git-hooks-installer/
bandit git-hooks-installer/

# Run pytest
pytest --maxfail=1 --disable-warnings --tb=short git-hooks-installer/
```

## High-Level Architecture

### Core Components

1. **Main Installer** (`git-hooks-installer/git-hooks-installer.py`)
   - Auto-detects source location using `Path(__file__).parent`
   - Creates feature branches: `feat/safe-githooks-installation-<timestamp>`
   - PR-only workflow, never auto-merges
   - Uses FileTracker class for secure file management
   - Implements User Stories US-001 through US-005

2. **Security Package** (`git-hooks-installer/security/`) - **HARDENED v1.1.0**
   - `secure_git_wrapper.py`: Command whitelisting, argument validation, timeout protection, shell injection prevention
   - `file_tracker.py`: FileTracker class with atomic operations, file locking, resource limits (1000 files, 100MB max)
   - `repository_validator.py`: Pre-flight validation with sensitive file detection, path traversal prevention
   - All subprocess calls secured with `shell=False`, timeouts, and sanitized error handling

3. **Developer Setup** (`git-hooks-installer/developer-setup/`)
   - Must be copied to target repositories
   - Contains manual setup scripts for developers
   - Platform-specific: `.sh` (Linux/macOS), `.ps1` (Windows)

4. **Git Hooks** (`git-hooks-installer/git-hooks/`)
   - `post-commit`: Generates documentation after commits
   - Uses lock files to prevent recursive execution
   - Outputs to `docs/commit-logs/<branch>/`

5. **Test Infrastructure** (`tests/`)
   - Docker-based multi-OS validation
   - User Story tests validate business requirements
   - Results saved to `tests/results/` with complete logging

### Security Implementation

**SecureGitWrapper Features:**
- Command whitelisting (only approved Git commands)
- Argument validation per command
- Path sanitization (prevents traversal attacks)
- Branch name validation
- 30-second timeout protection
- `shell=False` enforced
- `GIT_TERMINAL_PROMPT=0` to prevent hangs

**User Story Requirements:**
- US-001: Safe installation for developers with secrets
- US-002: Team lead code quality control via PR workflow
- US-003: Developer work-in-progress protection
- US-004: Cross-platform developer setup
- US-005: Repository administrator branch protection

### Git Workflow

```
main (protected, PR-only)
  └── development (active integration)
       ├── feature/* (created from development)
       ├── bugfix/* (bug fixes)
       └── docs/* (documentation only)
```

**Commit Convention:**
```
type(scope): description

Types: feat, fix, docs, test, refactor, style, chore
Example: feat(installer): add repository validation
```

**Critical:** Never use `--auto-merge` flag (security risk)

### Installation Flow

1. Validates repository state
2. Creates feature branch (automated installations only)
3. Copies hooks to `.git/hooks/`
4. Installs developer-setup files to repository root
5. Updates .gitignore
6. Installs CI/CD files if detected
7. Commits tracked files only
8. Provides PR creation instructions

### Security Features (v1.1.0)

**Critical Security Fixes Applied:**
- ✅ Command injection prevention (branch name validation: `^[a-zA-Z0-9/_.-]+$`)
- ✅ Path traversal protection (realpath validation, directory containment)
- ✅ Race condition mitigation (file locking with fcntl, atomic operations)
- ✅ Resource exhaustion protection (file limits: 1000 files, 100MB total)
- ✅ Information disclosure prevention (sanitized error messages)
- ✅ Input validation framework (email, branch names, commit hashes)

**Security Score:** 9/10 (85% improvement from previous version)

### Important Notes

- Python 3.12+ required
- **Security:** All git operations use SecureGitWrapper with command validation
- **Resource Limits:** 1000 files max, 100MB total, 30-second timeouts
- FileTracker ensures only installer files are committed
- Never overwrites user files or commits sensitive data
- All security vulnerabilities documented in `SECURITY-CHANGELOG.md`
- Legacy installers archived in `git-hooks-installer/archived/`

### Security Documentation

- `SECURITY-CHANGELOG.md`: Complete vulnerability fixes and impact assessment
- `SYSTEM-ARCHITECTURE.md`: Security architecture and threat model coverage  
- `SECURITY-IMPLEMENTATION.md`: Detailed security implementation guide
- `SECURITY-TESTING-GUIDE.md`: Comprehensive security testing procedures