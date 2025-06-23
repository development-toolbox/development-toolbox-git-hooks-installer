# manage_gitignore.py

A safe and intelligent `.gitignore` manager that prevents duplicate entries and preserves existing content.

## Features

- ✅ **No Duplicates**: Detects and prevents duplicate patterns
- ✅ **Smart Pattern Recognition**: Recognizes equivalent patterns (e.g., `__pycache__/` vs `**/__pycache__/`)
- ✅ **Preserves Existing Content**: Never overwrites or corrupts your existing `.gitignore`
- ✅ **Section Headers**: Maintains organized sections with descriptive headers
- ✅ **Safe Operations**: All operations are atomic and safe
- ✅ **Standalone or Module**: Use as CLI tool or import as Python module

## Installation

Place `manage_gitignore.py` in your project or in your PATH.

```bash
chmod +x manage_gitignore.py
```

## Usage

### Command Line Interface

```bash
# Add default git hooks patterns
python manage_gitignore.py /path/to/repo

# List current patterns
python manage_gitignore.py /path/to/repo --list

# Add custom patterns from file
python manage_gitignore.py /path/to/repo --custom-entries patterns.txt

# Enable debug logging
python manage_gitignore.py /path/to/repo --debug
```

### As a Python Module

```python
from pathlib import Path
from manage_gitignore import update_gitignore, GitIgnoreManager

# Quick update with defaults
update_gitignore(Path("/path/to/repo"))

# Advanced usage
manager = GitIgnoreManager(Path("/path/to/repo"))
added_count = manager.add_entries()  # Returns number of new patterns added

# Custom entries
custom_patterns = """
# Build artifacts
*.exe
*.dll
bin/
obj/
"""
manager.add_entries(custom_patterns)
```

### Integration with Git Hooks Installer

```python
# In your githooks-install.py
from manage_gitignore import update_gitignore

def setup_git_hooks(target_repo, source_dir, ...):
    # ... existing code ...
    
    # Update .gitignore
    if update_gitignore(target_repo):
        files_to_commit.append(".gitignore")
```

## Default Patterns

The script includes sensible defaults for Python projects with git hooks:

### 🐍 Python
- `**/__pycache__/` - Python cache directories
- `*.py[cod]` - Compiled Python files
- Virtual environments: `venv/`, `env/`, `.venv/`
- Build artifacts: `dist/`, `build/`, `*.egg-info/`

### 💻 Development Tools
- `.vscode/` - VS Code settings

### 🔒 Security
- `.env` - Environment files
- `.env.*` - Environment variants
- `!.env.example` - Except example files

### 📝 Git Hooks Specific
- `commit-*` - Temporary commit message files
- `!docs/commit-examples/` - Except documentation
- `!docs/commit-logs/` - Except commit history

## Pattern Recognition

The script intelligently recognizes equivalent patterns:

| Pattern A | Pattern B | Recognized as Same? |
|-----------|-----------|-------------------|
| `__pycache__/` | `**/__pycache__/` | ✅ Yes |
| `*.pyc` | `*.pyc` | ✅ Yes |
| `.env` | `.env/` | ❌ No (file vs directory) |
| `venv` | `venv/` | ✅ Yes |

## Safety Features

1. **Backup**: Original content is always preserved
2. **Atomic Writes**: File is written completely or not at all
3. **Format Preservation**: Maintains spacing and comments
4. **No Corruption**: Handles edge cases like missing newlines

## Example Output

```
[INFO] 🔎 Checking for updates...
[INFO] Loaded 45 existing patterns from .gitignore
[INFO] ✅ Will add pattern: **/__pycache__/
[INFO] ✅ Will add pattern: .vscode/
[INFO] ⏭️  Skipping duplicate: .env
[INFO] ✅ Added 2 new patterns to .gitignore
[INFO] ✅ Updated /path/to/repo/.gitignore
```

## Exit Codes

- `0` - Success (patterns added or already exist)
- `1` - Error occurred

## Requirements

- Python 3.6+
- No external dependencies

## ✅ Maintained by

- **Johan Sörell**  
- **GitHub:** [J-SirL](https://github.com/J-SirL)  
- **LinkedIn:** [Johan Sörell](https://se.linkedin.com/in/johansorell)  

## License

MIT License see [License](../LICENSE)