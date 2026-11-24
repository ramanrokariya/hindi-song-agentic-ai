# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
import time
from pathlib import Path

from backend.embedding_service import generate_embedding
from backend.incremental_enrichment_service import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENRICHED_FILE = (
    PROJECT_ROOT / "data/hindi_songs_incremental.json"
)

EMBEDDINGS_FILE = (
    PROJECT_ROOT / "data/hindi_song_embeddings.json"
)


def format_value(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    if value is None:
        return ""

    return str(value)


def build_song_description(song):
    enrichment = song.get("enrichment") or {}

    fields = {
        "Title": song.get("title"),
        "Artists": song.get("artists", []),
        "Genre": enrichment.get("genre"),
        "Mood": enrichment.get("mood", []),
        "Listening time": enrichment.get(
            "listening_time", []
        ),
        "Occasion": enrichment.get("occasion", []),
        "Category": song.get(
            "discovery_category_hint"
        ),
    }

    return ". ".join(
        f"{key}: {format_value(value)}"
        for key, value in fields.items()
        if format_value(value)
    )


def load_existing_embeddings():
    if not EMBEDDINGS_FILE.exists():
        return []

    return load_json(EMBEDDINGS_FILE)


def save_embeddings(records):
    EMBEDDINGS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = EMBEDDINGS_FILE.with_suffix(
        ".json.tmp"
    )

    with temporary_file.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(EMBEDDINGS_FILE)


def main():
    songs = load_json(ENRICHED_FILE)
    records = load_existing_embeddings()

    existing_ids = {
        record["musicbrainz_id"]
        for record in records
    }

    print("\n========== SONG EMBEDDING GENERATION ==========")
    print("Songs in catalog:", len(songs))
    print("Existing embeddings:", len(records))

    generated = 0
    skipped = 0
    failed = 0

    for index, song in enumerate(songs, start=1):
        musicbrainz_id = song.get("musicbrainz_id")

        if not musicbrainz_id:
            failed += 1
            print(f"[{index}] Missing MusicBrainz ID")
            continue

        if musicbrainz_id in existing_ids:
            skipped += 1
            continue

        description = build_song_description(song)

        try:
            vector = generate_embedding(
                description,
                task_type="RETRIEVAL_DOCUMENT",
            )

            record = {
                "musicbrainz_id": musicbrainz_id,
                "title": song.get("title"),
                "description": description,
                "model": "gemini-embedding-001",
                "dimensions": len(vector),
                "embedding": vector,
            }

            records.append(record)
            existing_ids.add(musicbrainz_id)

            save_embeddings(records)

            generated += 1

            print(
                f"[{index}/{len(songs)}] "
                f"Embedded: {song.get('title')}"
            )

            time.sleep(0.5)

        except Exception as exc:
            failed += 1
            print(
                f"[{index}/{len(songs)}] "
                f"FAILED: {song.get('title')} "
                f"- {exc}"
            )

            # Stop on the first API error.
            # The saved checkpoint allows safe resumption.
            break

    print("\n========== EMBEDDING SUMMARY ==========")
    print("New embeddings:", generated)
    print("Skipped existing:", skipped)
    print("Failures:", failed)
    print("Total saved:", len(records))
    print("Output file:", EMBEDDINGS_FILE)


if __name__ == "__main__":
    main()

