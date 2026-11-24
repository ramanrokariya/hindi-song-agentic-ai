# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
import os
import time
from pathlib import Path

from google import genai
from google.genai import types

from backend.enrichment_service import classify_song


# -------------------------------------------------
# Project paths
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
SAMPLE_FILE = PROJECT_ROOT / "data/hindi_songs_three_sample.json"
OUTPUT_FILE = PROJECT_ROOT / "data/hindi_songs_incremental.json"

# Maximum number of NEW successful classifications per run
MAX_NEW_RECORDS = 3


# -------------------------------------------------
# JSON utilities
# -------------------------------------------------

def load_json(path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"Expected a JSON list in {path}")

    return records


def save_json_atomic(path, records):
    """
    Write JSON to a temporary file and atomically
    replace the destination after writing succeeds.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = path.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    temporary_file.replace(path)


# -------------------------------------------------
# Classification helpers
# -------------------------------------------------

def is_classified(song):
    enrichment = song.get("enrichment", {})

    return (
        enrichment.get("classification_source")
        == "gemini_suggestion"
    )


def build_checkpoint(catalog, samples, existing):
    """
    Merge sample and existing enrichment records
    using the unique MusicBrainz recording ID.
    """

    catalog_ids = {
        song["musicbrainz_id"]
        for song in catalog
    }

    checkpoint = {}

    for song in samples + existing:
        recording_id = song["musicbrainz_id"]

        if recording_id not in catalog_ids:
            continue

        previous = checkpoint.get(recording_id)

        if previous is None:
            checkpoint[recording_id] = song

        elif is_classified(song) and not is_classified(previous):
            checkpoint[recording_id] = song

    return checkpoint


# -------------------------------------------------
# Main enrichment workflow
# -------------------------------------------------

def main():

    catalog = load_json(SOURCE_FILE)
    samples = load_json(SAMPLE_FILE)
    existing = load_json(OUTPUT_FILE)

    print("\n========== CATALOG INFORMATION ==========")
    print(f"Catalog records: {len(catalog)}")
    print(f"Sample records: {len(samples)}")
    print(f"Existing checkpoint records: {len(existing)}")

    checkpoint = build_checkpoint(
        catalog,
        samples,
        existing
    )

    # Persist reused classifications before API calls.
    save_json_atomic(
        OUTPUT_FILE,
        list(checkpoint.values())
    )

    print(f"Reusable checkpoint records: {len(checkpoint)}")

    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location="global",
        http_options=types.HttpOptions(api_version="v1")
    )

    processed = 0
    skipped = 0
    failed = 0

    try:

        for song in catalog:

            recording_id = song["musicbrainz_id"]
            title = song["title"]

            previous = checkpoint.get(recording_id)

            # -------------------------------------
            # Skip already classified recordings
            # -------------------------------------

            if previous and is_classified(previous):

                print(
                    f"SKIP   | MusicBrainz ID: {recording_id} "
                    f"| Title: {title}"
                )

                skipped += 1
                continue

            # -------------------------------------
            # Stop after test batch limit
            # -------------------------------------

            if processed >= MAX_NEW_RECORDS:

                print("\nReached test batch limit.")
                break

            # -------------------------------------
            # Classify new recording using Gemini
            # -------------------------------------

            print(
                f"\nENRICH | MusicBrainz ID: {recording_id} "
                f"| Title: {title}"
            )

            try:

                classification = classify_song(
                    client,
                    song
                )

                enriched = dict(song)

                enriched["enrichment"] = {
                    **classification.model_dump(),
                    "raaga": None,
                    "classification_source": "gemini_suggestion",
                    "review_status": "pending"
                }

                # Update checkpoint by recording ID
                checkpoint[recording_id] = enriched

                processed += 1

                # Save after each successful classification
                save_json_atomic(
                    OUTPUT_FILE,
                    list(checkpoint.values())
                )

                print(
                    f"SUCCESS | MusicBrainz ID: {recording_id} "
                    f"| Genre: {classification.genre}"
                )

            except Exception as exc:

                failed += 1

                print(
                    f"FAILED | MusicBrainz ID: {recording_id} "
                    f"| Title: {title} | Error: {exc}"
                )

                # Failed records remain eligible
                # for classification on future runs.
                continue

            # Avoid sending Gemini requests too rapidly.
            time.sleep(2)

    finally:
        client.close()

    print("\n========== ENRICHMENT SUMMARY ==========")
    print(f"New classifications: {processed}")
    print(f"Skipped existing: {skipped}")
    print(f"Failed classifications: {failed}")
    print(f"Total checkpoint records: {len(checkpoint)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

