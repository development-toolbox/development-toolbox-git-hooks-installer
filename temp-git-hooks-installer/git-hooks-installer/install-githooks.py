/*************  ✨ Windsurf Command 🌟  *************/
#!/usr/bin/env python3
#!/bin/bash

import os
import shutil
import subprocess
# Script: setup-githooks.sh
# Description: Setup git hooks and copy the scripts directory to $REPO_ROOT/scripts.

# Step 1: Get the repository root directory
repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip()
REPO_ROOT=$(git rev-parse --show-toplevel)
if [ $? -ne 0 ]; then
    echo "❌ Error: Not inside a Git repository."
    exit 1
fi

# Step 2: Locate the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Step 3: Define the source directories
hooks_src = os.path.join(script_dir, 'git-hooks')
scripts_src = os.path.join(script_dir, 'scripts')
HOOKS_SRC="$SCRIPT_DIR/git-hooks"
SCRIPTS_SRC="$SCRIPT_DIR/scripts"

# Step 4: Validate the source directories
if not os.path.isdir(hooks_src):
    print("Error: Hook source directory '{}' does not exist.".format(hooks_src))
    exit(1)
if [ ! -d "$HOOKS_SRC" ]; then
    echo "❌ Error: Hook source directory '$HOOKS_SRC' does not exist."
    exit 1
fi

if not os.path.isdir(scripts_src):
    print("Error: Scripts source directory '{}' does not exist.".format(scripts_src))
    exit(1)
if [ ! -d "$SCRIPTS_SRC" ]; then
    echo "❌ Error: Scripts source directory '$SCRIPTS_SRC' does not exist."
    exit 1
fi

# Step 5: Define the target directories
hooks_dir = os.path.join(repo_root, '.git', 'hooks')
scripts_dest = os.path.join(repo_root, 'scripts')
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SCRIPTS_DEST="$REPO_ROOT/scripts"

# Step 6: Ensure the target directories exist
os.makedirs(hooks_dir, exist_ok=True)
os.makedirs(scripts_dest, exist_ok=True)
mkdir -p "$HOOKS_DIR"
mkdir -p "$SCRIPTS_DEST"

# Step 7: Copy hooks to .git/hooks
for hook in os.listdir(hooks_src):
    shutil.copy2(os.path.join(hooks_src, hook), hooks_dir)
cp "$HOOKS_SRC"/* "$HOOKS_DIR" || {
    echo "❌ Error: Failed to copy hooks."
    exit 1
}

# Step 8: Copy the entire scripts directory to $REPO_ROOT/scripts
for item in os.listdir(scripts_src):
    source = os.path.join(scripts_src, item)
    destination = os.path.join(scripts_dest, item)
    if os.path.isfile(source):
        shutil.copy2(source, destination)
    else:
        shutil.copytree(source, destination, symlinks=True)
cp -r "$SCRIPTS_SRC/"* "$SCRIPTS_DEST/" || {
    echo "❌ Error: Failed to copy scripts."
    exit 1
}

# Step 9: Make hooks and scripts executable
for hook in os.listdir(hooks_dir):
    hook_path = os.path.join(hooks_dir, hook)
    os.chmod(hook_path, 0o755)
chmod +x "$HOOKS_DIR/"* || {
    echo "❌ Error: Failed to set hooks as executable."
    exit 1
}
chmod -R +x "$SCRIPTS_DEST" || {
    echo "❌ Error: Failed to set scripts as executable."
    exit 1
}

for root, dirs, files in os.walk(scripts_dest):
    for file in files:
        file_path = os.path.join(root, file)
        os.chmod(file_path, 0o755)

# Step 10 & 11: Check if source and destination differ and stage changes only if needed
diff_process = subprocess.Popen(['diff', '-r', scripts_src, scripts_dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
diff_output, diff_error = diff_process.communicate()
if diff_process.returncode == 0:
    print("Git hooks and scripts are already up-to-date. No changes detected, skipping commit.")
else:
if diff -r "$SCRIPTS_SRC" "$SCRIPTS_DEST" >/dev/null 2>&1; then
    echo "✅ Git hooks and scripts are already up-to-date. No changes detected, skipping commit."
else
    # Stage changes only if there are differences
    subprocess.check_call(['git', 'add', scripts_dest])
    git add "$SCRIPTS_DEST"

    # Double-check if changes are staged before committing
    if subprocess.call(['git', 'diff', '--cached', '--quiet', scripts_dest]) == 0:
        print("Changes detected but no modifications staged. Skipping commit.")
    else:
    if git diff --cached --quiet "$SCRIPTS_DEST"; then
        echo "✅ Changes detected but no modifications staged. Skipping commit."
    else
        # Commit the changes if modifications are staged
        subprocess.check_call(['git', 'commit', '-m', 'chore(setup-githooks.py): Successfully installed git hooks and committed scripts\n\n'
                              '- Installed git hooks to the .git/hooks directory (not tracked in the repository).\n'
                              '- Added and committed the scripts directory for git hook management.\n'
                              '- Prevented accidental commits of other manually staged files outside the intended scope.'])
        print("Git hooks installed to '{}' (not tracked in repository).".format(hooks_dir))
        print("Scripts have been added to '{}' and committed successfully!".format(scripts_dest))
        git commit -m "chore(setup-githooks.sh): Successfully installed git hooks and committed scripts

- Installed git hooks to the .git/hooks directory (not tracked in the repository).
- Added and committed the scripts directory for git hook management.
- Prevented accidental commits of other manually staged files outside the intended scope."
        echo "✅ Git hooks installed to '$HOOKS_DIR' (not tracked in repository)."
        echo "✅ Scripts have been added to '$SCRIPTS_DEST' and committed successfully!"
    fi
fi

/*******  92b13a51-1475-40de-a7e3-9e1b5ad0e2df  *******/