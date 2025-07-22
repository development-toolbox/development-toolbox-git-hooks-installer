#!/bin/bash
# setup-githooks.sh
# Script for developers to install git hooks after cloning the repository
# Version: 0.5

set -e  # Exit on error

# Current installer version
EXPECTED_VERSION="0.5"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Git Hooks Setup Script v${EXPECTED_VERSION} ===${NC}"
echo "This script will install the git hooks for this repository"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

echo -e "${YELLOW}📍 Repository root: $REPO_ROOT${NC}"

# Check if scripts directory exists
if [ ! -d "scripts/post-commit" ]; then
    echo -e "${RED}❌ Error: scripts/post-commit directory not found${NC}"
    echo "This repository may not have git hooks set up yet"
    exit 1
fi

# Function to check hook version and hash
check_hook_status() {
    local hook_file=".git/hooks/post-commit"
    
    if [ ! -f "$hook_file" ]; then
        return 2  # Not installed
    fi
    
    # Check if hook contains version string
    if grep -q "setup-githooks.sh v${EXPECTED_VERSION}" "$hook_file" 2>/dev/null; then
        return 0  # Current version
    else
        return 1  # Different/older version
    fi
}

# Create the actual post-commit hook
create_post_commit_hook() {
    cat > .git/hooks/post-commit << EOF
#!/bin/bash
# post-commit
# Installed by setup-githooks.sh v${EXPECTED_VERSION}

set -e  # Exit script if any command fails

# Prevent recursive execution using a marker file
MARKER_FILE=\$(git rev-parse --git-path hooks/.post-commit.lock)

if [ -f "\$MARKER_FILE" ]; then
  echo "🚫 Skipping post-commit actions to prevent recursion."
  exit 0
fi

# Create the marker file
touch "\$MARKER_FILE"

# Ensure marker is removed even if the script fails
trap 'rm -f "\$MARKER_FILE"' EXIT

# Get the repository root directory
REPO_ROOT=\$(git rev-parse --show-toplevel)

# Get commit details
COMMIT_HASH=\$(git rev-parse HEAD)
COMMIT_MESSAGE=\$(git log -1 --pretty=format:"%B")  # Full commit message
AUTHOR=\$(git log -1 --pretty=format:"%an")
DATE=\$(git log -1 --pretty=format:"%ad" --date=iso)
BRANCH_NAME=\$(git rev-parse --abbrev-ref HEAD)

# Fetch changed files with statuses
CHANGED_FILES=\$(git show --pretty="" --name-status HEAD)

# Skip log update commits
if [[ "\$COMMIT_MESSAGE" == "Update commit logs:"* ]] && [[ "\$COMMIT_HASH" == "\$(git rev-parse HEAD)" ]]; then
  echo "Skipping log update commit."
  exit 0
fi

# Ensure we are in the repository root
cd "\$REPO_ROOT" || { echo "ERROR: Could not navigate to repository root"; exit 1; }

# Define the log directory
LOG_DIR="docs/commit-logs/\$BRANCH_NAME"

# Ensure the directory exists
mkdir -p "\$LOG_DIR" || { echo "ERROR: Could not create directory \$LOG_DIR. Check permissions."; exit 1; }

# Define the log file name with branch structure and shortened hash
SHORT_HASH=\$(echo "\$COMMIT_HASH" | cut -c 1-8)
LOG_FILE="\$LOG_DIR/\$SHORT_HASH.md"

# Write the Markdown log
{
  echo "# Commit Log"
  echo
  echo "---"
  echo
  echo "## Commit Details"
  echo
  echo "- **Commit Hash:**   \\\`\$COMMIT_HASH\\\`"
  echo "- **Branch:**        \\\`\$BRANCH_NAME\\\`"
  echo "- **Author:**        \$AUTHOR"
  echo "- **Date:**          \$DATE"
  echo "- **Message:**"
  echo
  echo "  \$COMMIT_MESSAGE"
  echo
  echo "---"
  echo
  echo "## Changed Files:"
  echo
  while IFS= read -r line; do
    echo "- \\\`\$line\\\`"
  done <<< "\$CHANGED_FILES"
  echo
  echo "---"
} > "\$LOG_FILE"

echo "🎯 Commit Process Started..."
echo
echo "📌 Commit message logged to: \$LOG_FILE"
echo

# Stage the log file
git add "\$LOG_FILE"
if [ \$? -ne 0 ]; then
  echo "ERROR: Failed to stage \$LOG_FILE"
  exit 1
fi
echo "✅ Successfully staged: \$LOG_FILE"

# Update branch-specific README.md
export BRANCH_NAME="\$BRANCH_NAME"  # Pass branch name to the script
bash "\$REPO_ROOT/scripts/post-commit/update-readme.sh"

# Run the Python script to generate the timeline
python3 "\$REPO_ROOT/scripts/post-commit/generate_git_timeline.py" || { echo "Python script failed!"; exit 1; }

# Check if timeline was generated correctly
TIMELINE_FILE="\$REPO_ROOT/docs/commit-logs/\$BRANCH_NAME/git_timeline_report.md"

if [ ! -f "\$TIMELINE_FILE" ]; then
    echo "ERROR: git_timeline_report.md was not generated."
    exit 1
fi

# Commit the log file if there are changes
if ! git diff --cached --quiet; then
  git commit --quiet -m "Update commit logs: \$COMMIT_HASH"
  echo "DEBUG: Successfully committed staged files."
fi

# Optional Push: Controlled by an environment variable
if [ "\$GIT_AUTO_PUSH" == "true" ]; then
  git push origin "\$BRANCH_NAME"
  echo "DEBUG: Successfully pushed changes to remote."
else
  echo "🚀 [INFO] Auto-push disabled. Skipping push step."
fi
EOF
    chmod +x .git/hooks/post-commit
}

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Check hook status
check_hook_status
hook_status=$?

