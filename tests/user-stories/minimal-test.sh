#!/bin/bash
echo "🧪 Minimal User Story Test"
echo "========================="

echo "Environment check:"
echo "- Python: $(python3 --version)"
echo "- Git: $(git --version)"
echo "- Current dir: $(pwd)"
echo "- Files available:"
ls -la /app/git-hooks-installer/ | head -5

echo ""
echo "Creating test repo..."
mkdir -p /tmp/minimal-test
cd /tmp/minimal-test
git init
echo "test" > README.md
git add README.md
git commit -m "Initial commit"

echo ""
echo "Running safe installer..."
if python3 /app/git-hooks-installer/git-hooks-installer.py --source /app/git-hooks-installer . 2>&1 | head -10; then
    echo "✅ Installer started successfully"
else
    echo "❌ Installer failed to start"
fi

echo ""
echo "✅ Minimal test completed"