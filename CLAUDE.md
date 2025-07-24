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

# Run installer tests to verify git hooks installation
./run_installer-tests.sh

# Installer test results are saved in tests/installer-results/
# Format: YYYY-MM-DD-NNN-{OS}-{TEST_TYPE}
# Example: 2025-01-24-001-ubuntu-initial
# Latest test folder name is in: tests/installer-results/latest-run-foldername.info
```

### Installation
```bash
# Install git hooks into a target repository
python git-hooks-installer/git-hooks-installer.py /path/to/target/repo

# For developers to set up hooks manually
python git-hooks-installer/developer-setup/setup_githooks.py
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
   - Orchestrates the entire installation process
   - Creates feature branches for automated installations (format: `feat/install-githooks-<timestamp>`)
   - Installs hooks, scripts, docs, developer-setup files, and CI/CD configs
   - Tracks versions via `docs/githooks/.githooks-version.json`
   - Uses hash-based change detection to minimize unnecessary updates

2. **Developer Setup** (`git-hooks-installer/developer-setup/`)
   - **Critical**: This folder MUST be copied to target repositories
   - Contains setup scripts for developers to manually install hooks
   - Includes `setup_githooks.py` for interactive configuration
   - Platform-specific scripts: `setup-githooks.sh` (Linux/macOS) and `.ps1` (Windows)

3. **Git Hooks** (`git-hooks-installer/git-hooks/`)
   - `post-commit`: Triggers documentation generation after commits
   - Uses lock files to prevent recursive execution
   - Generates logs in `docs/commit-logs/<branch>/`

4. **Supporting Scripts** (`git-hooks-installer/scripts/post-commit/`)
   - `generate_git_timeline.py`: Creates comprehensive timeline reports
   - `update-readme.sh`: Updates branch-specific READMEs
   - `githooks_utils.py`: Shared utilities for Git operations

5. **Code Style Tutorials** (Under Development)
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