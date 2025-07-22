# setup-githooks.ps1
# PowerShell script for Windows developers to install git hooks
# Run with: .\setup-githooks.ps1

Write-Host "=== Git Hooks Setup Script (Windows) ===" -ForegroundColor Green
Write-Host "This script will install the git hooks for this repository"
Write-Host ""

# Check if we're in a git repository
try {
    $gitDir = git rev-parse --git-dir 2>$null
    if (!$?) {
        throw "Not in a git repository"
    }
} catch {
    Write-Host "❌ Error: Not in a git repository" -ForegroundColor Red
    Write-Host "Please run this script from the repository root"
    exit 1
}

# Get repository root
$repoRoot = git rev-parse --show-toplevel
$repoRoot = $repoRoot -replace '/', '\'
Set-Location $repoRoot

Write-Host "📍 Repository root: $repoRoot" -ForegroundColor Yellow

# Check if scripts directory exists
if (!(Test-Path "scripts\post-commit")) {
    Write-Host "❌ Error: scripts\post-commit directory not found" -ForegroundColor Red
    Write-Host "This repository may not have git hooks set up yet"
    exit 1
}

# Create hooks directory if it doesn't exist
$hooksDir = Join-Path $repoRoot ".git\hooks"
if (!(Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir | Out-Null
}

# Function to install a hook
function Install-Hook {
    param($hookName)
    
    $sourceFile = Join-Path $repoRoot "scripts\git-hooks\$hookName"
    $destFile = Join-Path $hooksDir $hookName
    
    if (Test-Path $sourceFile) {
        Write-Host "📄 Installing $hookName hook..." -ForegroundColor Green
        Copy-Item $sourceFile $destFile -Force
        Write-Host "   ✅ Installed"
    } else {
        Write-Host "⏭️  No $hookName hook found, skipping" -ForegroundColor Yellow
    }
}

# Install post-commit hook
if (Test-Path "scripts\git-hooks\post-commit") {
    Write-Host "📄 Installing post-commit hook..." -ForegroundColor Green
    Copy-Item "scripts\git-hooks\post-commit" "$hooksDir\post-commit" -Force
    Write-Host "   ✅ Installed"
} else {
    # Create post-commit hook for Windows
    Write-Host "📝 Creating post-commit hook..." -ForegroundColor Yellow
    
    $postCommitContent = @'
#!/bin/bash
# Auto-generated post-commit hook for Windows

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Export variables for the scripts
export REPO_ROOT
export BRANCH_NAME=$(git symbolic-ref --short HEAD 2>/dev/null || echo "HEAD")

echo "🎯 Running post-commit hooks..."

# Run generate_git_timeline.py if it exists
if [ -f "$REPO_ROOT/scripts/post-commit/generate_git_timeline.py" ]; then
    echo "📊 Generating git timeline..."
    python "$REPO_ROOT/scripts/post-commit/generate_git_timeline.py"
fi

# Run update-readme.sh if it exists
if [ -f "$REPO_ROOT/scripts/post-commit/update-readme.sh" ]; then
    echo "📝 Updating README..."
    bash "$REPO_ROOT/scripts/post-commit/update-readme.sh"
fi

echo "✅ Post-commit hooks completed"
'@
    
    Set-Content -Path "$hooksDir\post-commit" -Value $postCommitContent -Encoding UTF8
    Write-Host "   ✅ Created"
}

# Install other hooks
foreach ($hook in @("pre-commit", "prepare-commit-msg", "commit-msg", "pre-push")) {
    Install-Hook $hook
}

# Set up git config
Write-Host "⚙️  Setting up git config..." -ForegroundColor Green

# Check if user.name is set
$userName = git config user.name
if (!$userName) {
    Write-Host "   No git user.name set" -ForegroundColor Yellow
    $userName = Read-Host "   Enter your name"
    git config user.name $userName
}

# Check if user.email is set
$userEmail = git config user.email
if (!$userEmail) {
    Write-Host "   No git user.email set" -ForegroundColor Yellow
    $userEmail = Read-Host "   Enter your email"
    git config user.email $userEmail
}

# Set up commit template if exists
if (Test-Path ".gitmessage") {
    git config commit.template .gitmessage
    Write-Host "   ✅ Commit template configured"
}

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>$null
    if ($?) {
        Write-Host "   ✅ Python found: $pythonVersion"
    } else {
        throw "Python not found"
    }
} catch {
    try {
        $pythonVersion = python3 --version 2>$null
        if ($?) {
            Write-Host "   ✅ Python3 found: $pythonVersion"
            Write-Host "   Note: You may need to use 'python3' instead of 'python'" -ForegroundColor Yellow
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "   ❌ Python not found! Please install Python 3" -ForegroundColor Red
        Write-Host "   Download from: https://www.python.org/downloads/"
    }
}

# Install Python dependencies
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Green
    try {
        pip install -r requirements.txt
        if (!$?) {
            pip3 install -r requirements.txt
        }
    } catch {
        Write-Host "   ⚠️  Could not install dependencies automatically" -ForegroundColor Yellow
        Write-Host "   Please run: pip install -r requirements.txt"
    }
}

# Final summary
Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Git hooks have been installed. They will run automatically on commits."
Write-Host ""
Write-Host "Hooks installed:"

if (Test-Path "$hooksDir\post-commit") { Write-Host "  ✅ post-commit - Updates git timeline and README" }
if (Test-Path "$hooksDir\pre-commit") { Write-Host "  ✅ pre-commit" }
if (Test-Path "$hooksDir\prepare-commit-msg") { Write-Host "  ✅ prepare-commit-msg" }
if (Test-Path "$hooksDir\commit-msg") { Write-Host "  ✅ commit-msg" }
if (Test-Path "$hooksDir\pre-push") { Write-Host "  ✅ pre-push" }

Write-Host ""
Write-Host "To test the hooks, make a commit:"
Write-Host "  git add ."
Write-Host '  git commit -m "test: Testing git hooks"'
Write-Host ""
Write-Host "Note: If you're using Git Bash on Windows, the hooks should work automatically." -ForegroundColor Yellow
Write-Host ""