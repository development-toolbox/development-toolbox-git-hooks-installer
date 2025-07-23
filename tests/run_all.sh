#!/bin/bash
set -e

mkdir -p tests/results

echo "Running black..."
black --check . | tee tests/results/black.txt

echo "Running isort..."
isort --check-only . | tee tests/results/isort.txt

echo "Running ruff..."
ruff . | tee tests/results/ruff.txt

echo "Running flake8..."
flake8 . | tee tests/results/flake8.txt

echo "Running pylint..."
pylint $(find . -name "*.py" ! -path "./tests/*") | tee tests/results/pylint.txt

echo "Running mypy..."
mypy . | tee tests/results/mypy.txt

echo "Running bandit..."
bandit -r . | tee tests/results/bandit.txt

echo "Running pytest (unit)..."
pytest tests/unit --cov=your_package_name --html=tests/results/unit-report.html --self-contained-html | tee tests/results/pytest-unit.txt

echo "Running pytest (integration)..."
pytest tests/integration --cov=your_package_name --html=tests/results/integration-report.html --self-contained-html | tee tests/results/pytest-integration.txt
