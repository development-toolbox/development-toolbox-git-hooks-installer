# Contributing

## Testing & Code Quality

All tests and code quality checks must pass before merging.

### How to run tests

1. Install Docker and docker-compose.
2. Run:
   ```
   make test
   ```
   This will build and run all tests and checks in Ubuntu and AlmaLinux containers.

### What is checked

- Code formatting (black, isort)
- Linting (ruff, flake8, pylint)
- Type checking (mypy)
- Security scanning (bandit)
- Unit and integration tests (pytest)

### Adding tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
