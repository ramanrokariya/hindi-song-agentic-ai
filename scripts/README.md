# Application Verification Scripts

This directory contains reusable verification utilities
for Volume 1 of Building an Agentic AI Song Search Engine.

These scripts help readers independently verify metadata,
semantic search, Agentic AI and REST API functionality.

## Available Scripts

| Script | Purpose | Gemini API | PostgreSQL |
|---|---|---|---|
| verify_category_metadata.py | Validate catalog category metadata | No | No |
| verify_category_hybrid_search.py | Verify category filtering and vector search | Yes | Yes |
| verify_agent_category_intent.py | Verify Gemini query understanding | Yes | No |
| verify_api_category_integration.py | Verify the integrated FastAPI search pipeline | Yes | Yes |

## Prerequisites

Execute all commands from the repository root.

Activate the Python virtual environment:

    source .venv/bin/activate

For scripts requiring Google Cloud services, ensure
that Application Default Credentials are configured
and the correct Google Cloud project is selected.

Verify ADC without displaying the access token:

    gcloud auth application-default print-access-token > /dev/null

For scripts requiring PostgreSQL, verify database readiness:

    docker exec hindi-song-postgres \
      pg_isready -U songadmin -d hindi_songs

## 1. Verify Category Metadata

    PYTHONPATH=. python scripts/verify_category_metadata.py

Validates category metadata in the catalog and
incremental enrichment JSON files.

Reference dataset:

- Total recordings: 50
- Populated categories: 32
- Missing categories: 18

No Gemini API calls or database connections are required.

## 2. Verify Category Hybrid Search

    PYTHONPATH=. python -u \
      scripts/verify_category_hybrid_search.py

Verifies:

- Garba category filtering
- Krishna Bhajan category filtering
- Nonexistent category handling
- Similarity score range
- Descending similarity ranking

Reference verification result: 3 scenarios passed.

Requires PostgreSQL and the Gemini embedding service.

## 3. Verify Agentic AI Query Understanding

Execute all scenarios:

    PYTHONPATH=. python -u \
      scripts/verify_agent_category_intent.py --case all

Execute an individual scenario:

    PYTHONPATH=. python -u \
      scripts/verify_agent_category_intent.py --case devotional

Supported scenario arguments:

- all
- garba
- krishna
- romantic
- devotional
- folk_garba

Reference verification result: 5 scenarios passed.

Requires live Gemini query-understanding requests.

## 4. Verify FastAPI Category Integration

    PYTHONPATH=. python -u \
      scripts/verify_api_category_integration.py

Verifies the integrated application pipeline:

    FastAPI
      -> Gemini query understanding
      -> Agent orchestration
      -> Gemini query embedding
      -> PostgreSQL pgvector
      -> API response

Verification includes HTTP status, request IDs,
intent fields, category filtering, similarity scores
and result ordering.

Reference verification result: 3 scenarios passed.

The script uses FastAPI TestClient and does not require
a separately running Uvicorn server.

## API Usage and Cost Considerations

| Script | Expected model requests per full run |
|---|---|
| verify_category_metadata.py | None |
| verify_category_hybrid_search.py | 3 embedding requests |
| verify_agent_category_intent.py | 5 query-understanding requests |
| verify_api_category_integration.py | 3 query-understanding and 3 embedding requests |

These estimates exclude retries and assume successful
execution of all scenarios.

Live model requests may consume Google Cloud credits
or incur charges according to applicable pricing.

## Troubleshooting

- Verify Google Cloud authentication if model requests fail.
- Verify ADC separately from Google Cloud CLI authentication.
- Verify PostgreSQL readiness before database-dependent tests.
- Verify that embeddings and metadata have been imported.
- Use individual scenarios to isolate interpretation failures.

## Limitations

Gemini responses may vary between executions.

Successful verification of the reference scenarios does
not guarantee correct interpretation of every possible query.

Similarity scores represent vector similarity, not
statistical confidence or probability of relevance.

These scripts verify application functionality and do not
constitute production load, security or performance testing.

## 5. Verify PostgreSQL SQL Scripts

