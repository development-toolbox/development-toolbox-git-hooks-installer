# Commit Log

---

## Commit Details

- **Commit Hash:**   `b7c1f2bc4e658e75d00e82990b8064cfee1e4388`
- **Branch:**        `fetures/update-docs`
- **Author:**        Johan Sörell
- **Date:**          2025-06-25 16:15:40 +0200
- **Message:**

  fix(ci-cd): add REPO_ROOT env var and extended debugging

- Export REPO_ROOT to github.workspace for update-readme.sh
- Add grep search for the problematic commit reference
- Show lines 50-70 of update-readme.sh to find failing command
- Help diagnose where '27f36953' reference comes from
- Debug why script fails after directory definitions

---

## Changed Files:

- `M	git-hooks-installer/ci-cd/github-actions-update-timeline.yml`

---
