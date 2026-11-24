-- Verify category metadata completeness

SELECT
    COUNT(*) AS total_songs,
    COUNT(category) AS populated_categories,
    COUNT(*) FILTER (
        WHERE category IS NULL
    ) AS null_categories,
    COUNT(*) FILTER (
        WHERE TRIM(category) = ''
    ) AS empty_categories
FROM song_embeddings;

-- Verify category distribution
SELECT
    category,
    COUNT(*) AS total_songs
FROM song_embeddings
GROUP BY category
ORDER BY total_songs DESC;
