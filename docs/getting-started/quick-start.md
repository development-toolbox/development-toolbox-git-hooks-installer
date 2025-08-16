# Quick Start Guide

Get git hooks installed in your repository in 5 minutes.

## TL;DR

```bash
# If you have gh CLI setup
gh auth login
python git-hooks-installer/git-hooks-installer.py /path/to/your/repo

# If you have a GitHub token
export GITHUB_TOKEN=your_token
python git-hooks-installer/git-hooks-installer.py /path/to/your/repo

# Basic installation (no automatic PR)
python git-hooks-installer/git-hooks-installer.py /path/to/your/repo
```

## 5-Minute Setup

### Step 1: Prerequisites (30 seconds)

Make sure you have:
- Python installed (`python --version`)
- Git repository with clean working tree
- GitHub repository (for automatic PR creation)

### Step 2: Choose Authentication (2 minutes)

Pick the easiest option for you:

#### Option A: GitHub CLI (Recommended for developers)
```bash
# Install gh CLI if needed
# macOS: brew install gh
# Linux: see https://github.com/cli/cli#installation
# Windows: winget install GitHub.cli

# Login once
gh auth login
```

#### Option B: GitHub Token (Recommended for CI/CD)
```bash
# Create token at: https://github.com/settings/tokens
# Give it 'repo' scope
export GITHUB_TOKEN=ghp_your_token_here
```

#### Option C: Skip Authentication
Just run the installer - it will create a feature branch but you'll need to create the PR manually.

### Step 3: Run Installer (2 minutes)

```bash
# Navigate to your project
cd /path/to/your/repository

# Run installer
python /path/to/git-hooks-installer/git-hooks-installer.py .
```

The installer will:
1. ✅ Validate your repository
2. ✅ Create a feature branch  
3. ✅ Install git hooks and scripts
4. ✅ Create a pull request (if authenticated)
5. ✅ Return you to your original branch

### Step 4: Merge PR (30 seconds)

If a PR was created automatically:
1. Click the PR link shown in the output
2. Review the changes
3. Merge the PR

If no PR was created:
1. Use the link provided to create one manually
2. Review and merge

## What You Get

After installation, your repository will have:

- **Automated documentation** - Every commit generates logs and timelines
- **Cross-platform setup** - Shell scripts for team members on any OS  
- **Security safeguards** - Only installer files are committed, never your work
- **Professional workflow** - PR-based installation with mandatory review

## Testing It Works

Make a test commit to verify everything is working:

```bash
echo "Testing git hooks" > test-hooks.txt
git add test-hooks.txt
git commit -m "test: verify git hooks are working"

# Check if documentation was generated
ls docs/commit-logs/$(git branch --show-current)/
```

You should see new documentation files created automatically.

## Next Steps

1. **Delete test files** if you created any
2. **Inform your team** about the new git hooks
3. **Make commits** and watch the automatic documentation grow
4. **Customize hooks** if needed (see [Configuration Guide](../reference/configuration.md))

## Common Quick Fixes

### "Repository has uncommitted changes"
```bash
# Commit or stash your changes first
git stash
# or
git add . && git commit -m "wip: save current work"
```

### "No GitHub authentication"
```bash
# Quick token setup
export GITHUB_TOKEN=$(gh auth token)
# or just skip and create PR manually
```

### "Permission denied"
```bash
# Check git remote URL
git remote -v
# Make sure you have write access to the repository
```

## Advanced Quick Setup

### For Multiple Repositories
```bash
# Setup script for multiple repos
for repo in repo1 repo2 repo3; do
  echo "Installing hooks in $repo..."
  python git-hooks-installer/git-hooks-installer.py "$repo"
done
```

### For CI/CD Integration
```bash
# Add to your CI pipeline
export GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
python git-hooks-installer/git-hooks-installer.py .
```

### For Team Onboarding
```bash
# After the initial installation, new team members can use:
./setup-githooks.sh        # Linux/macOS
./setup-githooks.ps1       # Windows
```

That's it! You now have professional git hooks with automated documentation.

Need more details? Check the [Full Installation Guide](installation.md).