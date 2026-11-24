-- Verify database connectivity
SELECT
    current_database() AS database_name,
    current_user AS database_user;

-- Verify recovered song records
SELECT
    COUNT(*) AS total_songs
FROM song_embeddings;

-- Verify recovered embeddings and record uniqueness
SELECT
    COUNT(DISTINCT musicbrainz_id) AS unique_songs,
    COUNT(embedding) AS populated_embeddings,
    MIN(vector_dims(embedding)) AS min_dimensions,
    MAX(vector_dims(embedding)) AS max_dimensions
FROM song_embeddings;
