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
