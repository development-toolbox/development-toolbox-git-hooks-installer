Solution One import per line, grouped and sorted, unused imports removed.
💡 How to Fix with isort
1. Install isort:
$ pip install isort
2. Sort a single file:
$ isort your_file.py
3. Sort all files in your project:
$ isort .
What does isort do?
Groups imports into standard library, third-party, and local imports.
Sorts each group alphabetically.
Ensures one import per line.
Removes duplicates and (optionally) unused imports.
Pre-commit hook example:
# .pre-commit-config.yaml
-   repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        name: isort (python import sorting)
        entry: isort
        language: python
        types: [python]
        args: [--profile=black]

Tip: Add isort to your pre-commit hooks or configure your editor to run it on save for consistent imports! See more isort tips & automation →