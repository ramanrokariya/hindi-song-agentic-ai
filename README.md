
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