Execute all SQL verification scripts:

    python -u scripts/verify_database_sql.py

Execute an individual SQL verification script:

    python -u scripts/verify_database_sql.py \
      --file 04_verify_category.sql

The utility automatically discovers SQL files under
database/verification/, checks PostgreSQL readiness,
executes each selected file and reports a summary.

No Gemini API calls are required.

A successful execution confirms that the SQL statements
completed without errors. Readers must still review
the returned values against expected dataset results.

## 6. Verify Python Dependencies

    python -u scripts/verify_python_dependencies.py

This utility uses Python's Abstract Syntax Tree (AST)
to inspect imports under:

- backend/
- scripts/
- tests/

It reports installed third-party distribution versions
without executing the application source modules.

Use this utility when reviewing dependencies or
preparing application requirements files.

No Gemini API calls, database connections or additional
Python packages are required.

### Limitations

- Local modules may be reported as unresolved.
- Shared namespaces may map to multiple distributions.
- Dynamic imports may not be detected.
- Command-line tools and optional package extras may
  require separate verification.
- Installed package versions do not independently
  establish runtime compatibility.

Use pip check and clean-environment regression testing
to complement static dependency analysis.

## Volume 1 - Live Integration Verification Results

Reference verification date: November 24, 2026.

All existing verification utilities were executed
using the clean Python reference environment.

| Verification utility | Result |
|---|---|
| verify_database_sql.py | 7/7 SQL scripts executed successfully |
| verify_category_metadata.py | Both JSON distributions matched |
| verify_category_hybrid_search.py | 3/3 scenarios passed |
| verify_agent_category_intent.py | 5/5 scenarios passed |
| verify_api_category_integration.py | 3/3 scenarios passed |

### Recommended Execution Order

1. Verify Python environment and dependencies.
2. Verify Google Cloud project configuration.
3. Verify Application Default Credentials.
4. Verify PostgreSQL readiness.
5. Execute database SQL verification.
6. Execute JSON category metadata verification.
7. Execute live hybrid search verification.
8. Execute live Gemini agent intent verification.
9. Execute live FastAPI integration verification.
10. Verify local HTTP endpoints through Uvicorn.

### Cost Considerations

The database and JSON metadata verification utilities
do not require Gemini model requests.

The expected model request counts for the live
verification utilities are:

| Verification | Generative requests | Embedding requests |
|---|---:|---:|
| Hybrid search | 0 | 3 |
| Agent intent | 5 | 0 |
| FastAPI integration | 3 | 3 |
| Total | 8 | 6 |

These estimates exclude retries and additional
manual HTTP search requests.

### Operational Considerations

- Confirm infrastructure availability before execution.
- Investigate failures before repeating live requests.
- Review actual SQL values in addition to execution status.
- Never display or commit authentication credentials.
- Do not regenerate stored embeddings unnecessarily.
- Record actual verification results before publication.

Successful verification represents the tested scenarios
and reference environment, not a guarantee of complete
production readiness.


## Documentation Reference Verification

Script: verify_documentation_references.py

Purpose:

Verify that local file references, Python module
references, dependency manifests and Markdown links
in the project documentation resolve successfully.

Execution:

    python -u scripts/verify_documentation_references.py

Reference verification date: November 24, 2026.

Initial verification results:

| Metric | Result |
|---|---:|
| Total detected references | 115 |
| Passed | 115 |
| Failed | 0 |

Additional manual source review confirmed:

- 24 documented backend module filenames.
- 24 backend module main entry points.
- Four documented search and agent function signatures.
- 34 command reference sections.

### Prerequisites

- Execute from the project repository root.
- Activate the appropriate Python virtual environment.
- Install the required project dependencies.

### Verification Boundaries

- Uses Python standard library modules.
- Does not execute backend application modules.
- Does not generate Gemini model requests.
- Does not modify database records.
- Does not validate external website availability.
- Does not independently verify command runtime behavior.
- Uses pattern-based reference detection.
- Reference counts may increase as documentation evolves.

A successful result confirms that detected references
resolve correctly, not that every documented command
has been independently execution-tested.
