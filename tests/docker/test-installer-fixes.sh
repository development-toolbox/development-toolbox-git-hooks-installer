#!/bin/bash
set -e

# Configuration
TEST_REPO="/test-repo"
INSTALLER_PATH="/app/git-hooks-installer/git-hooks-installer-fixed.py"
RESULTS_BASE="/app/tests/installer-results"
OS_NAME="ubuntu-fix-test"
TEST_TYPE="${TEST_TYPE:-fixes}"

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
echo "=== TESTING INSTALLER FIXES ==="
echo "Test results will be saved to: $FULL_PATH"

# Start logging
LOG_FILE="$FULL_PATH/installer.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=== Git Hooks Installer FIXES Test ==="
echo "Date: $(date)"
echo "OS: $OS_NAME"
echo "Test Type: $TEST_TYPE"
echo "Python Version: $(python --version 2>&1)"
echo "Git Version: $(git --version)"
echo "Installer: FIXED VERSION (git-hooks-installer-fixed.py)"
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
        echo "=== Repository Tree Structure ==="
        tree -a -I '.git' || find . -type f | grep -v ".git/" | sort
    } > "$status_file"
}

# Capture initial state
echo "Capturing initial repository state..."
capture_git_status "$FULL_PATH/git-status-before.txt"

# Run the FIXED installer
echo "Running FIXED git hooks installer..."
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

# COMPREHENSIVE VALIDATION
echo ""
echo "=== COMPREHENSIVE VALIDATION (FIXED VERSION) ==="
cd "$TEST_REPO"

VALIDATION_ERRORS=0

# List complete directory structure
{
    echo "=== COMPLETE REPOSITORY STRUCTURE ==="
    tree -a -I '.git' || find . -type f | head -50 | sort
    echo ""
    echo "=== .git/hooks/ ==="
    ls -la .git/hooks/ 2>/dev/null || echo "No hooks directory"
    echo ""
    echo "=== scripts/ directory structure ==="
    if [ -d "scripts" ]; then
        find scripts -type f 2>/dev/null | sort
        echo "Scripts directory exists: ✅"
    else
        echo "❌ Scripts directory missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    echo ""
    echo "=== docs/ directory structure ==="
    if [ -d "docs" ]; then
        find docs -type f 2>/dev/null | sort
        echo "Docs directory exists: ✅"
    else
        echo "❌ Docs directory missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    echo ""
    echo "=== developer-setup/ directory structure ==="
    if [ -d "developer-setup" ]; then
        find developer-setup -type f 2>/dev/null | sort
        echo "Developer-setup exists: ✅"
        
        # Check for critical components
        if [ -d "developer-setup/templates" ]; then
            echo "Templates directory exists: ✅"
        else
            echo "❌ Templates directory missing"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
        
        if [ -f "developer-setup/setup_githooks.py" ]; then
            echo "setup_githooks.py exists: ✅"
        else
            echo "❌ setup_githooks.py missing"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
        
        if [ -f "developer-setup/SETUP-GITHOOKS.md" ]; then
            echo "SETUP-GITHOOKS.md exists: ✅"
        else
            echo "❌ SETUP-GITHOOKS.md missing"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
        
    else
        echo "❌ Developer-setup directory missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    echo ""
    echo "=== Shell wrapper scripts ==="
    if [ -f "setup-githooks.sh" ]; then
        echo "setup-githooks.sh exists: ✅"
        if [ -x "setup-githooks.sh" ]; then
            echo "setup-githooks.sh is executable: ✅"
        else
            echo "❌ setup-githooks.sh not executable"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
    else
        echo "❌ setup-githooks.sh missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    
    if [ -f "setup-githooks.ps1" ]; then
        echo "setup-githooks.ps1 exists: ✅"
    else
        echo "❌ setup-githooks.ps1 missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    echo ""
    echo "=== Version file ==="
    if [ -f "docs/githooks/.githooks-version.json" ]; then
        echo "Version file exists: ✅"
        echo "Version file contents:"
        cat "docs/githooks/.githooks-version.json" | head -20
    else
        echo "❌ Version file missing"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    echo ""
    echo "=== Git status after installation ==="
    git status --porcelain || echo "No git status available"
    echo ""
    echo "=== Git branches ==="
    git branch -a 2>/dev/null || echo "No branches found"
} > "$FULL_PATH/validation-detailed.txt"

# TEST DEVELOPER SETUP
echo ""
echo "=== TESTING DEVELOPER SETUP ==="
if [ -f "setup-githooks.sh" ]; then
    echo "Testing shell wrapper (--check-only)..."
    if ./setup-githooks.sh --check-only; then
        echo "Developer setup test passed: ✅"
    else
        echo "❌ Developer setup test failed"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
