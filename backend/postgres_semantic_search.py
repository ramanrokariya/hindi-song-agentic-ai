# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
from pathlib import Path

import psycopg

from backend.embedding_service import generate_embedding


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASSWORD_FILE = PROJECT_ROOT / ".env.postgres"


def load_database_password():
    for line in PASSWORD_FILE.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            return line.split("=", 1)[1]

    raise ValueError("POSTGRES_PASSWORD not found")


def postgres_semantic_search(query, limit=5):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must not be empty")

    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    # Generate a query embedding using Gemini.
    query_embedding = generate_embedding(
        query,
        task_type="RETRIEVAL_QUERY",
    )

    # Convert the 768-dimensional vector to pgvector format.
    vector_string = json.dumps(query_embedding)

    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="hindi_songs",
        user="songadmin",
        password=load_database_password(),
    ) as connection:

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    musicbrainz_id,
                    title,
                    description,
                    ROUND(
                        (1 - (embedding <=> %s::vector))::numeric,
                        4
                    ) AS similarity
                FROM song_embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    vector_string,
                    vector_string,
                    limit,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "musicbrainz_id": row[0],
            "title": row[1],
            "description": row[2],
            "similarity": float(row[3]),
        }
        for row in rows
    ]


def main():
    print("\n========== POSTGRESQL SEMANTIC SEARCH ==========")
    print("Type 'exit' to quit.")

    while True:
        try:
            query = input("\nPostgres Search> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            results = postgres_semantic_search(query)

            print("\nResults returned:", len(results))

            for index, song in enumerate(results, start=1):
                print(
                    f"{index}. {song['title']} "
                    f"| Similarity: {song['similarity']:.4f}"
                )

        except Exception as exc:
            print("Search error:", exc)


if __name__ == "__main__":
    main()

