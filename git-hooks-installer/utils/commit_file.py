import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def commit_file(repo_path: Path, file_path: str, message: str) -> bool:
    """
    Stage and commit a file in the given repository.

    Args:
        repo_path (Path): Path to the git repository.
        file_path (str): Path to the file to commit, relative to repo root.
        message (str): Commit message.

    Returns:
        bool: True if commit succeeded, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "-C", str(repo_path), "add", file_path],
            check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["git", "-C", str(repo_path), "commit", "-m", message],
            check=True, capture_output=True, text=True
        )
        logger.info("Committed %s with message: %s", file_path, message)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to commit %s: %s", file_path, e.stderr)
        return False
