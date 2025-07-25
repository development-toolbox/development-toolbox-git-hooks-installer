#!/bin/bash
set -e

# Debug script to test User Story environment setup
echo "🔍 Debug: User Story Test Environment Setup"
echo "=========================================="

echo "Debug: Python version:"
python3 --version

echo "Debug: Current directory:"
pwd

echo "Debug: Available files in git-hooks-installer:"
ls -la /app/git-hooks-installer/

echo "Debug: Testing basic git operations..."
mkdir -p /tmp/test-repo
cd /tmp/test-repo
git init
echo "test" > README.md
git add README.md
git commit -m "Initial commit"
echo "✅ Debug: Git test successful"

echo "Debug: Testing safe installer imports..."
python3 -c "
import sys
sys.path.append('/app/git-hooks-installer')
print('Available Python modules in git-hooks-installer:')
import os
for f in os.listdir('/app/git-hooks-installer'):
    if f.endswith('.py'):
        print(f'  {f}')
        
try:
    from repository_validator import RepositoryValidator
    print('✅ repository_validator imported successfully')
except Exception as e:
    print(f'❌ repository_validator import failed: {e}')

try:
    from file_tracker import SafeFileTracker
    print('✅ file_tracker imported successfully')
except Exception as e:
    print(f'❌ file_tracker import failed: {e}')
"

echo "Debug: Testing safe installer help..."
python3 /app/git-hooks-installer/git-hooks-installer.py --help

echo "✅ Debug: All environment checks completed successfully"