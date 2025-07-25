#!/bin/bash
# Script to run git-hooks-installer FIXES tests in Docker container

set -e

echo "=== Git Hooks Installer FIXES Test Runner ==="
echo "Testing the FIXED version of the installer..."
echo ""

# Ensure results directory exists
mkdir -p tests/installer-results

# Run the fix tests
docker-compose -f tests/docker/docker-compose.installer-fix-test.yml up --build --abort-on-container-exit

# Show summary
echo ""
echo "=== FIXES TEST SUMMARY ==="

if [ -f "tests/installer-results/latest-run-foldername.info" ]; then
    LATEST_FOLDER=$(cat tests/installer-results/latest-run-foldername.info)
    echo "Latest test results: tests/installer-results/$LATEST_FOLDER/"
    
    if [ -f "tests/installer-results/$LATEST_FOLDER/test-summary.json" ]; then
        echo ""
        echo "Test Summary:"
        cat "tests/installer-results/$LATEST_FOLDER/test-summary.json"
        echo ""
        
        # Extract validation errors count
        VALIDATION_ERRORS=$(cat "tests/installer-results/$LATEST_FOLDER/test-summary.json" | grep '"validation_errors"' | cut -d: -f2 | tr -d ' ,')
        
        if [ "$VALIDATION_ERRORS" = "0" ]; then
            echo "🎉 SUCCESS: All fixes working correctly!"
            echo "✅ No validation errors found"
        else
            echo "❌ FAILURE: $VALIDATION_ERRORS validation errors found"
            echo "Check detailed results in: tests/installer-results/$LATEST_FOLDER/"
        fi
    fi
else
    echo "No test results found"
fi

echo ""
echo "For detailed validation results, see:"
echo "  tests/installer-results/\$LATEST_FOLDER/validation-detailed.txt"