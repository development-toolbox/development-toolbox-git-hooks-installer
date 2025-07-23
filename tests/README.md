# Tests

This directory contains all test-related files for the project.

## Structure

- `unit/` - Unit tests for individual functions and modules.
- `integration/` - Integration tests that cover end-to-end scenarios, including git operations.
- `docker/` - Dockerfiles and docker-compose setup for running tests in multiple environments.
- `requirements.txt` - Python dependencies for testing and code quality.
- `run_all.sh` - Script to run all code quality checks and tests inside Docker containers.

## Running Tests

All tests and code quality checks are intended to be run inside Docker containers for reproducibility.

### Prerequisites

- Docker (and Docker Compose)
- (Optional) GNU Make (for `make test` command)

### How to Run

From the project root:

```sh
make test
```

Or, if you do not have `make` available (e.g., on Windows without WSL or Git Bash), run:

```sh
docker-compose -f tests/docker/docker-compose.yml up --build --abort-on-container-exit
```

This will:
- Build Docker images for Ubuntu and AlmaLinux (9 & 10)
- Run all linting, formatting, type checks, security scans, and tests in each environment

### Adding Tests

- Place new unit tests in `tests/unit/`
- Place new integration tests in `tests/integration/`

### Test Results

- All test and code quality outputs are saved in the `tests/results/` directory.
- HTML reports for unit and integration tests are generated as `unit-report.html` and `integration-report.html` in `tests/results/`.
- Text output for each code quality tool and test run is also saved in `tests/results/` (e.g., `pytest-unit.txt`, `black.txt`, etc.).
- Open the HTML files in your browser for a detailed, easy-to-read summary of test results.
- If you want to generate additional or custom reports, modify `run_all.sh` as needed.

### Notes

- See `CONTRIBUTING.md` in the project root for more details on contributing and testing.
- For troubleshooting Docker installation, see the scripts in `scripts/`.
