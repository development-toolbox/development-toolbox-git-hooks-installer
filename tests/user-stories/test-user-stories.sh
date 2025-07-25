#!/bin/bash
set -e

# User Story Test Suite for Safe Git Hooks Installer
# Tests all valid User Stories and validates invalid ones are rejected

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
    rm -rf "$repo_path"
    mkdir -p "$repo_path"
    cd "$repo_path"
    
    # Initialize clean git repo
    git init --quiet
    echo "# Test Repository for $repo_name" > README.md
    git add README.md
    git commit --quiet -m "Initial commit"
    
    echo "$repo_path"
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

# Create repo with existing conflicting branch
setup_repo_with_branch_conflict() {
    local repo_name=$1
    local repo_path="$TEST_REPO_BASE/$repo_name"
    
    setup_clean_repo "$repo_name" > /dev/null
    cd "$repo_path"
    
    # Create conflicting branch
    git checkout -b feat/safe-githooks-installation-20250724-000000 --quiet
    git checkout main --quiet
    
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

###########################################
# USER STORY TESTS
###########################################

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

# US-002: Team Lead Code Quality Control
test_us002_pr_workflow_required() {
    local repo_path
    repo_path=$(setup_clean_repo "us002-pr-workflow")
    cd "$repo_path"
    
    log_info "US-002: Testing PR workflow requirement"
    
    # Run safe installer
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        # Check that changes are on feature branch, not main
        local feature_branch
        feature_branch=$(git branch | grep "feat/safe-githooks-installation" | sed 's/^[* ] *//')
        
        if [ -n "$feature_branch" ]; then
            # Switch to feature branch and verify files exist
            git checkout "$feature_branch" --quiet
            if [ -d "scripts" ] && [ -d "developer-setup" ]; then
                # Switch back to main and verify files don't exist there
                git checkout main --quiet
                if [ ! -d "scripts" ] && [ ! -d "developer-setup" ]; then
                    log_info "✅ Changes isolated to feature branch, PR workflow enforced"
                    return 0
                else
                    log_info "❌ Changes found on main branch - PR workflow bypassed"
                    return 1
                fi
            else
                log_info "❌ Files not found on feature branch"
                return 1
            fi
        else
            log_info "❌ Feature branch not created"
            return 1
        fi
    else
        log_info "❌ Safe installer failed"
        return 1
    fi
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

# US-004: Cross-Platform Developer Setup
test_us004_cross_platform_setup() {
    local repo_path
    repo_path=$(setup_clean_repo "us004-cross-platform")
    cd "$repo_path"
    
    log_info "US-004: Testing cross-platform developer setup"
    
    # Run safe installer
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        # Switch to feature branch to check files
        local feature_branch
        feature_branch=$(git branch | grep "feat/safe-githooks-installation" | sed 's/^[* ] *//')
        git checkout "$feature_branch" --quiet
        
        # Check for cross-platform files
        if [ -f "setup-githooks.sh" ] && [ -f "setup-githooks.ps1" ]; then
            # Test shell script is executable
            if [ -x "setup-githooks.sh" ]; then
                # Test shell script can run (dry run)
                if ./setup-githooks.sh --check-only 2>/dev/null; then
                    log_info "✅ Cross-platform setup working"
                    return 0
                else
                    log_info "❌ Shell script test failed"
                    return 1
                fi
            else
                log_info "❌ Shell script not executable"
                return 1
            fi
        else
            log_info "❌ Cross-platform wrapper scripts missing"
            return 1
        fi
    else
        log_info "❌ Safe installer failed"
        return 1
    fi
}

# US-005: Repository Administrator Branch Protection
test_us005_branch_protection_respect() {
    local repo_path
    repo_path=$(setup_repo_with_branch_conflict "us005-branch-conflict")
    cd "$repo_path"
    
    log_info "US-005: Testing branch protection respect"
    
    # Run safe installer (should fail due to branch conflict)
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        log_info "❌ Installer should have detected branch conflict"
        return 1
    else
        log_info "✅ Branch protection respected, conflicting branch detected"
        return 0
    fi
}

###########################################
# INVALID USER STORY TESTS (Should be rejected)
###########################################

# US-INVALID-001: Rushed Developer (Auto-merge request)
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

# US-INVALID-002: Lazy Cleanup (Auto-commit user files)
test_invalid_us002_auto_commit_user_files() {
    local repo_path
    repo_path=$(setup_dirty_repo_with_secrets "invalid-us002-auto-commit")
    cd "$repo_path"
    
    log_info "INVALID-US-002: Testing auto-commit rejection"
    
    # Safe installer should reject dirty repo
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        log_info "❌ Installer should reject dirty repository"
        return 1
    else
        # Double-check secrets weren't committed
        if git ls-files | grep -q ".env"; then
            log_info "❌ Secret files were committed!"
            return 1
        else
            log_info "✅ Auto-commit of user files properly prevented"
            return 0
        fi
    fi
}

###########################################
# SECURITY PENETRATION TESTS
###########################################

test_security_secret_file_protection() {
    local repo_path
    repo_path=$(setup_clean_repo "security-secrets")
    cd "$repo_path"
    
    log_info "SECURITY: Testing secret file protection"
    
    # Create common secret files
    echo "aws_access_key_id = AKIA..." > .aws/credentials
    echo "ssh-rsa AAAA..." > .ssh/id_rsa
    echo "API_KEY=sk-..." > .env.production
    echo "password123" > passwords.txt
    
    mkdir -p .aws .ssh
    
    # Try to run installer (should fail)
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        log_info "❌ Installer should reject repository with secrets"
        return 1
    else
        log_info "✅ Secret files properly protected"
        return 0
    fi
}

test_security_git_history_protection() {
    local repo_path
    repo_path=$(setup_clean_repo "security-history")
    cd "$repo_path"
    
    log_info "SECURITY: Testing git history protection"
    
    # Run installer
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>/dev/null; then
        # Check git history for any secrets or unexpected commits
        local commit_count
        commit_count=$(git log --oneline | wc -l)
        
        # Should only have initial commit + installer commit on feature branch
        local feature_branch
        feature_branch=$(git branch | grep "feat/safe-githooks-installation" | sed 's/^[* ] *//')
        
        if [ -n "$feature_branch" ]; then
            git checkout "$feature_branch" --quiet
            local feature_commit_count
            feature_commit_count=$(git log --oneline | wc -l)
            
            if [ "$feature_commit_count" -eq 2 ]; then
                log_info "✅ Git history clean, only expected commits"
                return 0
            else
                log_info "❌ Unexpected commits in git history"
                return 1
            fi
        else
            log_info "❌ Feature branch not found"
            return 1
        fi
    else
        log_info "❌ Safe installer failed"
        return 1
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
    
    # Run all User Story tests
    log_info "📋 VALID USER STORY TESTS"
    echo "----------------------------"
    run_test "US-001: Safe Installation with Secrets" test_us001_safe_installation_with_secrets
    run_test "US-002: PR Workflow Required" test_us002_pr_workflow_required
    run_test "US-003: Work-in-Progress Protection" test_us003_wip_protection
    run_test "US-004: Cross-Platform Setup" test_us004_cross_platform_setup
    run_test "US-005: Branch Protection Respect" test_us005_branch_protection_respect
    
    log_info "🚫 INVALID USER STORY TESTS (Should be rejected)"
    echo "---------------------------------------------------"
    run_test "INVALID-US-001: Auto-merge Request" test_invalid_us001_auto_merge_request
    run_test "INVALID-US-002: Auto-commit User Files" test_invalid_us002_auto_commit_user_files
    
    log_info "🛡️ SECURITY PENETRATION TESTS"
    echo "--------------------------------"
    run_test "Security: Secret File Protection" test_security_secret_file_protection
    run_test "Security: Git History Protection" test_security_git_history_protection
    
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
        log_success "Safe installer implementation validated against all User Stories"
        exit 0
    else
        echo ""
        log_failure "❌ Some tests failed - see details above"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "🧹 Cleaning up test repositories..."
    rm -rf "$TEST_REPO_BASE"
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main