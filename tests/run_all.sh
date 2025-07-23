#!/bin/bash
set -e

mkdir -p tests/results

# Black: HTML report via blacken-docs (not native, so use txt for now)
black git-hooks-installer --check --diff > tests/results/black.txt 2>&1 || true

# isort: HTML via txt2html (workaround, since isort has no native HTML)
isort git-hooks-installer --check-only --diff > tests/results/isort.txt 2>&1 || true

# Ruff: HTML via txt2html (workaround, since ruff has no native HTML)
ruff git-hooks-installer > tests/results/ruff.txt 2>&1 || true

# Flake8: Native HTML report
flake8 git-hooks-installer --htmldir=tests/results/flake8_html > tests/results/flake8.txt 2>&1 || true

# Pylint: JSON to HTML
pylint git-hooks-installer > tests/results/pylint.txt 2>&1 || true
pylint-json2html -f json -o tests/results/pylint.html tests/results/pylint.json || true

# Pytest: Native HTML report
pytest --maxfail=1 --disable-warnings --tb=short git-hooks-installer > tests/results/pytest.txt 2>&1 || true

# Bandit: HTML report
bandit -r git-hooks-installer -f html -o tests/results/bandit.html > tests/results/bandit.txt 2>&1 || true

# mypy: HTML via txt2html (workaround)
mypy git-hooks-installer > tests/results/mypy.txt 2>&1 || true

# Convert txt reports to HTML for black, isort, ruff, mypy
for tool in black isort ruff mypy; do
    if [ -f tests/results/$tool.txt ]; then
        ansi2html < tests/results/$tool.txt > tests/results/$tool.html || true
    fi
done

echo "All reports generated in tests/results/"
