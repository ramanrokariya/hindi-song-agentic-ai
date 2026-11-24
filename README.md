
## Application Verification and Regression Testing

Volume 1 includes reusable verification utilities and
automated regression tests to help readers independently
validate the application at different architectural layers.

### Verification Documentation

| Documentation | Purpose |
|---|---|
| [Database Verification](database/verification/README.md) | PostgreSQL schema, embeddings, metadata and category verification |
| [Application Verification Scripts](scripts/README.md) | Metadata, semantic search, Gemini intent and FastAPI verification |
| [Automated Regression Tests](tests/README.md) | Automated testing, mocked dependencies and regression coverage |

### Recommended Verification Sequence

Run the following commands from the repository root
after completing the application setup.

Activate the Python virtual environment:

    source .venv/bin/activate

1. Verify PostgreSQL and database properties:

       python -u scripts/verify_database_sql.py

2. Execute automated regression tests:

       PYTHONPATH=. python -m pytest tests/ -v

3. Verify category metadata:

       PYTHONPATH=. python scripts/verify_category_metadata.py

4. Verify hybrid search:

       PYTHONPATH=. python -u \
         scripts/verify_category_hybrid_search.py

5. Verify Gemini query understanding:

       PYTHONPATH=. python -u \
         scripts/verify_agent_category_intent.py --case all

6. Verify FastAPI end-to-end integration:

       PYTHONPATH=. python -u \
         scripts/verify_api_category_integration.py

### Reference Verification Results

| Verification Area | Successful Checks |
|---|---:|
| PostgreSQL SQL script execution | 7 |
| PostgreSQL metadata regression | 9 |
| Live hybrid search | 3 |
| Agentic AI category regression | 14 |
| Live Gemini query understanding | 5 |
| FastAPI end-to-end integration | 3 |
| Total targeted checks | 41 |

These results represent the reference implementation
and dataset used during Volume 1 development.

SQL execution checks confirm successful execution,
while returned database values require separate review.

Live Gemini verification requires valid Google Cloud
credentials and may consume API credits.

Successful verification does not guarantee the absence
of all application defects or identical LLM behavior
for every possible query.

### Additional FastAPI Regression Verification

The application includes nine automated FastAPI
endpoint and error-handling regression tests.

Execute:

    PYTHONPATH=. python -m pytest \
      tests/test_api.py -v -W error

Reference result: 9 tests passed.

These additional tests extend the earlier 41 targeted
verification checks to a total of 50 successful checks.

The tests use mocked agent dependencies and do not
consume Google Cloud API credits.

Refer to tests/README.md for detailed coverage and
TestClient dependency compatibility information.

## Python Dependency Management

The application uses separate dependency manifests
to distinguish runtime dependencies from development,
testing and verification dependencies.

### Reference Python Environment

The Volume 1 reference implementation uses:

- Python 3.12.3
- Python virtual environment (venv)
- pip package manager
- Explicitly versioned Python dependencies

### Dependency Manifest Files

| File | Purpose |
|---|---|
| [requirements.txt](requirements.txt) | Application runtime dependencies |
| [requirements-dev.txt](requirements-dev.txt) | Runtime, development, testing and verification dependencies |

### 1. Application Runtime Dependencies

The requirements.txt file contains the Python packages
required to execute the application.

These dependencies support:

- MusicBrainz API integration
- Google Cloud authentication
- Gemini-based song enrichment
- Structured AI response validation
- Embedding generation
- NumPy and Pandas data processing
- PostgreSQL pgvector connectivity
- Semantic and hybrid search
- Agentic AI query understanding
- FastAPI REST API services
- Uvicorn ASGI application server

Install runtime dependencies using:

    python -m pip install -r requirements.txt

This installation is appropriate for readers who only
need to execute the application without running the
automated test suite or TestClient verification scripts.

### 2. Development and Testing Dependencies

The requirements-dev.txt file extends requirements.txt
using the following directive:

    -r requirements.txt

It includes additional packages required for:

- Automated pytest regression testing
- FastAPI TestClient integration
- Application verification utilities
- HTTP client compatibility

Install development dependencies using:

    python -m pip install -r requirements-dev.txt

Readers following all hands-on exercises in Volume 1
should use requirements-dev.txt.

There is no need to install requirements.txt separately
when installing requirements-dev.txt.

### 3. Create a Python Virtual Environment

Run the following commands from the repository root.

Verify Python availability:

    python3 --version

Create an isolated Python environment:

    python3 -m venv .venv

Activate the virtual environment on Linux or Google
Cloud Shell:

    source .venv/bin/activate

For Windows PowerShell:

    .venv\Scripts\Activate.ps1

Verify the active Python environment:

    python --version
    python -m pip --version

