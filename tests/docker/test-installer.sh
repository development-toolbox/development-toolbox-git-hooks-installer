#!/bin/bash
set -e

# Configuration
TEST_REPO="/test-repo"
INSTALLER_PATH="/app/git-hooks-installer/git-hooks-installer.py"
RESULTS_BASE="/app/tests/installer-results"
OS_NAME=$(cat /etc/os-release | grep "^ID=" | cut -d= -f2 | tr -d '"')
TEST_TYPE="${TEST_TYPE:-initial}"

# Generate test run directory name
DATE=$(date +%Y-%m-%d)
RUN_NUMBER=1

# Find the next available run number for today
while true; do
    RUN_DIR=$(printf "%s-%03d-%s-%s" "$DATE" "$RUN_NUMBER" "$OS_NAME" "$TEST_TYPE")
    FULL_PATH="$RESULTS_BASE/$RUN_DIR"
    if [ ! -d "$FULL_PATH" ]; then
        break
    fi
    ((RUN_NUMBER++))
done

# Create results directory
mkdir -p "$FULL_PATH"
echo "Test results will be saved to: $FULL_PATH"

# Start logging
LOG_FILE="$FULL_PATH/installer.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=== Git Hooks Installer Test ==="
echo "Date: $(date)"
echo "OS: $OS_NAME"
echo "Test Type: $TEST_TYPE"
echo "Python Version: $(python --version 2>&1)"
echo "Git Version: $(git --version)"
echo ""

# Function to capture git status
capture_git_status() {
    local status_file="$1"
    cd "$TEST_REPO"
    {
        echo "=== Git Status ==="
        git status
        echo ""
        echo "=== Git Log ==="
        git log --oneline -10
        echo ""
        echo "=== Installed Files ==="
        find . -type f -name "*" | grep -E "(hook|githook|\.git/)" | sort || true
    } > "$status_file"
}

# Capture initial state
echo "Capturing initial repository state..."
capture_git_status "$FULL_PATH/git-status-before.txt"

# Run the installer
echo "Running git hooks installer..."
cd /app
INSTALL_START=$(date +%s)

if python "$INSTALLER_PATH" --source /app/git-hooks-installer --auto-merge "$TEST_REPO"; then
    INSTALL_STATUS="success"
    INSTALL_EXIT_CODE=0
else
    INSTALL_STATUS="failed"
    INSTALL_EXIT_CODE=$?
fi

INSTALL_END=$(date +%s)
INSTALL_DURATION=$((INSTALL_END - INSTALL_START))

echo ""
echo "Installation completed with status: $INSTALL_STATUS (exit code: $INSTALL_EXIT_CODE)"
echo "Duration: ${INSTALL_DURATION}s"

# Capture final state
echo "Capturing final repository state..."
capture_git_status "$FULL_PATH/git-status-after.txt"

# List installed files
echo "Listing installed files..."
cd "$TEST_REPO"
{
    echo "=== Repository Structure After Installation ==="
    find . -type f -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.json" | grep -v ".git/" | sort
    echo ""
    echo "=== .git/hooks/ ==="
    ls -la .git/hooks/ 2>/dev/null || echo "No hooks directory"
    echo ""
    echo "=== docs/ directory structure ==="
    find docs -type f 2>/dev/null | sort || echo "No docs directory"
    echo ""
    echo "=== scripts/ directory structure ==="
    find scripts -type f 2>/dev/null | sort || echo "No scripts directory"
    echo ""
    echo "=== Developer setup files ==="
    ls -la setup-githooks.* SETUP-GITHOOKS.md 2>/dev/null || echo "No developer setup files found"
    echo ""
    echo "=== Version file ==="
    if [ -f "docs/githooks/.githooks-version.json" ]; then
        echo "Version file exists:"
        cat "docs/githooks/.githooks-version.json"
    else
        echo "No version file found"
    fi
    echo ""
    echo "=== Git status after installation ==="
    git status --porcelain || echo "No git status available"
    echo ""
    echo "=== Git branches ==="
    git branch -a 2>/dev/null || echo "No branches found"
} > "$FULL_PATH/installed-files.txt"

