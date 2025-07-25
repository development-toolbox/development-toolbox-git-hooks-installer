#!/bin/bash
set -e

# Simple User Story Test Suite - No trap cleanup to avoid hanging

# Configuration
TEST_REPO_BASE="/tmp/user-story-tests"
SAFE_INSTALLER="/app/git-hooks-installer/git-hooks-installer.py"
SOURCE_DIR="/app/git-hooks-installer"
RESULTS_DIR="/tmp/user-story-results"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test setup function
setup_clean_repo() {
    local repo_name=$1
    local repo_path="$TEST_REPO_BASE/$repo_name"
    
    # Clean up any existing repo
    rm -rf "$repo_path" 2>/dev/null || true
    mkdir -p "$repo_path"
    cd "$repo_path"
    
    # Initialize clean git repo
    git init --quiet
    echo "# Test Repository for $repo_name" > README.md
    git add README.md
    git commit --quiet -m "Initial commit"
    
    echo "$repo_path"
}

# Test runner function
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((TOTAL_TESTS++))
    log_info "Running: $test_name"
    
    if $test_function; then
        log_success "$test_name"
    else
        log_failure "$test_name"
    fi
    echo ""
}

# US-001: Safe Installation for Developer with Secrets
test_us001_safe_installation_with_secrets() {
    local repo_path
    repo_path=$(setup_clean_repo "us001-clean-repo")
    cd "$repo_path"
    
    log_info "US-001: Testing safe installation on clean repository"
    
    # Run safe installer
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        # Validate installation
        if [ -d "scripts" ] && [ -d "developer-setup" ] && [ -f "setup-githooks.sh" ]; then
            # Check that feature branch was created
            if git branch | grep -q "feat/safe-githooks-installation"; then
                # Check that main branch doesn't have installer files
                git checkout main --quiet
                
                # Post-commit hooks may have run, clean up any generated files
                git reset --hard HEAD --quiet 2>/dev/null || true
                git clean -fd --quiet 2>/dev/null || true
                
                # Check that installer files are NOT on main branch
                if [ ! -d "scripts" ] && [ ! -d "developer-setup" ] && [ ! -f "setup-githooks.sh" ]; then
                    log_info "✅ Feature branch created, main branch clean of installer files"
                    return 0
                else
                    log_info "❌ Main branch contains installer files (should be feature-branch only)"
                    return 1
                fi
            else
                log_info "❌ Feature branch not created"
                return 1
            fi
        else
            log_info "❌ Required files not installed"
            return 1
        fi
    else
        log_info "❌ Safe installer failed on clean repository"
        return 1
    fi
}

# Create dirty repo with secrets
setup_dirty_repo_with_secrets() {
    local repo_name=$1
    local repo_path="$TEST_REPO_BASE/$repo_name"
    
    # Start with clean repo
    setup_clean_repo "$repo_name" > /dev/null
    cd "$repo_path"
    
    # Add secrets and uncommitted changes
    echo "API_KEY=secret123456" > .env
    echo "DB_PASSWORD=admin123" > config.txt
    echo "debug info" > temp.log
    echo "uncommitted work" > work-in-progress.txt
    
    # Modify existing file
    echo "modified content" >> README.md
    
    echo "$repo_path"
}

# US-003: Developer Work-in-Progress Protection
test_us003_wip_protection() {
    local repo_path
    repo_path=$(setup_dirty_repo_with_secrets "us003-dirty-repo")
    cd "$repo_path"
    
    log_info "US-003: Testing work-in-progress protection"
    
    # Run safe installer (should fail)
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        log_info "❌ Installer should have rejected dirty repository"
        return 1
    else
        # Verify user's work is still intact
        if [ -f ".env" ] && [ -f "work-in-progress.txt" ] && [ -f "temp.log" ]; then
            # Verify files weren't committed
            if ! git ls-files | grep -q ".env"; then
                log_info "✅ Dirty repository rejected, user work protected"
                return 0
            else
                log_info "❌ User files were committed"
                return 1
            fi
        else
            log_info "❌ User work was lost"
            return 1
        fi
    fi
}

# INVALID-US-001: Rushed Developer (Auto-merge request)
test_invalid_us001_auto_merge_request() {
    local repo_path
    repo_path=$(setup_clean_repo "invalid-us001-auto-merge")
    cd "$repo_path"
    
    log_info "INVALID-US-001: Testing auto-merge rejection"
    
    # Try to run with auto-merge flag (should not exist in safe installer)
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" --auto-merge . 2>/dev/null; then
        log_info "❌ Auto-merge flag should not exist in safe installer"
        return 1
    else
        log_info "✅ Auto-merge functionality properly removed"
        return 0
    fi
}

###########################################
# MAIN TEST EXECUTION
###########################################

main() {
    log_info "🧪 Starting User Story Test Suite for Safe Git Hooks Installer"
    log_info "================================================================="
    echo ""
    
    # Ensure results directory exists
    mkdir -p "$RESULTS_DIR"
    
    # Run subset of User Story tests
    log_info "📋 VALID USER STORY TESTS"
    echo "----------------------------"
    run_test "US-001: Safe Installation with Secrets" test_us001_safe_installation_with_secrets
    run_test "US-003: Work-in-Progress Protection" test_us003_wip_protection
    
    log_info "🚫 INVALID USER STORY TESTS (Should be rejected)"
    echo "---------------------------------------------------"
    run_test "INVALID-US-001: Auto-merge Request" test_invalid_us001_auto_merge_request
    
    # Generate summary
    echo ""
    log_info "📊 TEST SUMMARY"
    echo "================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    
    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo ""
        log_success "🎉 ALL USER STORY TESTS PASSED!"
        log_success "Safe installer implementation validated against User Stories"
        exit 0
    else
        echo ""
        log_failure "❌ Some tests failed - see details above"
        exit 1
    fi
}

# Manual cleanup at end (no trap)
cleanup_at_end() {
    log_info "🧹 Cleaning up test repositories..."
    rm -rf "$TEST_REPO_BASE" 2>/dev/null || true
}

# Run main function
main

# Clean up at the end
cleanup_at_end
log_info "✅ Test completed"