else
    echo "❌ Cannot test - setup-githooks.sh missing"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# TEST INSTALLED HOOKS
if [ "$INSTALL_STATUS" = "success" ] && [ "$VALIDATION_ERRORS" -eq 0 ]; then
    echo ""
    echo "=== TESTING INSTALLED HOOKS ==="
    
    # Make a test commit
    echo "Creating test commit..."
    echo "Test content $(date)" >> test-file.txt
    git add test-file.txt
    
    if git commit -m "test: Testing installed hooks with FIXED installer"; then
        echo "Test commit successful: ✅"
        
        # Check if documentation was generated
        if [ -d "docs/commit-logs" ]; then
            echo "Commit logs directory exists: ✅"
            find docs/commit-logs -type f -name "*.md" | head -5
        else
            echo "❌ No commit logs directory found"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
    else
        echo "❌ Test commit failed"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
elif [ "$INSTALL_STATUS" = "success" ]; then
    echo "SKIPPING hook test due to validation errors"
fi

# Generate comprehensive test summary JSON
cat > "$FULL_PATH/test-summary.json" << EOF
{
    "test_run_id": "$RUN_DIR",
    "date": "$(date -Iseconds)",
    "os": "$OS_NAME",
    "test_type": "$TEST_TYPE",
    "installer_version": "FIXED v0.6",
    "python_version": "$(python --version 2>&1)",
    "git_version": "$(git --version)",
    "installer_path": "$INSTALLER_PATH",
    "test_repo": "$TEST_REPO",
    "status": "$INSTALL_STATUS",
    "exit_code": $INSTALL_EXIT_CODE,
    "duration_seconds": $INSTALL_DURATION,
    "validation_errors": $VALIDATION_ERRORS,
    "comprehensive_validation": {
        "scripts_directory_exists": $([ -d "scripts" ] && echo "true" || echo "false"),
        "scripts_post_commit_exists": $([ -d "scripts/post-commit" ] && echo "true" || echo "false"),
        "scripts_files_count": $(find scripts -type f 2>/dev/null | wc -l || echo 0),
        "docs_directory_exists": $([ -d "docs" ] && echo "true" || echo "false"),
        "docs_githooks_exists": $([ -d "docs/githooks" ] && echo "true" || echo "false"),
        "docs_files_count": $(find docs -type f 2>/dev/null | wc -l || echo 0),
        "developer_setup_exists": $([ -d "developer-setup" ] && echo "true" || echo "false"),
        "developer_setup_templates_exists": $([ -d "developer-setup/templates" ] && echo "true" || echo "false"),
        "setup_githooks_py_exists": $([ -f "developer-setup/setup_githooks.py" ] && echo "true" || echo "false"),
        "shell_wrapper_sh_exists": $([ -f "setup-githooks.sh" ] && echo "true" || echo "false"),
        "shell_wrapper_ps1_exists": $([ -f "setup-githooks.ps1" ] && echo "true" || echo "false"),
        "version_file_exists": $([ -f "docs/githooks/.githooks-version.json" ] && echo "true" || echo "false"),
        "hooks_installed": $(ls -1 .git/hooks/ 2>/dev/null | grep -v sample | wc -l || echo 0),
        "post_commit_hook_exists": $([ -f ".git/hooks/post-commit" ] && echo "true" || echo "false"),
        "git_branches_created": $(git branch -a 2>/dev/null | grep -c "feat/.*githooks" || echo 0),
        "developer_setup_functional": $([ -f "setup-githooks.sh" ] && [ -x "setup-githooks.sh" ] && echo "true" || echo "false")
    }
}
EOF

# Update status if validation failed
if [ "$VALIDATION_ERRORS" -gt 0 ]; then
    echo ""
    echo "❌ VALIDATION FAILED: $VALIDATION_ERRORS errors found"
    INSTALL_STATUS="validation_failed"
    INSTALL_EXIT_CODE=1
else
    echo ""
    echo "✅ ALL VALIDATIONS PASSED!"
fi

# Create text file with latest test folder name
cd "$RESULTS_BASE"
echo "$RUN_DIR" > latest-run-foldername.info

echo ""
echo "=== FIXES TEST COMPLETE ==="
echo "Results saved to: $FULL_PATH"
echo "Validation errors: $VALIDATION_ERRORS"
echo "Exit code: $INSTALL_EXIT_CODE"

if [ "$VALIDATION_ERRORS" -eq 0 ]; then
    echo ""
    echo "🎉 INSTALLER FIXES SUCCESSFUL!"
    echo "✅ Scripts directory created properly"
    echo "✅ Docs directory installed correctly"  
    echo "✅ Developer setup with full structure"
    echo "✅ Shell wrapper scripts created"
    echo "✅ Version file tracking working"
    echo "✅ All components validated"
fi

exit $INSTALL_EXIT_CODE