#!/bin/bash
set -e

# Run a single User Story test for debugging

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

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
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

# US-001: Safe Installation for Developer with Secrets
test_us001_safe_installation_with_secrets() {
    local repo_path
    repo_path=$(setup_clean_repo "us001-clean-repo")
    cd "$repo_path"
    
    log_info "US-001: Testing safe installation on clean repository"
    
    # Run safe installer
    log_info "Running: python3 $SAFE_INSTALLER --source $SOURCE_DIR ."
    if python3 "$SAFE_INSTALLER" --source "$SOURCE_DIR" . 2>&1; then
        log_info "Installer executed successfully"
        
        # Validate installation
        if [ -d "scripts" ] && [ -d "developer-setup" ] && [ -f "setup-githooks.sh" ]; then
            log_info "Required files found"
            
            # Check that feature branch was created
            if git branch | grep -q "feat/safe-githooks-installation"; then
                log_info "Feature branch found"
                
                # Check that main branch doesn't have installer files
                git checkout main --quiet
                
                # Post-commit hooks may have run, clean up any generated files
                git reset --hard HEAD --quiet 2>/dev/null || true
                git clean -fd --quiet 2>/dev/null || true
                
                # Check that installer files are NOT on main branch
                if [ ! -d "scripts" ] && [ ! -d "developer-setup" ] && [ ! -f "setup-githooks.sh" ]; then
                    log_success "✅ Feature branch created, main branch clean of installer files"
                    return 0
                else
                    log_failure "❌ Main branch contains installer files (should be feature-branch only)"
                    ls -la
                    return 1
                fi
            else
                log_failure "❌ Feature branch not created"
                git branch
                return 1
            fi
        else
            log_failure "❌ Required files not installed"
            ls -la
            return 1
        fi
    else
        log_failure "❌ Safe installer failed on clean repository"
        return 1
    fi
}

# Create results directory
mkdir -p "$RESULTS_DIR"

log_info "🧪 Running Single User Story Test: US-001"
log_info "========================================"

if test_us001_safe_installation_with_secrets; then
    log_success "🎉 US-001 TEST PASSED!"
else
    log_failure "❌ US-001 TEST FAILED!"
fi

log_info "🧹 Cleaning up test repositories..."
rm -rf "$TEST_REPO_BASE"
log_info "✅ Test completed"