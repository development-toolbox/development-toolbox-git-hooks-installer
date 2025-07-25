import subprocess

def test_git_version():
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    assert "git version" in result.stdout
