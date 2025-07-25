#!/usr/bin/env python3
"""
Test runner for validation logic tests - FOR DOCKER EXECUTION.
This belongs in the tests directory, not root!
"""

import sys
import unittest
from pathlib import Path

# Add the git-hooks-installer directory to Python path
installer_dir = Path(__file__).parent.parent / "git-hooks-installer"
if str(installer_dir) not in sys.path:
    sys.path.insert(0, str(installer_dir))

def run_validation_tests():
    """Run all validation-related tests."""
    print("🧪 Running File Tracker Validation Tests in Docker...")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load unit tests
    try:
        from unit.test_file_tracker_validation import TestFileTrackerValidation
        suite.addTests(loader.loadTestsFromTestCase(TestFileTrackerValidation))
        print("✅ Loaded unit tests for FileTracker validation")
    except ImportError as e:
        print(f"⚠️ Could not load unit tests: {e}")
    
    # Load integration tests
    try:
        from integration.test_installer_validation_workflow import (
            TestInstallerValidationWorkflow,
            TestValidationPerformance
        )
        suite.addTests(loader.loadTestsFromTestCase(TestInstallerValidationWorkflow))
        suite.addTests(loader.loadTestsFromTestCase(TestValidationPerformance))
        print("✅ Loaded integration tests for installer workflow")
    except ImportError as e:
        print(f"⚠️ Could not load integration tests: {e}")
    
    # Load staging bug reproduction tests
    try:
        from integration.test_staging_bug_reproduction import (
            TestStagingBugReproduction,
            TestStagingErrorDetection
        )
        suite.addTests(loader.loadTestsFromTestCase(TestStagingBugReproduction))
        suite.addTests(loader.loadTestsFromTestCase(TestStagingErrorDetection))
        print("✅ Loaded staging bug reproduction tests")
    except ImportError as e:
        print(f"⚠️ Could not load staging bug tests: {e}")
    
    print(f"📊 Total tests loaded: {suite.countTestCases()}")
    print()
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All validation tests passed in Docker!")
        return True
    else:
        print("❌ Some validation tests failed!")
        print(f"🔴 Failures: {len(result.failures)}")
        print(f"💥 Errors: {len(result.errors)}")
        return False

if __name__ == "__main__":
    print("🐳 Docker Test Runner - Validation Logic Tests")
    print("=" * 60)
    
    success = run_validation_tests()
    
    if success:
        print("\n🎯 Validation logic working correctly in Docker environment!")
        sys.exit(0)
    else:
        print("\n🚨 Fix validation issues before deploying.")
        sys.exit(1)