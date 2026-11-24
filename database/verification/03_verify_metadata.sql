-- Verify metadata population

SELECT
    COUNT(*) AS total_songs,
    COUNT(genre) AS populated_genres,
    COUNT(mood) AS populated_moods,
    COUNT(listening_time) AS populated_listening_times,
    COUNT(occasion) AS populated_occasions,
    COUNT(artists) AS populated_artists
FROM song_embeddings;

-- Verify genre distribution
SELECT
    genre,
    COUNT(*) AS total_songs
FROM song_embeddings
GROUP BY genre
ORDER BY total_songs DESC;

-- Inspect sample metadata records
SELECT
    title,
    genre,
    mood,
    listening_time,
    occasion,
    artists
FROM song_embeddings
ORDER BY title, musicbrainz_id
LIMIT 10;
