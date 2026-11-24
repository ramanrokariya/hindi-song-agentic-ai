-- Verify category-based structured filtering

SELECT
    musicbrainz_id,
    title,
    genre,
    category
FROM song_embeddings
WHERE category = 'garba'
ORDER BY title, musicbrainz_id;

-- Verify Krishna Bhajan category filtering

SELECT
    musicbrainz_id,
    title,
    genre,
    category
FROM song_embeddings
WHERE category = 'krishna_bhajan'
ORDER BY title, musicbrainz_id;
