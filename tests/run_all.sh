#!/bin/bash
set -e

mkdir -p tests/results

# Black: HTML report via blacken-docs (not native, so use txt for now)
black . --check --diff > tests/results/black.txt 2>&1 || true

# isort: HTML via txt2html (workaround, since isort has no native HTML)
isort . --check-only --diff > tests/results/isort.txt 2>&1 || true

# Ruff: HTML via txt2html (workaround, since ruff has no native HTML)
ruff check . > tests/results/ruff.txt 2>&1 || true

# Flake8: Native HTML report
flake8 . --format=html --htmldir=tests/results/flake8_html || true

# Pylint: JSON to HTML
pylint $(find . -name "*.py") --output-format=json > tests/results/pylint.json || true
pylint-json2html -f json -o tests/results/pylint.html tests/results/pylint.json || true

# Pytest: Native HTML report
pytest --maxfail=1 --disable-warnings --html=tests/results/pytest.html --self-contained-html || true

# Bandit: HTML report
bandit -r . -f html -o tests/results/bandit.html || true

# mypy: HTML via txt2html (workaround)
mypy . > tests/results/mypy.txt 2>&1 || true

# Convert txt reports to HTML for black, isort, ruff, mypy
for tool in black isort ruff mypy; do
    if [ -f tests/results/$tool.txt ]; then
        ansi2html < tests/results/$tool.txt > tests/results/$tool.html || true
    fi
done

echo "All reports generated in tests/results/"
