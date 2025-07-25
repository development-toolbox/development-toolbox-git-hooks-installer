# Git Workflow for Development Toolbox

## Branch Strategy

This project follows a structured git flow to ensure code quality and safety:

### Branch Types

1. **`main`** (Protected)
   - Production-ready code only
   - Never commit directly
   - Only receives merges from `development` via PR
   - All tests must pass
   - Requires code review

2. **`development`** (Integration)
   - Active development branch
   - Feature branches created from here
   - Feature branches merge back here
   - Regular integration testing
   - Merges to `main` when stable

3. **`feature/*`** (Feature Development)
   - Created from `development`
   - Named: `feature/description-of-feature`
   - Short-lived branches
   - Merge back to `development` via PR

4. **`bugfix/*`** (Bug Fixes)
   - Created from `development` (or `main` for hotfixes)
   - Named: `bugfix/description-of-fix`
   - Merge back to source branch via PR

5. **`docs/*`** (Documentation)
   - Created from `development`
   - Named: `docs/what-docs-updating`
   - For documentation-only changes

## Workflow Examples

### Starting New Feature
```bash
# Ensure development is up to date
git checkout development
git pull origin development

# Create feature branch
git checkout -b feature/safe-installer-implementation

# Work on feature
# ... make changes ...

# Commit with conventional commits
git add .
git commit -m "feat(installer): implement repository validation checks"

# Push feature branch
git push origin feature/safe-installer-implementation

# Create PR from feature -> development
```

### Merging to Main
```bash
# Ensure development is stable and tested
git checkout development
git pull origin development

# Create PR from development -> main
# After approval and tests pass, merge PR
```

### Hotfix for Production
```bash
# For critical fixes only
git checkout main
git pull origin main
git checkout -b bugfix/critical-security-fix

# Make minimal fix
# Test thoroughly

# Create PR from bugfix -> main
# After merge, also merge to development
git checkout development
git merge main
```

## Commit Message Convention

All commits must follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes

### Scopes
Can be single or multiple:
- `type(scope)`: Single scope
- `type(scope1,scope2)`: Multiple scopes

### Examples
```
feat(installer): add repository clean state validation
fix(security,installer): prevent auto-commit of user files  
docs(workflow,testing): add git workflow and testing strategy
test(installer,docker): add security validation test suite
```

## Protection Rules

### Main Branch
- No direct pushes
- Require PR reviews (at least 1)
- Require status checks to pass
- Require branches to be up to date
- Include administrators in restrictions

### Development Branch
- No direct pushes (prefer PRs)
- Require status checks to pass
- Encourage code reviews

## Why This Workflow?

1. **Safety**: Protects main branch from accidental changes
2. **Quality**: All code is reviewed before production
3. **Testing**: Features tested in development before main
4. **Flexibility**: Easy to experiment in feature branches
5. **Rollback**: Easy to revert if issues found

## Current Status

- ✅ `development` branch created
- 🔄 Currently on `development` branch
- 📝 Ready for feature development

---

**Remember**: NEVER use `--auto-merge` flag in the git hooks installer!