Install the development dependencies:

    python -m pip install -r requirements-dev.txt

Verify installed dependency compatibility:

    python -m pip check

Expected output:

    No broken requirements found.

### 4. Dependency Version Pinning

The dependency manifests use explicit version pinning.

For example:

    fastapi==0.159.1
    google-genai==2.29.0
    psycopg[binary]==3.3.6

Version pinning helps:

- Reduce unexpected package compatibility issues.
- Maintain consistency with the reference implementation.
- Improve installation reproducibility.
- Support automated regression testing.
- Prepare the application for future CI/CD integration.

Readers should avoid independently upgrading individual
packages without verifying application compatibility.

Explicitly pinned requirements do not necessarily lock
every transitive dependency.

### 5. PostgreSQL Driver Configuration

The application uses:

    psycopg[binary]==3.3.6

The binary distribution provides a precompiled PostgreSQL
client implementation with bundled client libraries on
supported platforms.

Verify the installed implementation:

    python -c "from psycopg import pq; print(pq.__impl__)"

Expected output:

    binary

This simplifies installation by reducing the need for
separate PostgreSQL client libraries and C compilers.

### 6. FastAPI TestClient Compatibility

The reference implementation retains httpx for
application dependency compatibility.

The development manifest additionally includes httpx2
and its selected dependencies for compatibility with
the installed Starlette TestClient version.

Verify TestClient availability:

    python -W error -c "from fastapi.testclient import TestClient; print('TestClient import successful')"

Execute automated API regression tests:

    PYTHONPATH=. python -m pytest tests/test_api.py -v -W error

Reference result: 9 tests passed.

### 7. Verify Python Dependencies

The repository includes a reusable dependency
diagnostic utility:

    python -u scripts/verify_python_dependencies.py

This utility analyzes Python imports and reports
installed distribution versions.

Refer to:

- [Application Verification Scripts](scripts/README.md)
- [Automated Regression Tests](tests/README.md)

### 8. External Infrastructure Requirements

Installing Python dependencies does not automatically
configure external infrastructure.

Depending on the application feature, readers may
also require:

- Google Cloud project
- Google Cloud CLI
- Application Default Credentials (ADC)
- Vertex AI API access
- Docker
- PostgreSQL with pgvector
- MusicBrainz contact email configuration
- Application environment configuration
- Imported song embeddings and metadata

These infrastructure components are configured
separately during the hands-on exercises.

### 9. Dependency Management Best Practices

- Always use an isolated Python virtual environment.
- Install dependencies using the provided manifests.
- Execute pip check after dependency installation.
- Run regression tests after dependency changes.
- Do not commit virtual environments to Git.
- Do not commit credentials or access tokens.
- Review dependency changes before committing them.
- Verify application compatibility before upgrading.

### 10. Troubleshooting Dependency Installation

If dependency installation fails:

1. Verify the Python version.
2. Verify that the virtual environment is active.
3. Review pip dependency resolution errors.
4. Verify operating-system and architecture compatibility.
5. Execute pip check.
6. Run the dependency diagnostic utility.
7. Execute targeted regression tests.

Successful dependency installation does not independently
guarantee external service availability or application
runtime compatibility.

### 11. Complete Dependency Snapshot

The repository also provides a version-pinned dependency
snapshot:

[requirements-lock.txt](requirements-lock.txt)

This file was generated from a clean Python virtual
environment after installing and verifying both runtime
and development dependencies.

Generate the dependency snapshot using:

    python -m pip freeze > requirements-lock.txt

Unlike the runtime and development dependency manifests,
this snapshot captures installed direct and transitive
dependency versions reported by pip freeze.

### 12. Selecting the Appropriate Dependency File

| Dependency File | Recommended Usage |
|---|---|
| requirements.txt | Application runtime installation |
| requirements-dev.txt | Hands-on development, testing and verification |
| requirements-lock.txt | Reproducing the reference package versions |

To install the reference dependency snapshot:

    python -m pip install -r requirements-lock.txt

Verify dependency compatibility after installation:

    python -m pip check

Readers following the complete Volume 1 hands-on
exercises should normally use requirements-dev.txt.

The dependency snapshot provides an additional option
when reproducing the reference environment or
investigating dependency compatibility issues.

### 13. Clean Environment Verification

The runtime and development dependency manifests were
validated in a separate, clean Python virtual environment.

Reference environment:

- Platform: Google Cloud Shell (Linux)
- Python: 3.12.3
- PostgreSQL driver: Psycopg binary implementation

The following verification checks were completed:

