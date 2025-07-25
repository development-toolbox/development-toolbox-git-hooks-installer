# TODO

## Current Work - FileTracker Security Validation Fixes
- [x] Redesigned FileTracker.validate_staging_area() with improved path normalization
- [x] Added debug logging to catch validation mismatches (security/file_tracker.py)
- [x] Fixed false positive warnings that were confusing during installation
- [x] Created comprehensive test coverage for validation edge cases
- [x] Fixed integration test import paths for git-hooks-installer module
- [ ] Fix Unicode filename test edge case (line 120 issue)
- [ ] Verify all FileTracker validation tests pass in Docker environment
- [ ] Test the improved validation logic with actual git-hooks-installer.py run

## Future Work
- [ ] Publish Docker images to a public registry (e.g., Docker Hub, GHCR) when project matures.
- [ ] Add `.pre-commit-config.yaml` for local developer hooks (lint, format, etc).
- [x] Expand integration tests to cover full git-hooks installation flow.
- [ ] Add more OS/Python/Git versions as they become available.
- [ ] Add CI workflow (e.g., GitHub Actions) to run tests on pull requests.
