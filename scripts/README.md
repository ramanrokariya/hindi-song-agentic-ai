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
