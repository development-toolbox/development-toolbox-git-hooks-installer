#!/bin/bash
# Script to run git-hooks-installer tests in Docker containers

set -e

echo "=== Git Hooks Installer Test Runner ==="
echo "Running installer tests across multiple OS environments..."
echo ""

# Ensure results directory exists
mkdir -p tests/installer-results

# Run the tests
docker-compose -f tests/docker/docker-compose.installer-test.yml up --build --abort-on-container-exit

# Show summary
echo ""
echo "=== Test Summary ==="

if [ -f "tests/installer-results/latest-run-foldername.info" ]; then
    LATEST_FOLDER=$(cat tests/installer-results/latest-run-foldername.info)
    echo "Latest test results: tests/installer-results/$LATEST_FOLDER/"
    
    if [ -f "tests/installer-results/$LATEST_FOLDER/test-summary.json" ]; then
        echo ""
        echo "Test Summary:"
        cat "tests/installer-results/$LATEST_FOLDER/test-summary.json"
    fi
else
    echo "No test results found"
fi

echo ""
echo "All test runs:"
ls -la tests/installer-results/ | grep -v "^total" | grep -v "latest"