# Conventional Commits Guide

This project uses the **Conventional Commits** standard to ensure clarity, consistency, and better automation in version control. The goal is to create a structured commit history that improves collaboration and makes the project easier to maintain.

## Why Use Conventional Commits?
- **Consistency:** Makes commit messages easier to read and understand.
- **Automation:** Allows tools to generate changelogs and automate versioning.
- **Clarity:** Helps contributors quickly understand the purpose of each commit.

## Commit Message Format
A commit message should follow this structure:

```plaintext
<type>(<scope>): <description>

[optional body with bullet points or paragraphs]

[optional footer(s)]
```

## Commit Types and Examples from This Project

### 🚀 `feat:` (Feature)
- **Description:** Introduces a new feature or major functionality.
- **Real Examples:**
  - `feat(installer): add --check/-c option for installation status verification`
  - `feat(testing): Add comprehensive Docker-based installer testing infrastructure`
  - `feat(installer): major refactor - secure Python package structure, comprehensive testing, and simplified interface`

### 🐛 `fix:` (Bug Fix)
- **Description:** Fixes a bug or issue.
- **Real Examples:**
  - `fix(installer): correct path normalization for cross-platform compatibility`
  - `fix(test): remove --source parameter from test scripts`
  - `fix(cleanup): properly remove tracked files on installation failure`

### ♻️ `refactor:` (Code Refactoring)
- **Description:** Code changes that improve structure without changing functionality.
- **Real Examples:**
  - `refactor(installer): rename SafeFileTracker to FileTracker`
  - `refactor(structure): reorganize into proper Python package with security/ and utils/`
  - `refactor(imports): update all import statements after package reorganization`

### 🔧 `chore:` (Maintenance Tasks)
- **Description:** Changes related to build tools, dependencies, or project settings.
- **Real Examples:**
  - `chore(cleanup): archive obsolete installer versions`
  - `chore(deps): update developer-setup requirements.txt`
  - `chore(git): add .treeignore for better directory visualization`

### 📚 `docs:` (Documentation)
- **Description:** Documentation changes only.
- **Real Examples:**
  - `docs(security): add SECURITY-IMPLEMENTATION-FRAMEWORK.md`
  - `docs(readme): update with new package structure and --check option`
  - `docs(todo): document todo folder management system in CLAUDE.md`

### 🎨 `style:` (Code Style)
- **Description:** Formatting and style updates without functional impact.
- **Real Examples:**
  - `style(formatting): fix indentation in git-hooks-installer.py`
  - `style(naming): update class names to follow Python conventions`
  - `style(comments): remove unnecessary inline comments`

### 🧪 `test:` (Testing)
- **Description:** Adding or updating tests.
- **Real Examples:**
  - `test(options): add test-all-program-options.sh for comprehensive CLI testing`
  - `test(docker): create separate compose files for different test suites`
  - `test(user-stories): add USER-STORY-TEST-RESULTS.md documentation`

### ⚡ `perf:` (Performance Improvements)
- **Description:** Performance-related improvements.
- **Real Examples:**
  - `perf(installer): optimize file tracking with proper path normalization`
  - `perf(git): batch git operations to reduce subprocess calls`

### 👷 `ci:` (Continuous Integration)
- **Description:** CI/CD configurations and changes.
- **Real Examples:**
  - `ci(docker): add Dockerfile.user-story-tests for isolated testing`
  - `ci(compose): create docker-compose.options-tests.yml`

### 🛡️ `security:` (Security Fixes)
- **Description:** Security-related changes or fixes.
- **Real Examples:**
  - `security(subprocess): implement SecureGitWrapper with command validation`
  - `security(validation): add RepositoryValidator for pre-flight checks`
  - `security(installer): ensure only tracked files are committed`

## Multi-line Commit Examples

### Example 1: Feature with Details
```
feat(installer): implement comprehensive status checking functionality

- Add --check/-c flag for installation verification
- Report status of hooks, scripts, documentation, and wrappers
- Provide clear exit codes (0=complete, 1=incomplete)
- Include detailed feedback on missing components
```

### Example 2: Major Refactor
```
refactor(structure): reorganize project into proper Python package

## Changes
- Create security/ package for secure operations
- Create utils/ package for helper functions
- Move obsolete files to archived/ directory
- Add proper __init__.py files for all packages

## Benefits
- Better code organization
- Cleaner import structure
- Easier testing and maintenance
```

## Best Practices for This Project

1. **Scope Usage**: Always include scope in parentheses (e.g., `feat(installer):`, `docs(readme):`)
2. **Present Tense**: Use present tense ("add" not "added")
3. **Lowercase**: Start descriptions with lowercase
4. **No Period**: Don't end the subject line with a period
5. **Body Format**: Use bullet points or markdown formatting in the body
6. **Co-authorship**: Include co-author info when using AI assistance:
   ```
   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

## Enforcing Conventional Commits
This project's git hooks automatically validate commit messages and generate documentation. The post-commit hook creates logs tracking all commits.

## References
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format)
- [Gitmoji](https://gitmoji.dev/) - Emoji guide for commit messages