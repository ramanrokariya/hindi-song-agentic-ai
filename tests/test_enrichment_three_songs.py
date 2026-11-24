# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
import os
import random
import time
from pathlib import Path

from google import genai
from google.genai import types

from backend.enrichment_service import classify_song


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
OUTPUT_FILE = PROJECT_ROOT / "data/hindi_songs_three_sample.json"


def main():
    with SOURCE_FILE.open(encoding="utf-8") as f:
        songs = json.load(f)

    # Select three recordings with distinct titles.
    selected = []
    seen_titles = set()

    for song in songs:
        title = song["title"].strip().casefold()

        if title not in seen_titles:
            selected.append(song)
            seen_titles.add(title)

        if len(selected) == 3:
            break

    print(f"Selected {len(selected)} distinct songs")

    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location="global",
        http_options=types.HttpOptions(api_version="v1")
    )

    results = []

    try:
        for song in selected:
            print(f"\nProcessing: {song['title']}")

            enriched = dict(song)

            try:
                classification = classify_song(client, song)

                enriched["enrichment"] = {
                    **classification.model_dump(),
                    "raaga": None,
                    "classification_source": "gemini_suggestion",
                    "review_status": "pending"
                }

            except Exception as exc:
                print(f"Classification failed: {exc}")

                enriched["enrichment"] = {
                    "genre": "unknown",
                    "mood": [],
                    "listening_time": [],
                    "occasion": [],
                    "raaga": None,
                    "classification_source": "unclassified",
                    "review_status": "pending"
                }

            results.append(enriched)

            # Space out Gemini API calls.
            time.sleep(2)

    finally:
        client.close()

    # Save to a separate file, leaving existing data untouched.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    temporary_file.replace(OUTPUT_FILE)

    print(f"\nSaved {len(results)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

