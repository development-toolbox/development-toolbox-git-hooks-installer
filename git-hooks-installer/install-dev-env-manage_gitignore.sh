#!/usr/bin/env bash
# install-dev-env-manage_gitignore.sh
# Set up local development environment for manage_gitignore.py

set -e

echo "🛠️  Creating virtual environment..."
python3 -m venv .venv

echo "✅ Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements-manage-gitignore.txt

echo "✅ Done. Environment is ready."
echo "To activate it later, run: source .venv/bin/activate"
echo "To deactivate, just run: deactivate"