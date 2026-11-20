
-- Hindi Song Agentic AI
-- PostgreSQL + pgvector database schema

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS song_embeddings (
    musicbrainz_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,
    embedding_model TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_song_embeddings_title
ON song_embeddings (title);

