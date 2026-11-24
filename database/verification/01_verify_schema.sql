-- Verify PostgreSQL version
SELECT version();

-- Verify pgvector extension
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';

-- Verify table column definitions
SELECT
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'song_embeddings'
ORDER BY ordinal_position;

-- Verify database indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'song_embeddings'
ORDER BY indexname;