if [ $hook_status -eq 0 ]; then
    echo -e "${GREEN}✅ Git hooks already installed and up-to-date (v${EXPECTED_VERSION})${NC}"
elif [ $hook_status -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Git hooks exist but are a different version${NC}"
    echo "   Your hook might have custom modifications or be outdated"
    read -p "   Replace with standard hook v${EXPECTED_VERSION}? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_post_commit_hook
        echo -e "${GREEN}✅ Updated post-commit hook to v${EXPECTED_VERSION}${NC}"
    else
        echo "Keeping existing hook"
    fi
else
    echo -e "${YELLOW}📝 Installing post-commit hook v${EXPECTED_VERSION}...${NC}"
    create_post_commit_hook
    echo -e "${GREEN}✅ Installed post-commit hook${NC}"
fi

# Check for other hooks
echo -e "${GREEN}🔍 Checking for other hooks...${NC}"
for hook in pre-commit prepare-commit-msg commit-msg pre-push; do
    if [ -f ".git/hooks/$hook" ]; then
        echo -e "   ✅ Found $hook hook"
    else
        echo -e "   ⏭️  No $hook hook"
    fi
done

# Set up git config for better commit messages
echo -e "${GREEN}⚙️  Setting up git config...${NC}"

# Check if user.name is set
if [ -z "$(git config user.name)" ]; then
    echo -e "${YELLOW}   No git user.name set${NC}"
    read -p "   Enter your name: " username
    git config user.name "$username"
else
    echo -e "   ✅ Git user: $(git config user.name)"
fi

# Check if user.email is set
if [ -z "$(git config user.email)" ]; then
    echo -e "${YELLOW}   No git user.email set${NC}"
    read -p "   Enter your email: " useremail
    git config user.email "$useremail"
else
    echo -e "   ✅ Git email: $(git config user.email)"
fi

# Set up commit template if exists
if [ -f ".gitmessage" ]; then
    git config commit.template .gitmessage
    echo -e "   ✅ Commit template configured"
fi

# Check Python installation
echo -e "${GREEN}🐍 Checking Python installation...${NC}"
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "   ✅ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "   ✅ Python found: $(python --version)"
else
    echo -e "${RED}   ❌ Python not found! Please install Python 3${NC}"
    echo "   The git hooks require Python to run"
    echo "   Install with:"
    echo "     Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "     macOS: brew install python3"
    echo "     Windows: Download from https://www.python.org/downloads/"
fi

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ] && [ -n "$PYTHON_CMD" ]; then
    echo -e "${GREEN}📦 Installing Python dependencies...${NC}"
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
        echo -e "   ✅ Dependencies installed with pip3"
    elif command -v pip &> /dev/null; then
        pip install -r requirements.txt
        echo -e "   ✅ Dependencies installed with pip"
    else
        echo -e "${YELLOW}   ⚠️  pip not found, skipping dependency installation${NC}"
        echo "   Please install manually: pip install -r requirements.txt"
    fi
else
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}📦 No requirements.txt found${NC}"
    fi
fi

# Final summary
echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo "Git hooks have been installed. They will:"
echo "  📝 Create commit logs in docs/commit-logs/"
echo "  📊 Generate git timeline reports"
echo "  🔄 Update README with latest commits"
echo "  🔒 Prevent recursive commits with lock files"
echo ""
echo "Environment variables:"
echo "  GIT_AUTO_PUSH=true  - Enable automatic push after commits"
echo ""
echo "To test the hooks, make a commit:"
echo "  git add ."
echo '  git commit -m "test: Testing git hooks"'
echo ""
echo "If hooks don't run, check:"
echo "  - File permissions: ls -la .git/hooks/"
echo "  - Python installation: which python3"
echo "  - Script files exist in scripts/post-commit/"
echo ""
echo -e "${YELLOW}Note: This is setup-githooks v${EXPECTED_VERSION}${NC}"