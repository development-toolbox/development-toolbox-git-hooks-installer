# AI Conversation History & Instructions

## Context

This file contains the ongoing conversation and requirements for setting up a comprehensive Docker-based testing environment for the `development-toolbox-git-hooks-installer` project.  
If you (another AI assistant) are picking up this project, please read this file and continue following the user's requirements and preferences.

## Instructions for the Next AI Assistant

- Read this file and all referenced project files before making changes.
- Review the detailed chat logs in `docs/ai-history/` for full context and decision history.
- Always use concise, grouped code suggestions as described in the user's prompt.
- Save any new conversation or context updates in this file and/or in a new dated file in `docs/ai-history/`.
- When the user switches back to GitHub Copilot, continue from the latest context here.
- If you generate new chat logs or context, save them in a new file in `docs/ai-history/` using the format `YYYY-MM-DD-topic.md` and update this file with a reference to the new log.

## Summary of Current Progress

- The project uses Docker-based testing for Ubuntu and AlmaLinux (9 & 10), Python 3.12+, and code quality tools.
- All test results (including HTML reports) are saved in `tests/results/`.
- The user prefers conventional commit messages.
- Troubleshooting scripts and documentation are included.
- See `tests/README.md` and `CONTRIBUTING.md` for details on running and adding tests.

## Conversation Log

- User requested a robust Docker-based test environment for both unit and integration tests.
- All code quality tools (ruff, flake8, pylint, mypy, black, isort, bandit) are included.
- Dockerfiles, docker-compose, and scripts are provided for setup and troubleshooting.
- Test results are now saved as HTML and text files in `tests/results/`.
- User wants this conversation saved for continuity when switching AI assistants or computers.

---

**Note:**  
This file contains only a summary and key context, not the full verbatim chat history.  
If you want to preserve the entire conversation, consider splitting the logs into multiple files (for example, one file per session or topic) inside `docs/ai-history/`.  
You can then copy and paste relevant parts of your chat logs into those files for easier management and reference.

**If you are a new AI assistant, please append any new context or instructions here as the project evolves, and reference any new log files you create in `docs/ai-history/`.**
