# Automated Application Tests

This directory contains automated tests supporting
Volume 1 of Building an Agentic AI Song Search Engine.

The tests use pytest to validate application behavior
and protect existing functionality against regressions.

## Prerequisites

Run all commands from the repository root.

Activate the Python virtual environment:

    source .venv/bin/activate

Verify pytest availability:

    python -m pytest --version

## Test Execution

Discover available tests without executing them:

    PYTHONPATH=. python -m pytest tests/ --collect-only -q

Execute the complete test directory:

    PYTHONPATH=. python -m pytest tests/ -v

Execute an individual test file:

    PYTHONPATH=. python -m pytest \
      tests/test_agent_category_integration.py -v

Execute tests matching a specific name:

    PYTHONPATH=. python -m pytest \
      tests/ -k category -v

## Selected Test Modules

| Test Module | Purpose |
|---|---|
| test_musicbrainz_unit.py | MusicBrainz client behavior and configuration |
| test_catalog.py | Catalog processing and data integrity |
| test_incremental_checkpoint.py | Incremental enrichment checkpoint behavior |
| test_postgres_metadata_import.py | PostgreSQL metadata mapping and array conversion |
| test_agent_category_integration.py | Intent validation, agent orchestration and API response serialization |

Use pytest collection to discover all available tests.

## PostgreSQL Metadata Regression Tests

    PYTHONPATH=. python -m pytest \
      tests/test_postgres_metadata_import.py -v

Coverage includes:

- Correct discovery category mapping
- Missing category handling
- Ignoring incorrect nested category metadata
- PostgreSQL parameter mapping
- Text array conversion
- Database transaction commit behavior

Reference verification result: 9 tests passed.

## Agentic AI Category Regression Tests

    PYTHONPATH=. python -m pytest \
      tests/test_agent_category_integration.py -v

Coverage includes:

- Supported category validation
- Unsupported category rejection
- Optional category handling
- Category propagation to hybrid search
- Combined genre and category propagation
- Existing genre-based search behavior
- API intent and result serialization

Reference verification result: 14 tests passed.

## Mocked Dependencies

The metadata and Agentic AI category regression tests
use mocked external dependencies.

These two test modules do not require:

- Live Gemini API requests
- A running PostgreSQL container
- Google Cloud API credits
- A running FastAPI server

Mocked tests verify application behavior without relying
on external service availability.

## Automated Tests Versus Live Verification

Automated tests validate isolated application behavior
and expected interactions between components.

Live verification scripts exercise real external services
and integrated application functionality.

Refer to:

- ../scripts/README.md
- ../database/verification/README.md

## Understanding Test Results

PASSED:
The test completed successfully.

FAILED:
An assertion or expected application behavior failed.

ERROR:
A problem occurred during test collection or execution.

SKIPPED:
A test was intentionally not executed.

## Regression Testing Workflow

1. Identify and reproduce the defect.
2. Correct the application behavior.
3. Add or update automated regression tests.
4. Execute targeted tests.
5. Execute the complete regression suite.
6. Review source changes.
7. Commit verified changes.
8. Push changes to the remote repository.
9. Verify the remote repository state.

## Limitations

Passing automated tests does not prove the absence
of all application defects.

Mocked tests do not establish external service
availability or live Gemini interpretation accuracy.

Live integration verification should complement
automated regression testing.

## FastAPI Endpoint and Error-Handling Tests

Test module:

    tests/test_api.py

Execute the API regression tests:

    PYTHONPATH=. python -m pytest \
      tests/test_api.py -v -W error

The -W error option treats Python warnings as errors.

Coverage includes:

- Health endpoint
- Root endpoint
- Successful song search
- Category response serialization
- Missing query validation
- Empty query validation
- Whitespace-only query validation
- Maximum query length validation
- Internal server error handling
- Request ID propagation
- Unique request ID generation
- Prevention of internal exception disclosure

Reference verification result:

- Total test scenarios: 9
- Passed: 9
- Failed: 0
- Reference execution time: 1.35 seconds

Execution time may vary across environments.

## FastAPI TestClient Dependency Compatibility

The reference implementation was verified using:

- FastAPI 0.159.1
- Starlette 1.9.0
- httpx 0.28.1
- httpx2 2.16.2
- httpcore 1.0.9
- httpcore2 2.16.2
- truststore 0.10.5

