# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
import os
import random
import time
from pathlib import Path
from typing import Literal

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
OUTPUT_FILE = PROJECT_ROOT / "data/hindi_songs_enriched.json"


class SongClassification(BaseModel):
    genre: Literal[
        "devotional", "romantic", "folk",
        "patriotic", "other", "unknown"
    ]
    mood: list[str] = Field(default_factory=list)
    listening_time: list[str] = Field(default_factory=list)
    occasion: list[str] = Field(default_factory=list)


def classify_song(client, song):
    title = song["title"]
    artists = song.get("artists", [])

    prompt = f"""
You are assisting with Hindi music catalog enrichment.

Classify the following recording using only the metadata supplied.

Title: {title}
Artists: {", ".join(artists)}

Return suggested genre, mood, listening time, and occasion.

Rules:
- Do not invent recording-specific facts.
- If the title and artist do not provide enough evidence,
  use "unknown" for genre and empty lists for other fields.
- Treat ambiguous song titles conservatively.
- Do not infer Raaga.
- Return structured JSON matching the provided schema.
"""

    max_attempts = 4

    for attempt in range(1, max_attempts + 1):
        try:
            print(
                f"Classifying '{title}' "
                f"(attempt {attempt}/{max_attempts})"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=SongClassification,
                    max_output_tokens=2048
                )
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response")


            print("Response length:", len(response.text))
            print("Raw Gemini response:", repr(response.text))
            
            if response.candidates:
                print(
                    "Finish reason:",
                    response.candidates[0].finish_reason
            )

            if response.usage_metadata:
                print(
                    "Token usage:",
                    response.usage_metadata
            )   



            return SongClassification.model_validate_json(
                response.text
            )

        except (ClientError, ServerError) as exc:
            if exc.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_attempts:
                raise

            delay = min(2 ** attempt, 30) + random.uniform(0, 1)

            print(
                f"Vertex AI HTTP {exc.code}. "
                f"Retrying in {delay:.1f} seconds..."
            )
            time.sleep(delay)

    raise RuntimeError("Classification failed")


def main():
    with SOURCE_FILE.open(encoding="utf-8") as file:
        songs = json.load(file)

    print(f"Loaded {len(songs)} MusicBrainz recordings")

    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location="global",
        http_options=types.HttpOptions(api_version="v1")
    )

    enriched_songs = []

    # Limit initial test to three recordings
    for song in songs[:3]:
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
            print(
                f"Classification failed for "
                f"'{song['title']}': {exc}"
            )

            enriched["enrichment"] = {
                "genre": "unknown",
                "mood": [],
                "listening_time": [],
                "occasion": [],
                "raaga": None,
                "classification_source": "unclassified",
                "review_status": "pending"
            }

        enriched_songs.append(enriched)

        # Space out requests to reduce burst traffic
        time.sleep(2)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(
            enriched_songs,
            file,
            indent=2,
            ensure_ascii=False
        )

    temporary_file.replace(OUTPUT_FILE)

    print(f"\nSaved {len(enriched_songs)} enriched recordings")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

