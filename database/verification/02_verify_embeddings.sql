-- Verify record uniqueness and embedding dimensions

SELECT
    COUNT(*) AS total_songs,
    COUNT(DISTINCT musicbrainz_id) AS unique_songs,
    COUNT(*) - COUNT(DISTINCT musicbrainz_id)
        AS duplicate_ids,
    MIN(vector_dims(embedding)) AS min_dimensions,
    MAX(vector_dims(embedding)) AS max_dimensions
FROM song_embeddings;

-- Verify embedding model distribution
SELECT
    embedding_model,
    COUNT(*) AS total_songs
FROM song_embeddings
GROUP BY embedding_model
ORDER BY total_songs DESC;