# Generate test summary JSON
cat > "$FULL_PATH/test-summary.json" << EOF
{
    "test_run_id": "$RUN_DIR",
    "date": "$(date -Iseconds)",
    "os": "$OS_NAME",
    "test_type": "$TEST_TYPE",
    "python_version": "$(python --version 2>&1)",
    "git_version": "$(git --version)",
    "installer_path": "$INSTALLER_PATH",
    "test_repo": "$TEST_REPO",
    "status": "$INSTALL_STATUS",
    "exit_code": $INSTALL_EXIT_CODE,
    "duration_seconds": $INSTALL_DURATION,
    "validation": {
        "hooks_installed": $(ls -1 .git/hooks/ 2>/dev/null | grep -v sample | wc -l || echo 0),
        "version_file_exists": $([ -f "docs/githooks/.githooks-version.json" ] && echo "true" || echo "false"),
        "docs_folder_exists": $([ -d "docs" ] && echo "true" || echo "false"),
        "scripts_folder_exists": $([ -d "scripts" ] && echo "true" || echo "false"),
        "docs_files_count": $(find docs -type f 2>/dev/null | wc -l || echo 0),
        "scripts_files_count": $(find scripts -type f 2>/dev/null | wc -l || echo 0),
        "developer_setup_exists": $([ -f "SETUP-GITHOOKS.md" ] && echo "true" || echo "false"),
        "post_commit_hook_exists": $([ -f ".git/hooks/post-commit" ] && echo "true" || echo "false"),
        "git_branches_created": $(git branch -a 2>/dev/null | grep -c "feat/.*githooks" || echo 0)
    }
}
EOF

# Validate installation completeness
echo ""
echo "=== Validating Installation ==="
VALIDATION_ERRORS=0

# Check critical components
if [ ! -f ".git/hooks/post-commit" ]; then
    echo "ERROR: post-commit hook not installed"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if [ ! -d "scripts" ]; then
    echo "ERROR: scripts directory not created"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    SCRIPTS_COUNT=$(find scripts -name "*.py" -o -name "*.sh" | wc -l)
    if [ "$SCRIPTS_COUNT" -eq 0 ]; then
        echo "ERROR: No scripts installed in scripts directory"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    else
        echo "SUCCESS: Found $SCRIPTS_COUNT script files"
    fi
fi

if [ ! -d "docs" ]; then
    echo "ERROR: docs directory not created"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    DOCS_COUNT=$(find docs -name "*.md" | wc -l)
    if [ "$DOCS_COUNT" -eq 0 ]; then
        echo "ERROR: No documentation files installed"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    else
        echo "SUCCESS: Found $DOCS_COUNT documentation files"
    fi
fi

if [ ! -f "SETUP-GITHOOKS.md" ]; then
    echo "ERROR: Developer setup documentation not installed"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# Test the installed hooks
if [ "$INSTALL_STATUS" = "success" ] && [ "$VALIDATION_ERRORS" -eq 0 ]; then
    echo ""
    echo "=== Testing Installed Hooks ==="
    
    # Make a test commit
    echo "Creating test commit..."
    echo "Test content $(date)" >> test-file.txt
    git add test-file.txt
    
    if git commit -m "test: Testing installed hooks"; then
        echo "Test commit successful"
        
        # Check if documentation was generated
        if [ -d "docs/commit-logs" ]; then
            echo "Commit logs directory exists"
            find docs/commit-logs -type f -name "*.md" | head -5
        else
            echo "WARNING: No commit logs directory found"
        fi
    else
        echo "ERROR: Test commit failed"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
elif [ "$INSTALL_STATUS" = "success" ]; then
    echo "SKIPPING hook test due to validation errors"
fi

# Update status if validation failed
if [ "$VALIDATION_ERRORS" -gt 0 ]; then
    echo "VALIDATION FAILED: $VALIDATION_ERRORS errors found"
    INSTALL_STATUS="validation_failed"
    INSTALL_EXIT_CODE=1
fi

# Create text file with latest test folder name
cd "$RESULTS_BASE"
echo "$RUN_DIR" > latest-run-foldername.info

echo ""
echo "=== Test Complete ==="
echo "Results saved to: $FULL_PATH"
echo "Exit code: $INSTALL_EXIT_CODE"

exit $INSTALL_EXIT_CODE