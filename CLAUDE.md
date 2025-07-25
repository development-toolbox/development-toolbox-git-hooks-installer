# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Git hooks installer system that automates commit logging and documentation. It installs post-commit hooks that generate detailed commit logs, timelines, and maintains documentation following Conventional Commits standards. The project also includes HTML-based code style tutorials under development.

## Commands

### Testing
```bash
# Run Docker-based code quality tests across multiple OS environments
./run_docker-tests.sh

# This runs tests on Ubuntu 22.04, AlmaLinux 9, and AlmaLinux 10
# Results are generated in tests/results/{OS_NAME}/

# Run User Story tests for safe installer validation
docker-compose -f tests/docker/docker-compose.user-story-tests.yml up --build --abort-on-container-exit

# Test --check functionality specifically
docker-compose -f tests/docker/docker-compose.check-tests.yml up --build --abort-on-container-exit

# Test all program options comprehensively
docker-compose -f tests/docker/docker-compose.options-tests.yml up --build --abort-on-container-exit

# All test results are saved to tests/results/ with proper logging
```

### Installation
```bash
# Main installer with security validation and PR workflow
python git-hooks-installer/git-hooks-installer.py [target-repo]

# Check installation status
python git-hooks-installer/git-hooks-installer.py -c

# All available options:
# -f, --force    Force reinstall even if up-to-date
# -v, --verbose  Enable verbose logging
# -d, --debug    Enable debug logging
# --no-ci        Skip CI/CD file installation
# -c, --check    Check current installation status

# For developers to set up hooks manually
python git-hooks-installer/developer-setup/setup_githooks.py

# Legacy installers are archived in git-hooks-installer/archived/
```

### Code Quality Tools
The project uses comprehensive Python linting configured in setup.cfg:
- **black**: Code formatter
- **isort**: Import sorting  
- **ruff**: Fast linter
- **flake8**: Style guide (max-line-length: 100)
- **pylint**: Static analysis (max-line-length: 100)
- **mypy**: Type checker
- **bandit**: Security linter

## High-Level Architecture

### Core Components

1. **Main Installer** (`git-hooks-installer/git-hooks-installer.py`)
   - Security-first implementation with comprehensive safety checks
   - **Auto-detects source**: No need for --source parameter, uses `Path(__file__).parent`
   - **PR-only workflow**: Never auto-merges, always requires manual review
   - **File tracking**: Only commits installer-created files via `security/file_tracker.py` (FileTracker class)
   - **Repository validation**: Pre-flight checks via `security/repository_validator.py`
   - **Secure Git operations**: Uses `security/secure_git_wrapper.py` for subprocess safety
   - **Consistent arguments**: All options have both short and long flags (-f/--force, -v/--verbose, etc.)
   - **Status checking**: Built-in --check/-c option to verify installation status
   - Creates timestamped feature branches: `feat/safe-githooks-installation-<timestamp>`
   - Implements User Story-driven requirements (US-001 through US-005)

2. **Developer Setup** (`git-hooks-installer/developer-setup/`)
   - **Critical**: This folder MUST be copied to target repositories
   - Contains setup scripts for developers to manually install hooks
   - Includes `setup_githooks.py` for interactive configuration
   - Platform-specific scripts: `setup-githooks.sh` (Linux/macOS) and `.ps1` (Windows)

3. **Security Package** (`git-hooks-installer/security/`)
   - `secure_git_wrapper.py`: Secure subprocess wrapper with command whitelisting
   - `file_tracker.py`: Tracks installer-created files for validated commits (FileTracker class)
   - `repository_validator.py`: Pre-flight repository validations
   - **Security features**: Path sanitization, branch name validation, timeout protection
   - **Bandit compliance**: All subprocess calls validated and marked with `# nosec B602`
   - **Python package**: Proper `__init__.py` with clean imports

