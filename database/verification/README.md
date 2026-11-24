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

## Final Volume 1 Database Reference Verification

Verification date: November 24, 2026.

The final database reference values were explicitly
reviewed against the actual PostgreSQL query results.

### Database Environment

| Component | Verified value |
|---|---|
| PostgreSQL | 16.16 |
| pgvector | 0.8.7 |
| Architecture | x86_64, 64-bit |
| Database columns | 12 |
| Database indexes | 6 |

### Embedding Integrity

| Metric | Verified value |
|---|---:|
| Total songs | 50 |
| Unique MusicBrainz IDs | 50 |
| Duplicate IDs | 0 |
| Minimum embedding dimensions | 768 |
| Maximum embedding dimensions | 768 |
| Records using gemini-embedding-001 | 50 |

### Category Distribution

| Metric | Verified value |
|---|---:|
| Total songs | 50 |
| Populated categories | 32 |
| NULL categories | 18 |
| Empty categories | 0 |
| Garba | 7 |
| Krishna Bhajan | 7 |
| Devotional | 6 |
| Folk | 6 |
| Patriotic | 6 |

### Schema Verification

The following column types were verified:

- musicbrainz_id: TEXT
- title: TEXT
- description: TEXT
- embedding: VECTOR
- embedding_model: TEXT
- created_at: TIMESTAMPTZ
- genre: TEXT
- mood: TEXT[]
- listening_time: TEXT[]
- occasion: TEXT[]
- category: TEXT
- artists: TEXT[]

### Index Verification

The following six indexes were verified:

- song_embeddings_pkey: Unique B-tree on musicbrainz_id.
- idx_song_embeddings_title: B-tree on title.
- idx_song_genre: B-tree on genre.
- idx_song_listening_time: GIN on listening_time.
- idx_song_mood: GIN on mood.
- idx_song_occasion: GIN on occasion.

### Final Verification Conclusion

All seven SQL verification scripts executed successfully.

The actual embedding integrity, category distribution,
column types and index definitions matched the expected
Volume 1 reference implementation.

The listening_time column was explicitly confirmed
as TEXT[] with a GIN index.

The database category distribution also matched the
previously reviewed JSON catalog distribution.

No database modifications or additional model requests
were required during this final verification.

### Verification Boundaries

These results describe the tested reference dataset
and database environment.

They do not independently establish:

- Per-record equivalence between JSON and database metadata.
- Semantic search relevance or classification accuracy.
- Query execution plan efficiency.
- Index utilization for every search query.
- Large-scale database performance.
- Production database readiness.