The httpx2 package supports the TestClient dependency
configuration used by the installed Starlette version.

The existing httpx package is retained to preserve
compatibility with other application dependencies.

Refer to the project dependency manifests for the
final supported installation configuration.

## API Testing Limitations

The API regression tests use FastAPI TestClient
and mocked song search agent dependencies.

These tests do not require:

- Live Gemini API requests
- A running PostgreSQL container
- A running Uvicorn server
- Google Cloud API credits

These tests verify in-process HTTP behavior.
They do not verify external network connectivity,
TLS certificates or production deployment readiness.

## FastAPI Endpoint and Error-Handling Tests

Test module:

    tests/test_api.py

Execute the API regression tests:

    PYTHONPATH=. python -m pytest \
      tests/test_api.py -v -W error

The -W error option treats Python warnings as errors.

Coverage includes:

- Health endpoint
- Root endpoint
- Successful song search
- Category response serialization
- Missing query validation
- Empty query validation
- Whitespace-only query validation
- Maximum query length validation
- Internal server error handling
- Request ID propagation
- Unique request ID generation
- Prevention of internal exception disclosure

Reference verification result:

- Total test scenarios: 9
- Passed: 9
- Failed: 0
- Reference execution time: 1.35 seconds

Execution time may vary across environments.

## FastAPI TestClient Dependency Compatibility

The reference implementation was verified using:

- FastAPI 0.159.1
- Starlette 1.9.0
- httpx 0.28.1
- httpx2 2.16.2
- httpcore 1.0.9
- httpcore2 2.16.2
- truststore 0.10.5

The httpx2 package supports the TestClient dependency
configuration used by the installed Starlette version.

The existing httpx package is retained to preserve
compatibility with other application dependencies.

Refer to the project dependency manifests for the
final supported installation configuration.

## API Testing Limitations

The API regression tests use FastAPI TestClient
and mocked song search agent dependencies.

These tests do not require:

- Live Gemini API requests
- A running PostgreSQL container
- A running Uvicorn server
- Google Cloud API credits

These tests verify in-process HTTP behavior.
They do not verify external network connectivity,
TLS certificates or production deployment readiness.

## Complete Regression Suite - Volume 1

The complete automated regression suite was verified
in a clean Python virtual environment on November 24,
2026.

### Prerequisites

- Python 3.12.3 reference environment
- Activated Python virtual environment
- Development dependencies installed

Install development dependencies:

    python -m pip install -r requirements-dev.txt

Verify dependency compatibility:

    python -m pip check

Execute the following commands from the repository root.

### 1. Discover Automated Tests

    PYTHONPATH=. python -m pytest tests/ --collect-only -q

Reference result:

    102 tests collected in 1.99s

### 2. Execute Complete Regression Suite

    PYTHONPATH=. python -m pytest tests/ -v

Reference result:

    102 passed in 1.93s

### 3. Execute Strict Warning Verification

    PYTHONPATH=. python -m pytest tests/ -v -W error

Reference result:

    102 passed in 1.94s

The -W error option treats Python warnings as errors,
subject to applicable warning filters.

This helps identify deprecated APIs, dependency
compatibility concerns and other warning-related issues.

### 4. Regression Testing Results

| Metric | Reference Result |
|---|---|
| Tests collected | 102 |
| Tests passed | 102 |
| Tests failed | 0 |
| Execution errors | 0 |
| Tests skipped | 0 |
| Success rate | 100% |
| Normal execution time | 1.93 seconds |
| Strict warning execution time | 1.94 seconds |

Execution times may vary depending on hardware,
operating system and available resources.

### 5. Regression Testing Best Practices

- Execute the complete suite after dependency changes.
- Execute targeted tests during defect correction.
- Execute the complete suite before release.
- Investigate unexpected warnings and failures.
- Avoid suppressing warnings without justification.
- Keep automated tests reproducible.
- Track live integration verification separately.
- Do not commit credentials or sensitive test data.

### 6. Testing Limitations

Passing the automated regression suite validates the
behaviors covered by the collected test cases.

It does not independently establish:

- Complete application code coverage.
- Production scalability or performance.
- External service availability.
- Gemini response accuracy for every possible query.
- PostgreSQL recovery under every failure scenario.
- Production security readiness.
- Absence of all application defects.

Live integration and infrastructure verification are
performed separately using the repository verification
utilities.
