# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CATALOG_FILE = (
    PROJECT_ROOT / "data" / "hindi_songs_incremental.json"
)

PASSWORD_FILE = PROJECT_ROOT / ".env.postgres"


def load_password():
    for line in PASSWORD_FILE.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")

    raise ValueError("POSTGRES_PASSWORD not found")


def as_text_array(value):
    if value is None:
        return None

    if isinstance(value, list):
        return [str(item) for item in value if item is not None]

    return [str(value)]


def main():
    records = json.loads(CATALOG_FILE.read_text())

    updated = 0
    missing = 0

    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="hindi_songs",
        user="songadmin",
        password=load_password(),
    ) as connection:

        with connection.cursor() as cursor:

            for song in records:
                enrichment = song.get("enrichment") or {}

                cursor.execute(
                    """
                    UPDATE song_embeddings
                    SET
                        genre = %s,
                        mood = %s,
                        listening_time = %s,
                        occasion = %s,
                        category = %s,
                        artists = %s
                    WHERE musicbrainz_id = %s
                    """,
                    (
                        enrichment.get("genre"),
                        as_text_array(enrichment.get("mood")),
                        as_text_array(
                            enrichment.get("listening_time")
                        ),
                        as_text_array(enrichment.get("occasion")),
                        song.get("discovery_category_hint"),
                        as_text_array(song.get("artists")),
                        song["musicbrainz_id"],
                    ),
                )

                if cursor.rowcount == 1:
                    updated += 1
                else:
                    missing += 1

        connection.commit()

    print("\n========== POSTGRESQL METADATA IMPORT ==========")
    print("Catalog records:", len(records))
    print("Database rows updated:", updated)
    print("Records without matching database row:", missing)
    print("Import completed successfully!")


if __name__ == "__main__":
    main()

