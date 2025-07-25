Perfect, Johan. Here's the complete **updated `README.md`** with:

✅ Clean structure
✅ Documented `requirements-manage-gitignore.txt`
✅ Added `install-dev-env-manage_gitignore.sh` for local setup
✅ All previous improvements retained

---

### ✅ `README.md`

````markdown
# manage_gitignore.py

A safe and intelligent `.gitignore` manager that prevents duplicate entries, handles encoding issues, and preserves formatting — fully cross-platform and Windows-aware.

---

## 🚀 Features

- ✅ **No Duplicates**: Detects and skips equivalent patterns intelligently  
- ✅ **Smart Recognition**: Understands pattern variants like `__pycache__/` and `**/__pycache__/`  
- ✅ **UTF-8 Safe**: Validates encoding, prevents file corruption on Windows  
- ✅ **No Extra Blank Lines**: Cleans leading/trailing whitespace  
- ✅ **Organized Output**: Default entries include section headers and emojis  
- ✅ **Portable & Safe**: Atomic writes, preserves formatting, no side effects  
- ✅ **Standalone or Module**: Use via CLI or Python API  
- ✅ **Editor-friendly**: Normalized LF line endings, safe for Git and CI

---

## 📦 Installation

### Basic install

Clone or download `manage_gitignore.py` and place it into your project or your `$PATH`.

Then install dependencies:

```bash
pip install -r requirements-manage-gitignore.txt
````

This installs:

* `chardet` — used to detect and validate file encoding safely

### Recommended: Developer setup with virtualenv

Run this helper script to set up everything in an isolated environment:

```bash
./install-dev-env-manage_gitignore.sh
```

It will:

* Create `.venv`
* Activate it
* Install dependencies from `requirements-manage-gitignore.txt`

---

## 💻 Usage

### 🔧 CLI Commands

```bash
# Add default patterns to .gitignore
python manage_gitignore.py /path/to/repo

# Add custom entries from a file
python manage_gitignore.py /path/to/repo --custom-entries patterns.txt

# List current patterns
python manage_gitignore.py /path/to/repo --list

# Enable debug logging
python manage_gitignore.py /path/to/repo --debug
```

---

### 📚 CLI Help

```bash
./manage_gitignore.py -h
```

```
usage: manage_gitignore.py [-h] [--custom-entries CUSTOM_ENTRIES] [--list] [--debug] repo_path

Manage .gitignore entries safely

positional arguments:
  repo_path             Path to the repository

options:
  -h, --help            Show this help message and exit
  --custom-entries CUSTOM_ENTRIES
                        Path to file containing custom .gitignore entries
  --list                List current .gitignore patterns and exit
  --debug               Enable debug logging output
```

---

### 🐍 Python Module Usage

```python
from pathlib import Path
from manage_gitignore import update_gitignore, GitIgnoreManager

# Quick default update
update_gitignore(Path("/path/to/repo"))

# Manual control
manager = GitIgnoreManager(Path("/path/to/repo"))
manager.add_entries()

# Add custom entries
custom = """
# Build artifacts
*.exe
*.dll
bin/
obj/
"""
manager.add_entries(custom)
```

---

### 🔗 Integration with Git Hooks Installer

```python
from manage_gitignore import update_gitignore

def setup_git_hooks(target_repo, source_dir, ...):
    # ...
    if update_gitignore(target_repo):
        files_to_commit.append(".gitignore")
```

---

## ✨ Default Patterns (Grouped & Commented)

These are included by default:

### 🐍 Python

* `**/__pycache__/`, `*.py[cod]`, `*$py.class`
* `venv/`, `env/`, `.venv/`

### 🧪 Testing

* `.coverage`, `.cache/`, `.tox/`, `.pytest_cache/`

### 🏗️ Build Artifacts

* `build/`, `dist/`, `*.egg-info/`, `.eggs/`

### 💻 IDEs / Editors

* `.vscode/`, `.idea/`, `*.swp`, `*.swo`

### 🔒 Secrets

* `.env`, `.env.*`, `**/.env.*`, `!.env.example`

### 📓 Jupyter

* `.ipynb_checkpoints/`

### 🖥️ OS Files

* `.DS_Store`, `Thumbs.db`

### 📝 Git Commit Logs

* `commit-*`, `**/commit-*`, excluding `docs/commit-logs/**`

---

## 🧠 Pattern Recognition

| Pattern A      | Pattern B         | Recognized as Same? |
| -------------- | ----------------- | ------------------- |
| `__pycache__/` | `**/__pycache__/` | ✅ Yes               |
| `venv`         | `venv/`           | ✅ Yes               |
| `.env`         | `.env/`           | ❌ No (file vs dir)  |

---

## 🔐 Safety Features

1. **Encoding Validation**: UTF-8 enforced, no blind decoding
2. **Line Ending Normalization**: Always uses `LF`
3. **Atomic Writes**: Never truncates or corrupts files
4. **No Extra Lines**: Prevents leading/trailing whitespace
5. **Accurate Detection**: Uses `chardet` + `file` CLI for encoding
6. **Windows-safe**: Handles CP1252, MacRoman, etc.

---

## ✅ Example Output

```
[INFO] 🔍 Detected encoding: utf-8 (confidence: 1.00)
[INFO] Loaded 43 existing patterns from .gitignore
[INFO] ✅ Will add: .vscode/
[INFO] ⏭️ Skipped duplicate: __pycache__/
[INFO] ✅ Added 1 new pattern to .gitignore
[INFO] ✅ Updated /myrepo/.gitignore
```

---

## 🔚 Exit Codes

| Code | Meaning                              |
| ---- | ------------------------------------ |
| 0    | Success (patterns added or skipped)  |
| 1    | Error (invalid path, encoding, etc.) |

---

## 🛠 Requirements

* Python 3.6 or newer
* `chardet` (installed via `requirements-manage-gitignore.txt`)

---

## 👤 Maintained by

**Johan Sörell**
GitHub: [@J-SirL](https://github.com/J-SirL)
LinkedIn: [Johan Sörell](https://se.linkedin.com/in/johansorell)

---

## 📄 License

MIT — see [LICENSE](../LICENSE)

