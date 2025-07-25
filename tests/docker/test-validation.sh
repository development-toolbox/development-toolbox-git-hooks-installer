#!/bin/bash
set -e

# Configuration
RESULTS_BASE="/app/tests/validation-results"
OS_NAME=$(cat /etc/os-release | grep "^ID=" | cut -d= -f2 | tr -d '"')
TEST_TYPE="validation"

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
echo "Validation test results will be saved to: $FULL_PATH"

# Start logging
LOG_FILE="$FULL_PATH/validation-tests.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=== Git Hooks Installer - Validation Logic Tests ==="
echo "Date: $(date)"
echo "OS: $OS_NAME"
echo "Test Type: $TEST_TYPE"
echo "Python Version: $(python --version 2>&1)"
echo "Git Version: $(git --version)"
echo ""

# Set Python path
export PYTHONPATH="/app/git-hooks-installer:/app/tests:$PYTHONPATH"

# Change to tests directory
cd /app/tests

echo "=== Running Validation Logic Tests ==="
TEST_START=$(date +%s)

# Run the validation tests
if python run_validation_tests.py; then
    TEST_STATUS="success"
    TEST_EXIT_CODE=0
    echo "✅ All validation tests passed!"
else
    TEST_STATUS="failed"
    TEST_EXIT_CODE=$?
    echo "❌ Some validation tests failed!"
fi

TEST_END=$(date +%s)
TEST_DURATION=$((TEST_END - TEST_START))

echo ""
echo "Validation tests completed with status: $TEST_STATUS (exit code: $TEST_EXIT_CODE)"
echo "Duration: ${TEST_DURATION}s"

# Generate test summary JSON
cat > "$FULL_PATH/validation-test-summary.json" << EOF
{
    "test_run_id": "$RUN_DIR",
    "date": "$(date -Iseconds)",
    "os": "$OS_NAME",
    "test_type": "$TEST_TYPE",
    "python_version": "$(python --version 2>&1)",
    "git_version": "$(git --version)",
    "status": "$TEST_STATUS",
    "exit_code": $TEST_EXIT_CODE,
    "duration_seconds": $TEST_DURATION,
    "test_categories": {
        "unit_tests": "FileTracker validation logic",
        "integration_tests": "Full installer workflow validation",
        "performance_tests": "Validation with many files"
    },
    "test_scenarios_covered": [
        "Path separator handling (Windows/Unix)",
        "Unicode/emoji filename support", 
        "False positive detection and elimination",
        "Unexpected file detection",
        "Missing file warning handling",
        "Full installer workflow validation",
        "Manifest file inclusion validation",
        "Performance with large file counts"
    ]
}
EOF

# Create text file with latest test folder name
cd "$RESULTS_BASE"
echo "$RUN_DIR" > latest-validation-run.info

echo ""
echo "=== Validation Test Complete ==="
echo "Results saved to: $FULL_PATH"
echo "Exit code: $TEST_EXIT_CODE"

# If tests failed, show some diagnostics
if [ "$TEST_STATUS" = "failed" ]; then
    echo ""
    echo "=== Diagnostic Information ==="
    echo "Python path: $PYTHONPATH"
    echo "Current directory: $(pwd)"
    echo "Available Python modules:"
    python -c "import sys; print('\n'.join(sys.path))" || true
    echo ""
    echo "Test files in tests directory:"
    find /app/tests -name "*.py" | head -10
fi

exit $TEST_EXIT_CODE