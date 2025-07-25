# Setting Up Git Hooks

This repository uses automated git hooks to maintain documentation and commit history. Follow these instructions to set them up on your local machine.

## Quick Start

### macOS/Linux:
```bash
./setup-githooks.sh
```

### Windows:
```powershell
.\setup-githooks.ps1
```

Or if using Git Bash:
```bash
bash setup-githooks.sh
```

## What This Does

The setup script will:

1. **Install Git Hooks** - Copies hooks to `.git/hooks/`
2. **Configure Git** - Sets up user.name and user.email if needed
3. **Check Python** - Verifies Python is installed
4. **Install Dependencies** - Runs `pip install -r requirements.txt`

## Installed Hooks

### post-commit
Runs after every commit to:
- Generate git timeline documentation
- Update README with latest commit info
- Create commit log files

## Manual Installation

If the setup script doesn't work, you can install manually:

1. Copy hook files:
   ```bash
   cp scripts/git-hooks/* .git/hooks/
   chmod +x .git/hooks/*
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure git (if needed):
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

## Troubleshooting

### Hooks not running?
- Check they're executable: `ls -la .git/hooks/`
- Make sure Python is installed: `python --version`
- Check for errors: `bash .git/hooks/post-commit`

### Python not found?
- Install Python 3: https://www.python.org/downloads/
- On macOS: `brew install python3`
- On Ubuntu: `sudo apt install python3 python3-pip`
- On AlmaLinux (RHEL) `yum install python3 python3-pip`

### Permission denied?
```bash
chmod +x setup-githooks.sh
chmod +x .git/hooks/*
```

## Disabling Hooks Temporarily

To skip hooks for one commit:
```bash
git commit --no-verify -m "your message"
```

To disable completely:
```bash
mv .git/hooks/post-commit .git/hooks/post-commit.disabled
```

## For Repository Maintainers

To update the git hooks installation:
```bash
python git-hooks-installer.py --source /path/to/git-hooks-installer
````

This will update the hooks and scripts to the latest version.