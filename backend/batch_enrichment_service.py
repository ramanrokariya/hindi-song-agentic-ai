# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import os
import time
from backend.retry_policy import evaluate_retry 
from pathlib import Path
from backend.batch_metrics import calculate_batch_metrics
from google import genai
from google.genai import types

from backend.enrichment_service import classify_song
from backend.failure_tracker import (
    clear_failure,
    load_failures,
    record_failure,
    save_failures,
)
from backend.incremental_enrichment_service import (
    build_checkpoint,
    is_classified,
    load_json,
    save_json_atomic,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
SAMPLE_FILE = PROJECT_ROOT / "data/hindi_songs_three_sample.json"
OUTPUT_FILE = PROJECT_ROOT / "data/hindi_songs_incremental.json"
FAILURE_FILE = PROJECT_ROOT / "data/hindi_songs_failed.json"

MAX_API_ATTEMPTS = 3


def process_batch(
    catalog,
    checkpoint,
    client,
    max_attempts,
    output_file=OUTPUT_FILE,
    failures=None,
    failure_file=None,
):
    """Process a limited batch and optionally persist failures."""

    if max_attempts < 0:
        raise ValueError("max_attempts cannot be negative")

    if (failures is None) != (failure_file is None):
        raise ValueError(
            "Provide both failures and failure_file, or neither"
        )

    attempts = 0
    succeeded = 0
    failed = 0
    skipped = 0
    retry_blocked = 0
    for song in catalog:
        recording_id = song["musicbrainz_id"]
        title = song["title"]

        previous = checkpoint.get(recording_id)

        if previous and is_classified(previous):
            skipped += 1
            print(
                f"SKIP | MusicBrainz ID: {recording_id} "
                f"| Title: {title}"
            )
            continue

        if attempts >= max_attempts:
            print("Batch attempt limit reached.")
            break

        # Apply retry policy when failure tracking is enabled.
        if failures is not None:
            failure_record = failures.get(recording_id)

            allowed, reason = evaluate_retry(failure_record)

            if not allowed:
                retry_blocked += 1
                print(
                    f"RETRY BLOCKED | MusicBrainz ID: {recording_id} "
                    f"| Title: {title} | Reason: {reason}"
                )
                continue

        attempts += 1

        print(
            f"ATTEMPT {attempts}/{max_attempts} "
            f"| MusicBrainz ID: {recording_id} "
            f"| Title: {title}"
        )

        try:
            classification = classify_song(client, song)

        except Exception as exc:
            failed += 1

            print(
                f"FAILED | MusicBrainz ID: {recording_id} "
                f"| Title: {title} | Error: {exc}"
            )

            if failures is not None:
                failure_record = record_failure(
                    failures, song, exc
                )
                save_failures(failure_file, failures)

                print(
                    "FAILURE SAVED | "
                    f"Attempts: {failure_record['attempt_count']}"
                )

        else:
            enriched = dict(song)

            enriched["enrichment"] = {
                **classification.model_dump(),
                "raaga": None,
                "classification_source": "gemini_suggestion",
                "review_status": "pending",
            }

            # Save successful classification first.
            updated_checkpoint = dict(checkpoint)
            updated_checkpoint[recording_id] = enriched

            save_json_atomic(
                output_file,
                list(updated_checkpoint.values()),
            )

            checkpoint[recording_id] = enriched

            # Clear any previous failure only after saving success.
            if failures is not None:
                clear_failure(failures, recording_id)
                save_failures(failure_file, failures)

            succeeded += 1

            print(
                f"SUCCESS | MusicBrainz ID: {recording_id} "
                f"| Genre: {classification.genre}"
            )

        time.sleep(2)

    return {
        "attempts": attempts,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "total_saved": len(checkpoint),
        "retry_blocked": retry_blocked,
    }


def main():
    catalog = load_json(SOURCE_FILE)
    samples = load_json(SAMPLE_FILE)
    existing = load_json(OUTPUT_FILE)

    checkpoint = build_checkpoint(
        catalog, samples, existing
    )

    save_json_atomic(
        OUTPUT_FILE,
        list(checkpoint.values()),
    )

    failures = load_failures(FAILURE_FILE)

    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location="global",
        http_options=types.HttpOptions(api_version="v1"),
    )

    start_time = time.perf_counter()

    try:
        summary = process_batch(
            catalog=catalog,
            checkpoint=checkpoint,
            client=client,
            max_attempts=MAX_API_ATTEMPTS,
            output_file=OUTPUT_FILE,
            failures=failures,
            failure_file=FAILURE_FILE,
        )
    finally:
        duration_seconds = time.perf_counter() - start_time
        client.close()
    
    metrics = calculate_batch_metrics(
    summary,
    duration_seconds,
    )


    print("\n========== BATCH SUMMARY ==========")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("Output file:", OUTPUT_FILE)
    print("Failure file:", FAILURE_FILE)
    print("Unresolved failures:", len(failures))

    print("\n========== OPERATIONAL METRICS ==========")

    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

