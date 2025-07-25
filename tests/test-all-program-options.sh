#!/bin/bash
set -e

# Comprehensive test suite for all program options

echo "🧪 Testing All Program Options"
echo "==============================="

INSTALLER="/app/git-hooks-installer/git-hooks-installer.py"
TEMP_BASE=$(mktemp -d)
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# Helper functions
log_test() {
    ((TEST_COUNT++))
    echo ""
    echo "Test $TEST_COUNT: $1"
    echo "-------------------"
}

pass_test() {
    ((PASS_COUNT++))
    echo "✅ PASS: $1"
}

fail_test() {
    ((FAIL_COUNT++))
    echo "❌ FAIL: $1"
}

create_test_repo() {
    local name=$1
    local repo_path="$TEMP_BASE/$name"
    mkdir -p "$repo_path"
    cd "$repo_path"
    git init
    echo "# Test repo $name" > README.md
    git add README.md
    git commit -m "Initial commit"
    echo "$repo_path"
}

# Test 1: Help option (-h and --help)
log_test "Help options (-h and --help)"
if python3 "$INSTALLER" -h > /dev/null 2>&1; then
    pass_test "Short help flag -h works"
else
    fail_test "Short help flag -h failed"
fi

if python3 "$INSTALLER" --help > /dev/null 2>&1; then
    pass_test "Long help flag --help works"
else
    fail_test "Long help flag --help failed"
fi

# Test 2: Check option (-c and --check)
log_test "Check options (-c and --check)"
REPO_PATH=$(create_test_repo "check-test")

# Both should fail (no hooks installed)
if python3 "$INSTALLER" -c; then
    fail_test "Short check flag -c should have failed (no hooks)"
else
    pass_test "Short check flag -c correctly reported no hooks"
fi

if python3 "$INSTALLER" --check; then
    fail_test "Long check flag --check should have failed (no hooks)"
else
    pass_test "Long check flag --check correctly reported no hooks"
fi

# Test 3: Force option (-f and --force)
log_test "Force options (-f and --force)"
REPO_PATH=$(create_test_repo "force-test")

# Install once
python3 "$INSTALLER" . > /dev/null 2>&1 || true

# Test short flag - should work even if "up to date"
if python3 "$INSTALLER" -f .; then
    pass_test "Short force flag -f works"
else
    fail_test "Short force flag -f failed"
fi

# Test long flag
REPO_PATH=$(create_test_repo "force-test-2")
python3 "$INSTALLER" . > /dev/null 2>&1 || true

if python3 "$INSTALLER" --force .; then
    pass_test "Long force flag --force works"
else
    fail_test "Long force flag --force failed"
fi

# Test 4: Verbose option (-v and --verbose)
log_test "Verbose options (-v and --verbose)"
REPO_PATH=$(create_test_repo "verbose-test")

# Test short flag - should produce more output
if python3 "$INSTALLER" -v . 2>&1 | grep -q "INFO"; then
    pass_test "Short verbose flag -v produces INFO output"
else
    fail_test "Short verbose flag -v did not produce INFO output"
fi

REPO_PATH=$(create_test_repo "verbose-test-2")
if python3 "$INSTALLER" --verbose . 2>&1 | grep -q "INFO"; then
    pass_test "Long verbose flag --verbose produces INFO output"
else
    fail_test "Long verbose flag --verbose did not produce INFO output"
fi

# Test 5: Debug option (-d and --debug)
log_test "Debug options (-d and --debug)"
REPO_PATH=$(create_test_repo "debug-test")

# Test short flag - should produce DEBUG output
if python3 "$INSTALLER" -d . 2>&1 | grep -q "DEBUG\|Executing secure Git command"; then
    pass_test "Short debug flag -d produces DEBUG output"
else
    fail_test "Short debug flag -d did not produce DEBUG output"
fi

REPO_PATH=$(create_test_repo "debug-test-2")
if python3 "$INSTALLER" --debug . 2>&1 | grep -q "DEBUG\|Executing secure Git command"; then
    pass_test "Long debug flag --debug produces DEBUG output"
else
    fail_test "Long debug flag --debug did not produce DEBUG output"
fi

# Test 6: No-CI option (--no-ci)
log_test "No-CI option (--no-ci)"
REPO_PATH=$(create_test_repo "no-ci-test")

if python3 "$INSTALLER" --no-ci .; then
    pass_test "No-CI flag --no-ci works"
else
    fail_test "No-CI flag --no-ci failed"
fi

# Test 7: Combination flags
log_test "Combination flags"
REPO_PATH=$(create_test_repo "combo-test")

if python3 "$INSTALLER" -vf .; then
    pass_test "Combined flags -vf works"
else
    fail_test "Combined flags -vf failed"
fi

REPO_PATH=$(create_test_repo "combo-test-2")
if python3 "$INSTALLER" -d --no-ci .; then
    pass_test "Mixed flags -d --no-ci works"
else
    fail_test "Mixed flags -d --no-ci failed"
fi

# Test 9: Invalid options
log_test "Invalid options (should fail gracefully)"

if python3 "$INSTALLER" --invalid-option 2>/dev/null; then
    fail_test "Invalid option should have failed"
else
    pass_test "Invalid option correctly rejected"
fi

if python3 "$INSTALLER" -x 2>/dev/null; then
    fail_test "Invalid short option should have failed"
else
    pass_test "Invalid short option correctly rejected"
fi

# Test 8: Positional argument
log_test "Positional argument (target path)"
REPO_PATH=$(create_test_repo "positional-test")
PARENT_DIR=$(dirname "$REPO_PATH")
REPO_NAME=$(basename "$REPO_PATH")

cd "$PARENT_DIR"
if python3 "$INSTALLER" "$REPO_NAME"; then
    pass_test "Positional target argument works"
else
    fail_test "Positional target argument failed"
fi

# Test 9: Default behavior (no arguments)
log_test "Default behavior (current directory)"
REPO_PATH=$(create_test_repo "default-test")

if python3 "$INSTALLER"; then
    pass_test "Default behavior (current directory) works"
else
    fail_test "Default behavior (current directory) failed"
fi

# Cleanup
cd /
rm -rf "$TEMP_BASE"

# Summary
echo ""
echo "==============================="
echo "📊 TEST SUMMARY"
echo "==============================="
echo "Total Tests: $TEST_COUNT"
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo ""
    echo "🎉 ALL PROGRAM OPTION TESTS PASSED!"
    echo "✅ All argument combinations work correctly"
    exit 0
else
    echo ""
    echo "❌ Some tests failed - see details above"
    exit 1
fi