
-- Step 16.7
-- Add structured metadata to song_embeddings.

BEGIN;

ALTER TABLE song_embeddings
    ADD COLUMN IF NOT EXISTS genre TEXT,
    ADD COLUMN IF NOT EXISTS mood TEXT[],
    ADD COLUMN IF NOT EXISTS listening_time TEXT[],
    ADD COLUMN IF NOT EXISTS occasion TEXT[],
    ADD COLUMN IF NOT EXISTS category TEXT,
    ADD COLUMN IF NOT EXISTS artists TEXT[];

-- Indexes for frequently used metadata filters.

CREATE INDEX IF NOT EXISTS idx_song_genre
    ON song_embeddings (genre);

CREATE INDEX IF NOT EXISTS idx_song_listening_time
    ON song_embeddings USING GIN (listening_time);

CREATE INDEX IF NOT EXISTS idx_song_mood
    ON song_embeddings USING GIN (mood);

CREATE INDEX IF NOT EXISTS idx_song_occasion
    ON song_embeddings USING GIN (occasion);

COMMIT;

