#!/bin/bash
set -e

# Detect OS name for results subfolder (set by Docker Compose or fallback to uname)
OS_NAME="${OS_NAME:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
RESULTS_DIR="tests/results/${OS_NAME}"

mkdir -p "${RESULTS_DIR}"

# Black: HTML report via blacken-docs (not native, so use txt for now)
black git-hooks-installer --check --diff > "${RESULTS_DIR}/black.txt" 2>&1 || true

# isort: HTML via txt2html (workaround, since isort has no native HTML)
isort git-hooks-installer --check-only --diff > "${RESULTS_DIR}/isort.txt" 2>&1 || true

# Ruff: HTML via txt2html (workaround, since ruff has no native HTML)
ruff check git-hooks-installer > "${RESULTS_DIR}/ruff.txt" 2>&1 || true

# Flake8: Native HTML report
mkdir -p "${RESULTS_DIR}/flake8_html"
flake8 . --format=html --htmldir="${RESULTS_DIR}/flake8_html" || true

# If flake8_html is empty, create a placeholder index.html
if [ ! -f "${RESULTS_DIR}/flake8_html/index.html" ]; then
    cat > "${RESULTS_DIR}/flake8_html/index.html" <<EOF
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><title>flake8 (HTML)</title></head>
<body>
  <h2>No flake8 issues found 🎉</h2>
</body>
</html>
EOF
fi

# Pylint: JSON to HTML
pylint git-hooks-installer --output-format=json > "${RESULTS_DIR}/pylint.json" 2>&1 || true
pylint-json2html -f json -o "${RESULTS_DIR}/pylint.html" "${RESULTS_DIR}/pylint.json" || true

# Pytest: Native HTML report
pytest --maxfail=1 --disable-warnings --tb=short git-hooks-installer > "${RESULTS_DIR}/pytest.txt" 2>&1 || true

# Bandit: HTML report
bandit -r git-hooks-installer -f html -o "${RESULTS_DIR}/bandit.html" > "${RESULTS_DIR}/bandit.txt" 2>&1 || true

# mypy: HTML via txt2html (workaround)
mypy git-hooks-installer > "${RESULTS_DIR}/mypy.txt" 2>&1 || true

# Convert txt reports to HTML for black, isort, ruff, mypy
for tool in black isort ruff mypy; do
    if [ -f "${RESULTS_DIR}/$tool.txt" ]; then
        ansi2html < "${RESULTS_DIR}/$tool.txt" > "${RESULTS_DIR}/$tool.html" || true
    fi
done

# Generate a simple index.html for this OS
cat > "${RESULTS_DIR}/index.html" <<EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Test Results - ${OS_NAME}</title>
</head>
<body>
  <h1>Test Results for <code>${OS_NAME}</code></h1>
  <ul>
    <li><a href="black.html">black</a></li>
    <li><a href="isort.html">isort</a></li>
    <li><a href="ruff.html">ruff</a></li>
    <li><a href="flake8_html/index.html">flake8 (HTML)</a></li>
    <li><a href="pylint.html">pylint</a></li>
    <li><a href="pytest.html">pytest</a></li>
    <li><a href="bandit.html">bandit</a></li>
    <li><a href="mypy.html">mypy</a></li>
    <li><a href="black.txt">black.txt</a></li>
    <li><a href="isort.txt">isort.txt</a></li>
    <li><a href="ruff.txt">ruff.txt</a></li>
    <li><a href="flake8.txt">flake8.txt</a></li>
    <li><a href="pylint.txt">pylint.txt</a></li>
    <li><a href="pytest.txt">pytest.txt</a></li>
    <li><a href="bandit.txt">bandit.txt</a></li>
    <li><a href="mypy.txt">mypy.txt</a></li>
  </ul>
</body>
</html>
EOF

echo "All reports generated in ${RESULTS_DIR}/"
echo "Current directory: $(pwd)"
ls -l git-hooks-installer
