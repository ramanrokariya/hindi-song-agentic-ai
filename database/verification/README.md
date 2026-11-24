# PostgreSQL Verification Scripts

These read-only SQL scripts support database verification
for Volume 1 of Building an Agentic AI Song Search Engine.

## Prerequisites

- Running PostgreSQL pgvector Docker container
- Container name: hindi-song-postgres
- Database: hindi_songs
- Database user: songadmin
- Database schema and metadata migration applied
- Song embeddings and metadata imported

## Available verification scripts

| Script | Purpose |
|---|---|
| 01_verify_schema.sql | PostgreSQL version, pgvector extension, columns and indexes |
| 02_verify_embeddings.sql | Recording counts, unique IDs, vector dimensions and embedding models |
| 03_verify_metadata.sql | Metadata population and genre distribution |
| 04_verify_category.sql | Category population and distribution |
| 05_verify_hybrid_search.sql | Structured metadata filtering |
| 06_verify_database_recovery.sql | Database identity and recovered recording counts |
| 07_verify_category_filter.sql | Garba and Krishna Bhajan category filtering |

## Verify PostgreSQL readiness

Run from the repository root:

    docker exec hindi-song-postgres \
      pg_isready -U songadmin -d hindi_songs

## Execute an individual verification script

    docker exec -i hindi-song-postgres \
      psql -v ON_ERROR_STOP=1 \
      -U songadmin -d hindi_songs \
      < database/verification/01_verify_schema.sql

## Execute all SQL verification scripts

    for file in database/verification/*.sql; do
        echo "========================================"
        echo "Executing: $file"

        docker exec -i hindi-song-postgres \
          psql -v ON_ERROR_STOP=1 \
          -U songadmin -d hindi_songs \
          < "$file" || break
    done

## Reference dataset results

The Volume 1 reference dataset contains:

- Total recordings: 50
- Unique MusicBrainz IDs: 50
- Duplicate MusicBrainz IDs: 0
- Embedding dimensions: 768
- Populated categories: 32
- NULL categories: 18
- Garba recordings by category: 7
- Krishna Bhajan recordings by category: 7

Results may differ when using an expanded dataset.

## Important notes

- These scripts do not modify database records.
- No Gemini API calls are required.
- NULL category values are valid for uncategorized recordings.
- Different MusicBrainz IDs may have identical song titles.
- SQL script 05 verifies structured metadata filtering,
  not vector similarity ranking.
- Database recovery checks verify selected database
  properties, not complete backup integrity.
- These scripts provide diagnostic output rather than
  automated assertions for every expected value.

## Automated SQL Verification Using Python

Instead of manually executing each SQL file or using
the Bash loop, readers can use the reusable Python utility.

Execute all SQL verification scripts:

    python -u scripts/verify_database_sql.py

Execute an individual SQL verification script:

    python -u scripts/verify_database_sql.py \
      --file 04_verify_category.sql

The utility checks PostgreSQL readiness, executes the
selected SQL files and reports passed and failed scripts.

No additional Python packages or Gemini API calls
are required.
