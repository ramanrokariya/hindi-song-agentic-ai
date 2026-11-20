
import time
from pathlib import Path

from backend.musicbrainz_client import MusicBrainzClient
from backend.song_search_seeds import get_search_seeds
from backend.incremental_enrichment_service import (
    load_json,
    save_json_atomic,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"

SEARCH_LIMIT = 5
REQUEST_DELAY_SECONDS = 1.2


def normalize_musicbrainz_record(record, search_term, category_hint):
    """Convert a raw MusicBrainz recording into our catalog format."""

    recording_id = record.get("id")
    title = record.get("title")

    if not recording_id or not title:
        raise ValueError("MusicBrainz recording missing id or title")

    artists = []

    for credit in record.get("artist-credit", []):
        if not isinstance(credit, dict):
            continue

        artist = credit.get("artist", {})

        if isinstance(artist, dict):
            name = artist.get("name")

            if name:
                artists.append(name)

    return {
        "musicbrainz_id": recording_id,
        "title": title,
        "artists": artists,
        "search_term": search_term,
        "discovery_category_hint": category_hint,
    }


def expand_catalog(
    client,
    seeds,
    catalog_file=CATALOG_FILE,
    search_limit=SEARCH_LIMIT,
    request_delay=REQUEST_DELAY_SECONDS,
):
    """Expand the catalog while preserving existing recordings."""

    existing = load_json(catalog_file)

    catalog = {
        song["musicbrainz_id"]: song
        for song in existing
    }

    initial_count = len(catalog)

    added = 0
    duplicates = 0
    failed_searches = 0
    completed_searches = 0
    invalid_records = 0

    for seed in seeds:
        title = seed["title"]
        category_hint = seed["category_hint"]

        print(f"\nSEARCH | {title} | Hint: {category_hint}")

        try:
            results = client.search_songs(
                title,
                limit=search_limit,
            )

        except Exception as exc:
            failed_searches += 1
            print(f"SEARCH FAILED | {title} | Error: {exc}")
            time.sleep(request_delay)
            continue

        for record in results:
            try:
                song = normalize_musicbrainz_record(
                    record,
                    search_term=title,
                    category_hint=category_hint,
                )

            except (ValueError, TypeError, AttributeError) as exc:
                invalid_records += 1
                print(f"INVALID RECORD | {title} | Error: {exc}")
                continue

            recording_id = song["musicbrainz_id"]

            if recording_id in catalog:
                duplicates += 1
                continue

            catalog[recording_id] = song
            added += 1

        # Save after each successful search.
        save_json_atomic(
            catalog_file,
            list(catalog.values()),
        )

        completed_searches += 1

        print(
            f"SAVED | New: {added} | Total: {len(catalog)}"
        )

        time.sleep(request_delay)

    return {
        "initial_recordings": initial_count,
        "new_recordings": added,
        "duplicate_results": duplicates,
        "invalid_records": invalid_records,
        "completed_searches": completed_searches,
        "failed_searches": failed_searches,
        "total_recordings": len(catalog),
    }


def main():
    client = MusicBrainzClient()

    summary = expand_catalog(
        client=client,
        seeds=get_search_seeds(),
    )

    print("\n========== EXPANDED INGESTION SUMMARY ==========")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("Catalog file:", CATALOG_FILE)


if __name__ == "__main__":
    main()

