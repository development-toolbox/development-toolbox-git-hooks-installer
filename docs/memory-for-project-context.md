# Project Memory - Development Toolbox Git Hooks Installer

Copy each section below into separate `<user-memory-input>` tags:

## Section 1: Project Overview and Critical Security Issues
```
<user-memory-input>
Development Toolbox Git Hooks Installer Project:
- Main installer: git-hooks-installer/git-hooks-installer.py (has security vulnerabilities)
- CRITICAL SECURITY ISSUE: --auto-merge flag is dangerous (auto-commits user files, bypasses PR review)
- Safe implementation exists: git-hooks-installer-fixed.py (but still needs improvements)
- Uses Python 3.12, conventional commits, hash-based change detection for updates
- Post-commit hooks automatically generate docs/commit-logs/ with commit documentation
- Developer setup folder MUST be copied to target repositories for manual hook installation
- Testing via Docker multi-OS environments: ./run_docker-tests.sh for validation
- Repository currently on development branch workflow for safer collaboration
</user-memory-input>
```

## Section 2: Project Structure and Key Components
```
<user-memory-input>
Git Hooks Installer Project Structure:
- git-hooks-installer/ - Main installer code and components
- git-hooks-installer/developer-setup/ - CRITICAL: Must be copied to target repos
- git-hooks-installer/git-hooks/ - Hook scripts (post-commit for documentation)
- git-hooks-installer/scripts/post-commit/ - Timeline generation and utilities
- tests/docker/ - Multi-OS testing environments (Ubuntu, AlmaLinux)
- tests/installer-results/ - Test output and validation results
- todo/ - Task tracking with markdown files
- todo/analysis/ - Complex issue analysis folders
- docs/ - Project documentation and workflow guides
- commit/ - Commit messages in markdown format
- code-style-tutorial/ - HTML tutorials for code style (nginx served)
- CLAUDE.md - AI instance context and architecture documentation
</user-memory-input>
```

## Section 3: Dangerous Auto-Merge Behavior (Critical Security Analysis)
```
<user-memory-input>
Critical Security Vulnerability in Git Hooks Installer:
- Auto-merge functionality bypasses code review and directly merges to main branch
- Auto-commits ANY uncommitted files including .env, secrets, work-in-progress
- Uses git add without user consent (essentially git add . behavior)
- Risk scenarios: API keys committed, passwords exposed, incomplete work merged
- Analysis completed in: todo/analysis/git-hooks-installer-safety-2025-07-24/
- Mermaid diagrams show dangerous vs safe code paths with visual color coding
- NEVER use --auto-merge flag until safe implementation completed
- Safe implementation requires: repository validation, file tracking, PR-only workflow
- Testing showed functional success in clean Docker environment but would fail with real user repositories
</user-memory-input>
```

## Section 4: Safe Implementation Requirements
```
<user-memory-input>
Git Hooks Installer Safe Implementation Requirements:
- Repository clean state validation before any operations (reject dirty repos)
- File tracking system to only commit installer-created files, never user files
- PR-only workflow - never merge directly to main branch
- Comprehensive security testing: secret protection, WIP protection, dirty repo protection
- Multi-OS Docker testing environments for validation
- Shell wrapper scripts for cross-platform developer setup
- Version tracking via docs/githooks/.githooks-version.json
- Proper error handling and rollback on failures
- Branch protection rules and mandatory code review
- User consent required for all git operations
</user-memory-input>
```

## Section 5: Testing Strategy and Docker Infrastructure
```
<user-memory-input>
Git Hooks Installer Testing Infrastructure:
- Multi-OS Docker testing: Ubuntu 22.04, AlmaLinux 9, Windows Server
- Python 3.12 via deadsnakes PPA for Ubuntu compatibility
- Test runners: ./run_docker-tests.sh, ./run_installer-tests.sh, ./run_installer-fix-tests.sh
- Comprehensive validation including: directory creation, file installation, hook functionality
- Security test scenarios: dirty repository rejection, secret file protection, untracked file safety
- Test results structure: tests/installer-results/YYYY-MM-DD-###-OS-TYPE/
- Results include: validation logs, git status, test summaries in JSON format
- Windows symlink compatibility handled via latest-run-foldername.info text file
- Docker compose orchestration for multiple environments simultaneously
</user-memory-input>
```

## Section 6: Development Workflow and Branch Strategy
```
<user-memory-input>
Git Hooks Project Development Workflow:
- Branch structure: main (protected) ← development ← feature branches
- Currently on development branch for active work
- Feature branches: feature/description, bugfix/description, docs/description
- All changes require PR review before merging to development
- Development to main requires additional review and testing
- Conventional commits required with proper scopes
- Branch protection prevents direct commits to main
- Git workflow documented in docs/git-workflow.md
- CLAUDE.md updated with workflow for future AI instances
- Commit messages stored in markdown format in commit/ folder
</user-memory-input>
```

## Section 7: Key Files and Documentation
```
<user-memory-input>
Important Git Hooks Project Files:
- CLAUDE.md - AI instance context with architecture, commands, workflows
- docs/git-workflow.md - Complete development workflow documentation
- .gitignore includes .claude/ (local workspace, never commit)
- requirements.txt - Python dependencies including python-dotenv
- setup.cfg, pytest.ini - Testing and linting configuration
- Makefile - Build and test automation
- tests/requirements.txt - Testing dependencies
- git-hooks-installer/manage_gitignore.py - Gitignore management (needs chardet dependency)
- Developer setup creates shell wrappers: setup-githooks.sh, setup-githooks.ps1
- Post-commit hooks use lock files to prevent recursive execution
</user-memory-input>
```

## Section 8: Pending Tasks and Next Steps
```
<user-memory-input>
Git Hooks Installer Pending Work:
- Implement safe installer version with repository validation and file tracking
- Fix path detection logic in setup_githooks.py for cross-platform compatibility
- Set up git hooks on this repository itself for auto-documentation
- Configure branch protection rules on GitHub/GitLab
- Create comprehensive User Story-driven test suite
- Deploy safe installer testing infrastructure
- Update all documentation to warn against --auto-merge usage
- Establish CI/CD pipeline working with development branch workflow
- Complete security analysis methodology documentation for reuse on other projects
</user-memory-input>
```