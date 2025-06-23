#!/usr/bin/env python3
# manage_gitignore.py
"""
Safely manage .gitignore entries without duplicates or data loss.
Can be used standalone or imported as a module.
"""
import sys
from pathlib import Path
from typing import List, Set, Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class GitIgnoreManager:
    """Manage .gitignore file entries safely."""
    
    # Default entries for git hooks installation
    DEFAULT_ENTRIES = """
############################
# 🐍 PYTHON
############################
**/__pycache__/
*.py[cod]
*$py.class

# Virtual environments
env/
venv/
.venv/
**/env/
**/venv/
**/.venv/

# Build / distribution artifacts
build/
dist/
*.egg-info/
.eggs/
*.egg

############################
# 💻 VISUAL STUDIO CODE
############################
.vscode/

############################
# 🔒 SECRETS / ENV FILES
############################
.env
**/.env
.env.*
**/.env.*
!.env.example

############################
# 📝 LOCAL COMMIT MESSAGE DRAFTS & LOGS
############################
# Ignore all commit-* files everywhere in the repo,
# except those in docs/commit-examples/ and docs/commit-logs/
commit-*
**/commit-*

# Never ignore documentation commit logs or commit-examples
!docs/commit-examples/commit-*
!docs/commit-logs/
!docs/commit-logs/**
"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.gitignore_path = repo_path / ".gitignore"
        self.existing_patterns: Set[str] = set()
        self.existing_content: List[str] = []
        
    def normalize_pattern(self, pattern: str) -> str:
        """
        Normalize a pattern for comparison.
        Handles different variations of the same pattern.
        """
        pattern = pattern.strip()
        
        # Remove trailing slashes for directories
        if pattern.endswith('/') and not pattern.endswith('**/'):
            pattern = pattern.rstrip('/')
            
        # Normalize **/__pycache__/ vs __pycache__/
        if pattern.startswith('**/'):
            alt_pattern = pattern[3:]  # Remove **/
            return alt_pattern if alt_pattern else pattern
            
        return pattern
    
    def patterns_equivalent(self, pattern1: str, pattern2: str) -> bool:
        """
        Check if two patterns are equivalent.
        E.g., '__pycache__/' and '**/__pycache__/' match the same files.
        """
        # Direct match
        if pattern1 == pattern2:
            return True
            
        # Normalize and compare
        norm1 = self.normalize_pattern(pattern1)
        norm2 = self.normalize_pattern(pattern2)
        
        if norm1 == norm2:
            return True
            
        # Check with/without **/ prefix
        if pattern1.startswith('**/') and pattern1[3:] == pattern2:
            return True
        if pattern2.startswith('**/') and pattern2[3:] == pattern1:
            return True
            
        # Check with/without trailing slash
        if pattern1.rstrip('/') == pattern2.rstrip('/'):
            return True
            
        return False
    
    def load_existing_gitignore(self) -> None:
        """Load and parse existing .gitignore file."""
        if not self.gitignore_path.exists():
            logger.info("No existing .gitignore found")
            return
            
        with open(self.gitignore_path, 'r', encoding='utf-8') as f:
            self.existing_content = f.readlines()
            
        # Extract patterns (non-empty, non-comment lines)
        for line in self.existing_content:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                self.existing_patterns.add(stripped)
                
        logger.info(f"Loaded {len(self.existing_patterns)} existing patterns from .gitignore")
    
    def pattern_exists(self, pattern: str) -> bool:
        """Check if a pattern or equivalent already exists."""
        pattern = pattern.strip()
        
        # Check for exact match
        if pattern in self.existing_patterns:
            return True
            
        # Check for equivalent patterns
        for existing in self.existing_patterns:
            if self.patterns_equivalent(pattern, existing):
                logger.debug(f"Pattern '{pattern}' equivalent to existing '{existing}'")
                return True
                
        return False
    
    def add_entries(self, entries: Optional[str] = None) -> int:
        """
        Add entries to .gitignore, avoiding duplicates.
        Returns number of new patterns added.
        """
        if entries is None:
            entries = self.DEFAULT_ENTRIES
            
        # Load existing file
        self.load_existing_gitignore()
        
        # Parse new entries
        new_lines = entries.strip().split('\n')
        patterns_to_add = []
        section_headers = []
        current_section = []
        added_count = 0
        
        for line in new_lines:
            stripped = line.strip()
            
            # Empty line
            if not stripped:
                if current_section and any(p[1] for p in current_section):
                    # Only add empty line if we have non-duplicate patterns
                    patterns_to_add.append('')
                continue
                
            # Comment/header line
            if stripped.startswith('#'):
                current_section.append((line, False))
                continue
                
            # Pattern line
            if not self.pattern_exists(stripped):
                current_section.append((line, True))
                added_count += 1
                logger.info(f"✅ Will add pattern: {stripped}")
            else:
                logger.debug(f"⏭️  Skipping duplicate: {stripped}")
                current_section.append((line, False))
        
        # Process the last section
        if current_section:
            has_new_patterns = any(is_new for _, is_new in current_section)
            if has_new_patterns:
                for line, is_new in current_section:
                    patterns_to_add.append(line.rstrip())
        
        # Write to file if we have new patterns
        if added_count > 0:
            self.write_gitignore(patterns_to_add)
            logger.info(f"✅ Added {added_count} new patterns to .gitignore")
        else:
            logger.info("✅ All patterns already exist in .gitignore")
            
        return added_count
    
    def write_gitignore(self, new_patterns: List[str]) -> None:
        """Write updated content to .gitignore file."""
        # Read existing content as string to preserve formatting
        existing_text = ''
        if self.gitignore_path.exists():
            with open(self.gitignore_path, 'r', encoding='utf-8') as f:
                existing_text = f.read()
        
        # Ensure existing content ends with newline
        if existing_text and not existing_text.endswith('\n'):
            existing_text += '\n'
            
        # Add separator if file exists and doesn't end with empty lines
        if existing_text and not existing_text.endswith('\n\n'):
            existing_text += '\n'
            
        # Add new patterns
        new_text = '\n'.join(new_patterns)
        
        # Write combined content
        with open(self.gitignore_path, 'w', encoding='utf-8') as f:
            f.write(existing_text + new_text)
            # Ensure file ends with newline
            if not new_text.endswith('\n'):
                f.write('\n')
                
        logger.info(f"✅ Updated {self.gitignore_path}")
    
    
    def list_patterns(self) -> List[str]:
        """List all current patterns."""
        self.load_existing_gitignore()
        return sorted(list(self.existing_patterns))


def update_gitignore(repo_path: Path, entries: Optional[str] = None) -> bool:
    """
    Convenience function to update .gitignore.
    
    Args:
        repo_path: Path to the repository
        entries: Custom entries to add (uses defaults if None)
        
    Returns:
        True if any changes were made
    """
    try:
        manager = GitIgnoreManager(repo_path)
        added = manager.add_entries(entries)
        return added > 0
    except Exception as e:
        logger.error(f"Failed to update .gitignore: {e}")
        return False


def main():
    """CLI interface for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage .gitignore entries safely"
    )
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the repository"
    )
    parser.add_argument(
        "--custom-entries",
        type=str,
        help="Path to file with custom entries"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current patterns and exit"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    repo_path = Path(args.repo_path).resolve()
    
    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    manager = GitIgnoreManager(repo_path)
    
    # List mode
    if args.list:
        patterns = manager.list_patterns()
        print(f"\nCurrent .gitignore patterns ({len(patterns)}):")
        for pattern in patterns:
            print(f"  {pattern}")
        sys.exit(0)
    
    # Add entries
    entries = None
    if args.custom_entries:
        with open(args.custom_entries, 'r') as f:
            entries = f.read()
    
    added = manager.add_entries(entries)
    sys.exit(0 if added >= 0 else 1)


if __name__ == "__main__":
    main()