#!/bin/bash
set -e

# Test script for new --check/-c functionality

echo "🧪 Testing --check/-c functionality"
echo "===================================="

# Test 1: Check in non-git repo (should fail)
echo "Test 1: Check in non-git repository"
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

if python3 /app/git-hooks-installer/git-hooks-installer.py --check; then
    echo "❌ Should have failed in non-git repo"
    exit 1
else
    echo "✅ Correctly failed in non-git repo"
fi

# Test 2: Check in clean git repo without hooks (should show not installed)
echo ""
echo "Test 2: Check in clean git repository"
git init
echo "test" > README.md
git add README.md
git commit -m "Initial commit"

echo "Running check on clean repo..."
if python3 /app/git-hooks-installer/git-hooks-installer.py --check; then
    echo "❌ Should have returned non-zero exit code (hooks not installed)"
    exit 1
else
    echo "✅ Correctly reported hooks not installed"
fi

# Test 3: Install hooks and then check (should show installed)
echo ""
echo "Test 3: Install hooks then check status"
echo "Installing hooks..."
if python3 /app/git-hooks-installer/git-hooks-installer.py .; then
    echo "✅ Installation completed"
    
    # Switch to feature branch to check installed files
    FEATURE_BRANCH=$(git branch | grep "feat/githooks-installation" | sed 's/^[* ] *//')
    if [ -n "$FEATURE_BRANCH" ]; then
        git checkout "$FEATURE_BRANCH"
        echo "Switched to feature branch: $FEATURE_BRANCH"
        
        # Now check status
        echo "Running check after installation..."
        if python3 /app/git-hooks-installer/git-hooks-installer.py --check; then
            echo "✅ Check passed - hooks are installed"
        else
            echo "❌ Check failed - hooks should be installed"
            exit 1
        fi
    else
        echo "❌ Feature branch not found"
        exit 1
    fi
else
    echo "❌ Installation failed"
    exit 1
fi

# Test 4: Test short flag -c
echo ""
echo "Test 4: Test short flag -c"
if python3 /app/git-hooks-installer/git-hooks-installer.py -c; then
    echo "✅ Short flag -c works"
else
    echo "❌ Short flag -c failed"
    exit 1
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 All --check functionality tests passed!"