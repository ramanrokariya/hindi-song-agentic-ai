# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
from pathlib import Path

import psycopg

from backend.embedding_service import generate_embedding


ROOT = Path(__file__).resolve().parent.parent
PASSWORD_FILE = ROOT / ".env.postgres"


def load_password():
    for line in PASSWORD_FILE.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("POSTGRES_PASSWORD not found")


def hybrid_search(
    query,
    genre=None,
    mood=None,
    listening_time=None,
    occasion=None,
    category=None,
    limit=5,
):
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    embedding = generate_embedding(
        query,
        task_type="RETRIEVAL_QUERY",
    )
    vector = json.dumps(embedding)

    sql = """
        SELECT
            musicbrainz_id,
            title,
            description,
            genre,
            mood,
            listening_time,
            occasion,
            category,
            ROUND(
                (1 - (embedding <=> %s::vector))::numeric,
                4
            ) AS similarity
        FROM song_embeddings
        WHERE (%s::text IS NULL OR genre = %s)
          AND (%s::text IS NULL OR %s = ANY(mood))
          AND (%s::text IS NULL OR %s = ANY(listening_time))
          AND (%s::text IS NULL OR %s = ANY(occasion))
          AND (%s::text IS NULL OR category = %s)
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    parameters = (
        vector,
        genre, genre,
        mood, mood,
        listening_time, listening_time,
        occasion, occasion,
        category, category,
        vector,
        limit,
    )

    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="hindi_songs",
        user="songadmin",
        password=load_password(),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()

    return [
        {
            "musicbrainz_id": row[0],
            "title": row[1],
            "description": row[2],
            "genre": row[3],
            "mood": row[4],
            "listening_time": row[5],
            "occasion": row[6],
            "category": row[7],
            "similarity": float(row[8]),
            "structured_match": True,
        }
        for row in rows
    ]


def main():
    print("\n========== POSTGRESQL HYBRID SEARCH ==========")

    query = "peaceful Krishna bhajans suitable for early morning"

    print("Query:", query)
    print("Genre: devotional")
    print("Mood: peaceful")
    print("Listening time: morning")

    results = hybrid_search(
        query=query,
        genre="devotional",
        mood="peaceful",
        listening_time="morning",
        limit=5,
    )

    print("\nResults returned:", len(results))

    for index, song in enumerate(results, start=1):
        print(
            f"{index}. {song['title']} "
            f"| Similarity: {song['similarity']:.4f} "
            f"| Genre: {song['genre']} "
            f"| Mood: {song['mood']} "
            f"| Time: {song['listening_time']}"
        )


if __name__ == "__main__":
    main()

