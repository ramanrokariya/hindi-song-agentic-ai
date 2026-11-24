-- Verify morning listening-time filtering

SELECT
    title,
    genre,
    listening_time
FROM song_embeddings
WHERE 'morning' = ANY(listening_time)
ORDER BY title, musicbrainz_id
LIMIT 10;

-- Verify devotional genre and morning filtering

SELECT
    title,
    genre,
    mood,
    listening_time
FROM song_embeddings
WHERE genre = 'devotional'
  AND 'morning' = ANY(listening_time)
ORDER BY title, musicbrainz_id
LIMIT 10;
