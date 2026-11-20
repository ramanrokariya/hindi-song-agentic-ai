
import json
from pathlib import Path

import psycopg

from backend.incremental_enrichment_service import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent
EMBEDDINGS_FILE = PROJECT_ROOT / "data/hindi_song_embeddings.json"
PASSWORD_FILE = PROJECT_ROOT / ".env.postgres"


def load_database_password():
    for line in PASSWORD_FILE.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            return line.split("=", 1)[1]

    raise ValueError("POSTGRES_PASSWORD not found")


def import_embeddings():
    records = load_json(EMBEDDINGS_FILE)

    imported = 0

    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="hindi_songs",
        user="songadmin",
        password=load_database_password(),
    ) as connection:

        with connection.cursor() as cursor:
            for song in records:
                embedding = song["embedding"]

                if len(embedding) != 768:
                    raise ValueError(
                        f"Invalid embedding dimensions for "
                        f"{song['title']}"
                    )

                cursor.execute(
                    """
                    INSERT INTO song_embeddings (
                        musicbrainz_id,
                        title,
                        description,
                        embedding,
                        embedding_model
                    )
                    VALUES (%s, %s, %s, %s::vector, %s)
                    ON CONFLICT (musicbrainz_id)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        embedding = EXCLUDED.embedding,
                        embedding_model = EXCLUDED.embedding_model
                    """,
                    (
                        song["musicbrainz_id"],
                        song["title"],
                        song["description"],
                        json.dumps(embedding),
                        song["model"],
                    ),
                )

                imported += 1

    print("\n========== POSTGRESQL EMBEDDING IMPORT ==========")
    print("Records processed:", imported)
    print("Database: hindi_songs")
    print("Table: song_embeddings")
    print("Import completed successfully!")


if __name__ == "__main__":
    import_embeddings()

