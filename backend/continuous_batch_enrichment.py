
import argparse
import subprocess
import sys
import time
from pathlib import Path

from backend.incremental_enrichment_service import (
    load_json,
    is_classified,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CATALOG_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
ENRICHED_FILE = PROJECT_ROOT / "data/hindi_songs_incremental.json"

DEFAULT_MAX_BATCHES = 10
DEFAULT_DELAY_SECONDS = 3


def count_classified():
    songs = load_json(ENRICHED_FILE)

    return sum(
        1 for song in songs
        if is_classified(song)
    )


def count_total():
    return len(load_json(CATALOG_FILE))


def run_batch():
    """Execute the existing enrichment service."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backend.batch_enrichment_service",
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )

    return result.returncode == 0


def run_continuous_enrichment(
    max_batches=DEFAULT_MAX_BATCHES,
    delay_seconds=DEFAULT_DELAY_SECONDS,
):
    total = count_total()

    print("\n========== CONTINUOUS ENRICHMENT ==========", flush=True)
    print(f"Catalog recordings: {total}", flush=True)
    print(f"Initially classified: {count_classified()}", flush=True)
    print(f"Maximum batches: {max_batches}", flush=True)

    for batch_number in range(1, max_batches + 1):
        before = count_classified()

        if before >= total:
            print("\nAll recordings already classified.", flush=True)
            break

        print(
            f"\n========== GEMINI BATCH {batch_number} ==========",
            flush=True,
        )

        success = run_batch()

        if not success:
            print(
                "\nBatch service failed. Stopping safely.",
                flush=True,
            )
            break

        after = count_classified()

        print(
            f"\nClassified before: {before} | after: {after}",
            flush=True,
        )

        if after <= before:
            print(
                "No classification progress. "
                "Stopping to review failures or cooldown.",
                flush=True,
            )
            break

        if after >= total:
            print(
                "\nAll catalog recordings classified!",
                flush=True,
            )
            break

        if batch_number < max_batches:
            print(
                f"Waiting {delay_seconds} seconds...",
                flush=True,
            )
            time.sleep(delay_seconds)

    classified = count_classified()
    remaining = max(0, total - classified)

    coverage = (
        round(classified / total * 100, 2)
        if total else 0.0
    )

    print("\n========== FINAL ENRICHMENT SUMMARY ==========")
    print(f"Total recordings: {total}")
    print(f"Classified: {classified}")
    print(f"Remaining: {remaining}")
    print(f"Coverage: {coverage}%")
    print(f"Enrichment file: {ENRICHED_FILE}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Gemini enrichment in controlled batches."
    )

    parser.add_argument(
        "--max-batches",
        type=int,
        default=DEFAULT_MAX_BATCHES,
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
    )

    args = parser.parse_args()

    if args.max_batches < 1:
        parser.error("--max-batches must be at least 1")

    if args.delay < 0:
        parser.error("--delay cannot be negative")

    run_continuous_enrichment(
        max_batches=args.max_batches,
        delay_seconds=args.delay,
    )


if __name__ == "__main__":
    main()

