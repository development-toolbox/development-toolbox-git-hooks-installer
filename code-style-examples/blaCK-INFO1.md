
## 🖤 How to Use Black in VS Code

- Install the official <b>Python</b> extension for VS Code.
- In your <code>settings.json</code>, set:
  ```json
  {
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
  }
  ```
- Now, every time you save a Python file, <code>black</code> will automatically format it.
- You can also run <kbd>Format Document</kbd> (<kbd>Shift+Alt+F</kbd>) manually.

> **Note:**
> <code>black --check</code> only tells you if files would be reformatted, but does not show a diff.
> To see what would change, use <code>black --diff your_file.py</code> or <code>black --diff .</code>.

---