| Verification | Result |
|---|---|
| Clean virtual environment creation | Passed |
| Runtime dependency installation | Passed |
| Development dependency installation | Passed |
| pip dependency compatibility | Passed |
| Psycopg binary implementation | Passed |
| FastAPI application import | Passed |
| Uvicorn version verification | Passed |
| pytest version verification | Passed |
| HTTP client version compatibility | Passed |
| FastAPI TestClient import with warnings treated as errors | Passed |
| Dependency snapshot generation | Passed |
| Environment-specific dependency reference check | Passed |

Verified framework and testing versions:

| Package | Version |
|---|---|
| FastAPI | 0.159.1 |
| Starlette | 1.9.0 |
| Uvicorn | 0.54.0 |
| pytest | 9.1.1 |
| httpx | 0.28.1 |
| httpcore | 1.0.9 |
| httpx2 | 2.16.2 |
| httpcore2 | 2.16.2 |
| truststore | 0.10.5 |
| Psycopg | 3.3.6 |

### 14. Dependency Snapshot Limitations

The requirements-lock.txt file is a version-pinned
environment snapshot generated using pip freeze.

It is not a cryptographically verified, hash-based
dependency lock file.

The reference snapshot was generated on Google Cloud
Shell using Python 3.12.3. Compatibility with other
Python versions, operating systems and hardware
architectures may vary.

Dependency installation and import verification do not
replace automated regression testing or live application
integration testing.

Whenever dependencies are changed:

1. Update the appropriate dependency manifest.
2. Verify installation in a clean virtual environment.
3. Execute pip check.
4. Run automated regression tests.
5. Run relevant application integration tests.
6. Regenerate the dependency snapshot.
7. Review and commit the dependency changes.

## Complete Automated Regression Verification

The complete automated regression suite was executed
in a newly created Python virtual environment using
the Volume 1 dependency manifests.

### Reference Testing Environment

- Platform: Google Cloud Shell (Linux)
- Python: 3.12.3
- pytest: 9.1.1
- Verification date: November 24, 2026

### Test Discovery

    PYTHONPATH=. python -m pytest tests/ --collect-only -q

Actual result:

    102 tests collected in 1.99s

### Complete Regression Execution

    PYTHONPATH=. python -m pytest tests/ -v

Actual result:

    102 passed in 1.93s

### Strict Warning Verification

    PYTHONPATH=. python -m pytest tests/ -v -W error

Actual result:

    102 passed in 1.94s

### Regression Verification Summary

| Verification | Result |
|---|---|
| Automated tests collected | 102 |
| Automated tests passed | 102 |
| Failed tests | 0 |
| Execution errors | 0 |
| Skipped tests | 0 |
| Test success rate | 100% |
| Strict warning verification | Passed |
| Additional defect correction required | None for this run |

The successful regression execution provides evidence
that the tested application functionality remains
compatible with the reference dependency configuration.

These results represent 102 unique collected test cases,
executed under normal and strict warning configurations.

Previously executed targeted automated tests are not
added to this total because they are included in the
complete regression suite.

Live Gemini integration, PostgreSQL verification and
SQL execution checks are tracked separately.

Successful automated regression testing does not
guarantee the absence of all application defects or
external infrastructure issues.

For additional testing instructions, refer to:

- [Automated Regression Tests](tests/README.md)
- [Application Verification Scripts](scripts/README.md)
- [Database Verification](database/verification/README.md)

## Live Application Integration Verification - Volume 1

Live application integration verification was performed
on November 24, 2026, using the clean Python reference
environment.

### Infrastructure Prerequisites

The following prerequisites were verified:

- Python 3.12.3 virtual environment.
- Google Cloud project configuration.
- Application project environment variable.
- Application Default Credentials (ADC).
- PostgreSQL Docker container availability.
- PostgreSQL connection readiness.
- Database configuration file availability.
- Restricted database configuration file permissions.

### Live Integration Verification Results

| Verification | Result |
|---|---|
| Infrastructure prerequisite checks | 8/8 |
| SQL verification script execution | 7/7 |
| JSON catalog distribution verification | 2/2 |
| Live hybrid search scenarios | 3/3 |
| Live Gemini agent intent scenarios | 5/5 |
| Live FastAPI integration scenarios | 3/3 |
| Local Uvicorn HTTP verification | Completed |

### Reference Dataset

Both the original and incrementally enriched JSON
catalogs contain 50 song records.

| Discovery category | Records |
|---|---:|
| Garba | 7 |
| Krishna Bhajan | 7 |
| Devotional | 6 |
| Folk | 6 |
| Patriotic | 6 |
| Missing category hint | 18 |
| Total | 50 |

The reference dataset contains 32 records with
category hints and 18 without category hints.

### Reusable Verification Commands

Execute these commands from the repository root
with the appropriate Python environment activated.

Database SQL verification:

    python -u scripts/verify_database_sql.py

Category metadata verification:

    python -u scripts/verify_category_metadata.py

