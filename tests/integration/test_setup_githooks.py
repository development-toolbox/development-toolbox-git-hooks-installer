import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT_PATH = Path("git-hooks-installer/developer-setup/setup_githooks.py")

@pytest.fixture
def temp_git_repo_with_template(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    template_dir = repo_dir / "developer-setup" / "templates"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "post-commit"
    template_file.write_text("#!/bin/sh\n# setup_githooks.py v0.5\n")
    yield repo_dir, template_dir, template_file

def run_script(args, cwd):
    return subprocess.run(
        ["python", str(SCRIPT_PATH)] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

def test_check_only_mode(temp_git_repo_with_template):
    repo_dir, template_dir, _ = temp_git_repo_with_template
    hooks_dir = repo_dir / ".git" / "hooks"
    result = run_script(["--template-dir", str(template_dir), "--check-only"], repo_dir)
    assert "would install" in result.stdout or "would keep" in result.stdout or "would update" in result.stdout
    assert "No changes were made" in result.stdout
    assert not (hooks_dir / "post-commit").exists()

def test_install_mode(temp_git_repo_with_template):
    repo_dir, template_dir, _ = temp_git_repo_with_template
    hooks_dir = repo_dir / ".git" / "hooks"
    result = run_script(["--template-dir", str(template_dir)], repo_dir)
    assert "Installed post-commit hook from template" in result.stdout
    hook_path = hooks_dir / "post-commit"
    assert hook_path.exists()
    content = hook_path.read_text()
    assert "# setup_githooks.py v0.5" in content

def test_force_update(temp_git_repo_with_template):
    repo_dir, template_dir, template_file = temp_git_repo_with_template
    hooks_dir = repo_dir / ".git" / "hooks"
    # First install
    run_script(["--template-dir", str(template_dir)], repo_dir)
    # Modify hook to simulate different version
    hook_path = hooks_dir / "post-commit"
    hook_path.write_text("#!/bin/sh\n# setup_githooks.py v0.4\n")
    # Now force update
    result = run_script(["--template-dir", str(template_dir), "--force"], repo_dir)
    assert "Installed post-commit hook from template" in result.stdout or "Updated" in result.stdout
    assert "# setup_githooks.py v0.5" in hook_path.read_text()

def test_info_option(temp_git_repo_with_template):
    repo_dir, template_dir, _ = temp_git_repo_with_template
    result = run_script(["--info"], repo_dir)
    assert "Git Hooks Installer v0.5" in result.stdout
    assert "Project URL" in result.stdout

def test_version_option(temp_git_repo_with_template):
    repo_dir, template_dir, _ = temp_git_repo_with_template
    result = run_script(["--version"], repo_dir)
    assert "0.5" in result.stdout

def test_help_option(temp_git_repo_with_template):
    repo_dir, template_dir, _ = temp_git_repo_with_template
    result = run_script(["-h"], repo_dir)
    assert "usage:" in result.stdout
    assert "--check-only" in result.stdout

def test_reports_generated(temp_git_repo_with_template):
    repo_dir, template_dir, _ = temp_git_repo_with_template
    # Simulate running the test runner
    subprocess.run(["bash", "tests/run_all.sh"], cwd=repo_dir, check=False)
    results_dir = repo_dir / "tests" / "results"
    assert (results_dir / "flake8_html" / "index.html").exists()
    assert (results_dir / "pylint.html").exists()
    assert (results_dir / "pytest.html").exists()
    assert (results_dir / "bandit.html").exists()
    assert (results_dir / "black.html").exists()
    assert (results_dir / "isort.html").exists()
    assert (results_dir / "ruff.html").exists()
    assert (results_dir / "mypy.html").exists()
    # Optionally, check that the reports are not empty
    for report in [
        results_dir / "flake8_html" / "index.html",
        results_dir / "pylint.html",
        results_dir / "pytest.html",
        results_dir / "bandit.html",
        results_dir / "black.html",
        results_dir / "isort.html",
        results_dir / "ruff.html",
        results_dir / "mypy.html",
    ]:
        assert report.stat().st_size > 0