4. **Utilities Package** (`git-hooks-installer/utils/`)
   - `commit_file.py`: Commit processing utilities
   - `debug_commit_log.py`: Debug and logging helpers
   - `manage_gitignore.py`: Gitignore management utilities
   - **Python package**: Organized utility functions

5. **Archived Components** (`git-hooks-installer/archived/`)
   - Legacy installer versions for reference
   - Obsolete files moved here for potential cleanup
   - **Do not use**: These are kept for historical reference only

6. **Git Hooks** (`git-hooks-installer/git-hooks/`)
   - `post-commit`: Triggers documentation generation after commits
   - Uses lock files to prevent recursive execution
   - Generates logs in `docs/commit-logs/<branch>/`

7. **Supporting Scripts** (`git-hooks-installer/scripts/post-commit/`)
   - `generate_git_timeline.py`: Creates comprehensive timeline reports
   - `update-readme.sh`: Updates branch-specific READMEs
   - `githooks_utils.py`: Shared utilities for Git operations

8. **User Story Tests** (`tests/user-stories/`)
   - Docker-based User Story test suite
   - Validates safe installer against business requirements
   - Tests all User Stories (US-001 through US-005)
   - Results documented in `tests/user-stories/USER-STORY-TEST-RESULTS.md`

9. **Comprehensive Test Suite** (`tests/`)
   - **Option Testing**: `test-all-program-options.sh` validates all command-line arguments
   - **Check Functionality**: `test-check-functionality.sh` tests status checking features
   - **Docker Compose**: Multiple test environments (check-tests, options-tests, user-story-tests)
   - **Proper Logging**: All test results saved to `tests/results/` with complete logs
   - **Multi-OS Support**: Validates functionality across Ubuntu and AlmaLinux distributions

10. **Code Style Tutorials** (Under Development)
   - `code-style-tutorial/`: HTML-based tutorial pages for code style best practices
     - Includes guides for black, imports, and various tips
     - Subdirectories for specific tools (black/, tips/)
   - `code-style-examples/`: HTML examples demonstrating code style issues
     - Examples for indentation, long lines, trailing whitespace
   - Will be served via nginx Docker container (planned)

### Important Workflows

1. **Installation Flow**
   - Validates target repository and checks for uncommitted changes
   - Creates feature branch for installation (only for automated installations)
   - Copies hooks to `.git/hooks/` (not tracked by Git)
   - **Installs developer-setup files to repository root**
   - Copies scripts and documentation
   - Updates .gitignore with required patterns
   - Installs CI/CD files if GitHub/GitLab detected
   - Commits all changes with detailed message

2. **Testing Flow**
   - Docker Compose orchestrates multi-OS testing
   - Each OS (Ubuntu, AlmaLinux 9/10) runs the full test suite
   - Results saved to `tests/results/{OS_NAME}/`
   - Generates both text and HTML reports for each tool

3. **Post-Commit Documentation Flow**
   - Hook captures commit metadata and changed files
   - Generates individual commit log files
   - Updates Git timeline reports
   - Auto-commits documentation (configurable auto-push)

### Todo Management System

The project uses a structured todo folder system for task tracking:

1. **Creating Tasks**: When AI is asked to create something, it should be documented in the `todo/` folder with:
   - Date of task creation
   - Detailed task description
   - Current status

2. **Task Completion**: Tasks remain in the todo folder until the user explicitly confirms completion
   - Only move to done folder when user confirms "it's done"
   - If user doesn't confirm completion, task stays pending

3. **Structure**:
   - `todo/`: Active tasks and work in progress
   - `todo/done/`: Completed tasks (only moved here with user confirmation)

### Key Design Principles

- **Never overwrites user files**: Uses manifest tracking to manage files safely
- **Multi-OS support**: Tested on Ubuntu and AlmaLinux distributions
- **Developer-friendly**: Provides both automated and manual setup options
- **Version-aware**: Only updates when source files actually change
- **CI/CD ready**: Auto-detects and integrates with GitHub Actions/GitLab CI