Live hybrid search verification:

    PYTHONPATH=. python -u scripts/verify_category_hybrid_search.py

Live Gemini agent intent verification:

    PYTHONPATH=. python -u scripts/verify_agent_category_intent.py

Live FastAPI integration verification:

    PYTHONPATH=. python -u scripts/verify_api_category_integration.py

Start the local HTTP server:

    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

### Verification Limitations

- SQL execution success does not independently assert
  every returned database value.
- Live Gemini responses may vary between executions.
- Similarity scores are not confidence percentages.
- The reference dataset contains only 50 song records.
- The health endpoint verifies application responsiveness
  rather than complete external dependency readiness.
- Local HTTP verification does not establish production
  transport security or scalability.
- Live model requests may incur Google Cloud charges.

Automated regression results and live integration
results are tracked separately to avoid double-counting
verification scenarios.


## Comprehensive Command Reference

Volume 1 includes a dedicated command reference to help
readers reproduce the hands-on implementation, execute
verification utilities and troubleshoot common issues.

**[UsefulCommands.txt - Complete Command Reference](UsefulCommands.txt)**

The command reference contains 34 sections covering:

- Google Cloud project configuration and authentication.
- Application Default Credentials (ADC).
- Python virtual environments and dependency management.
- MusicBrainz ingestion and catalog management.
- Gemini enrichment and incremental checkpointing.
- Batch processing, retry policies and failure tracking.
- Catalog quality reporting and discovery validation.
- Embedding generation and semantic search.
- Docker, PostgreSQL and pgvector configuration.
- Database schema, migrations and metadata imports.
- Database verification and recovery.
- Hybrid search and Agentic AI orchestration.
- FastAPI, Uvicorn and REST API verification.
- Automated regression and live integration testing.
- Structured logging and troubleshooting.
- Git, GitHub and Gitleaks security verification.
- Official Volume 1 release management.

### How to Use the Command Reference

Execute individual commands as required by the relevant
book chapter or implementation activity.

The command reference is not an executable shell script
and should not be executed in its entirety.

Commands that modify data, change configuration or
potentially incur Google Cloud charges are identified
where applicable.

Readers should configure their own Google Cloud project,
authentication credentials and database password.

The reference also includes expected verification results
from the Volume 1 implementation.

### Additional Documentation

- [Command Reference](UsefulCommands.txt)
- [Verification Utilities](scripts/README.md)
- [Automated Testing](tests/README.md)
- [Database Verification](database/verification/README.md)
- [Runtime Dependencies](requirements.txt)
- [Development Dependencies](requirements-dev.txt)
- [Reference Dependency Snapshot](requirements-lock.txt)


## Documentation Quality Verification

The project includes a reusable documentation
reference verification utility:

[verify_documentation_references.py](scripts/verify_documentation_references.py)

Execute from the repository root:

    python -u scripts/verify_documentation_references.py

Initial reference verification results:

| Verification | Result |
|---|---:|
| Documentation references | 115/115 |
| Backend module filenames | 24/24 |
| Backend module main entry points | 24/24 |
| Function signatures reviewed | 4/4 |
| Command reference sections | 34 |

Documentation verification is separate from automated
application regression and live integration testing.

Reference counts may change as documentation is updated.

## About the Author

**Raman Rokariya**

Raman Rokariya is an experienced Software Engineering and API Platform
professional with over 20 years of experience in Information Technology,
specializing in enterprise integration, API management, platform
engineering, automation, security and distributed systems.

He is the author, architect and developer of the Hindi Song Agentic AI
Search Engine, an enterprise-oriented AI solution that integrates
Generative AI, natural language understanding, vector embeddings,
semantic search, structured metadata filtering and intelligent
agent orchestration.

The solution leverages Google Cloud, Gemini, Python, PostgreSQL,
pgvector and FastAPI, incorporating enterprise engineering practices
such as modular architecture, API design, structured logging,
exception handling, automated regression testing, dependency
management, database persistence and version-controlled releases.

His approach emphasizes practical implementation, maintainability,
reliability, extensibility and architectural foundations for
scalable AI-powered applications.

Beyond his professional career in technology, Raman is a passionate
singer and music enthusiast with an active presence on platforms
such as YouTube, Smule and StarMaker. He is also an active volunteer
in cultural events, community programs and social gatherings.

His passion for music inspired the selection of song discovery as
the use case for this Agentic AI solution. The project brings
together two of his greatest interests — technology and music —
addressing the challenge of discovering songs through natural
language based on mood, genre, occasion and listening preferences
rather than relying solely on conventional keyword-based searches.

Through this book, he shares his technical experience and
implementation approach to architecting and building end-to-end
Agentic AI solutions using modern cloud technologies and established
software engineering practices.