## Git Workflow

This project follows a structured git flow for safer development:

### Branch Structure
- **`main`**: Production-ready code only (protected, PR-only)
- **`development`**: Active development integration branch
- **`feature/*`**: Created from development, merged back via PR
- **`bugfix/*`**: Bug fixes, merged to development (or main for hotfixes)
- **`docs/*`**: Documentation-only changes

### Workflow
1. Create feature branches from `development`
2. Make changes with conventional commits: `type(scope): description`
3. Submit PR from feature branch to `development`
4. After review and testing, merge to `development`
5. When stable, create PR from `development` to `main`

### Important Notes
- **NEVER commit directly to main**
- **NEVER use `--auto-merge` flag** (security risk - see analysis folder)
- Always create PRs for code review
- Use conventional commit format with proper scopes

See `docs/git-workflow.md` for complete workflow documentation.

## Security Implementation

The project implements comprehensive security measures through the safe installer:

### SecureGitWrapper Security Features
1. **Command Whitelisting**: Only approved Git commands can be executed
2. **Argument Validation**: Each command has whitelisted allowed arguments  
3. **Path Sanitization**: All file paths validated to prevent traversal attacks
4. **Branch Name Validation**: Prevents injection via malicious branch names
5. **Timeout Protection**: 30-second timeout prevents hanging operations
6. **No Shell Execution**: `shell=False` enforced, prevents shell injection
7. **Git Prompt Disabled**: Sets `GIT_TERMINAL_PROMPT=0` to prevent hangs

### User Story Requirements
- **US-001**: Safe installation for developers with secrets
- **US-002**: Team lead code quality control via PR workflow
- **US-003**: Developer work-in-progress protection
- **US-004**: Cross-platform developer setup
- **US-005**: Repository administrator branch protection

### Security Documentation
- Complete security implementation documented in `git-hooks-installer/SECURITY-ENHANCEMENTS.md`
- All Bandit security warnings addressed with proper `# nosec B602` annotations
- User Story test results documented in `tests/user-stories/USER-STORY-TEST-RESULTS.md`

## Recent Improvements (2025-07-25)

### Simplified Installer Interface
- **Removed --source parameter**: Installer now auto-detects its location using `Path(__file__).parent`
- **Clearer target parameter**: Users only specify WHERE to install hooks, not WHERE to install FROM
- **Consistent argument flags**: All options now have both short and long versions:
  - `-f, --force` (Force reinstall)
  - `-v, --verbose` (Verbose logging)
  - `-d, --debug` (Debug logging)
  - `-c, --check` (Check installation status)
  - `--no-ci` (Skip CI/CD files)

### Enhanced Testing Infrastructure
- **Comprehensive option testing**: `test-all-program-options.sh` validates all command-line arguments
- **Status checking tests**: `test-check-functionality.sh` validates --check functionality
- **Proper test logging**: All test results saved to `tests/results/` with complete logs
- **Multiple test environments**: Separate Docker Compose files for different test types

### Improved User Experience
- **Help with examples**: Built-in usage examples in help output
- **Status checking**: New --check/-c option shows detailed installation status
- **Auto-detection**: No more confusing source directory parameter
- **Better error messages**: Clear feedback on what's installed vs missing

## Development Notes

- Python 3.12 required
- Always run tests via `./run_docker-tests.sh` for multi-OS validation
- The `developer-setup` folder is essential - it must be installed in target repos
- Test dependencies in `tests/requirements.txt`
- Configuration in `setup.cfg` and `pytest.ini`
- Feature branches are created automatically only during git hooks installation
- Code style tutorials are being developed and will be served via nginx container
- **Docker Compose**: Never use `version:` field in docker-compose.yml files - it's deprecated
- **Installer Testing**: Test results organized by date and run number in `tests/installer-results/`
- **Security**: Use main installer (`git-hooks-installer.py`) for production deployments