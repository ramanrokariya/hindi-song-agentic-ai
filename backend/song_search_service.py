# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from pathlib import Path

import pandas as pd

from backend.incremental_enrichment_service import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CATALOG_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
ENRICHED_FILE = PROJECT_ROOT / "data/hindi_songs_incremental.json"


MOOD_SYNONYMS = {
    "sad": {
        "sad",
        "melancholic",
        "melancholy",
        "heartbroken",
        "heartbreak",
    },
    "happy": {
        "happy",
        "joyful",
        "cheerful",
    },
    "peaceful": {
        "peaceful",
        "calm",
        "relaxing",
    },
    "energetic": {
        "energetic",
        "upbeat",
        "lively",
    },
}


def matches_mood(value, expected):
    if not expected:
        return True

    expected = str(expected).casefold().strip()
    accepted = MOOD_SYNONYMS.get(expected, {expected})

    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        return False

    return any(
        str(item).casefold().strip() in accepted
        for item in values
    )




def contains_value(value, expected):
    """
    Case-insensitive search against a string or list.
    """
    if expected is None or not str(expected).strip():
        return True

    expected = str(expected).casefold().strip()

    if isinstance(value, list):
        return any(
            expected in str(item).casefold()
            for item in value
        )

    if isinstance(value, str):
        return expected in value.casefold()

    return False


def build_search_dataframe(
    catalog_file=CATALOG_FILE,
    enriched_file=ENRICHED_FILE,
):
    """
    Join MusicBrainz catalog and Gemini enrichment
    using musicbrainz_id.
    """
    catalog = load_json(catalog_file)
    enriched = load_json(enriched_file)

    catalog_df = pd.DataFrame(catalog)
    enriched_df = pd.DataFrame(enriched)

    if catalog_df.empty:
        return pd.DataFrame()

    if enriched_df.empty:
        catalog_df["enrichment"] = None
        return catalog_df

    enrichment_columns = enriched_df[
        ["musicbrainz_id", "enrichment"]
    ]

    # Duplicate IDs should be detected, not silently removed.
    return catalog_df.drop(
        columns=["enrichment"],
        errors="ignore",
    ).merge(
        enrichment_columns,
        on="musicbrainz_id",
        how="left",
        validate="one_to_one",
    )




def rank_and_deduplicate(songs, unique_titles=False):
    """
    Preserve search order and optionally return
    one recording per normalized song title.
    """
    if not unique_titles:
        return songs

    seen_titles = set()
    unique_songs = []

    for song in songs:
        normalized_title = " ".join(
            song["title"].casefold().split()
        )

        if normalized_title in seen_titles:
            continue

        seen_titles.add(normalized_title)
        unique_songs.append(song)

    return unique_songs





def search_songs(
    genre=None,
    mood=None,
    listening_time=None,
    occasion=None,
    category=None,
    limit=10,
    unique_titles=False,
    catalog_file=CATALOG_FILE,
    enriched_file=ENRICHED_FILE,
):
    """
    Search songs using structured metadata filters.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")

    df = build_search_dataframe(
        catalog_file,
        enriched_file,
    )

    if df.empty:
        return []

    results = []

    for song in df.to_dict(orient="records"):
        enrichment = song.get("enrichment")

        if not isinstance(enrichment, dict):
            enrichment = {}

        if not contains_value(
            enrichment.get("genre"), genre
        ):
            continue


        if not matches_mood(
            enrichment.get("mood"), mood
        ):
            continue


        if not contains_value(
            enrichment.get("listening_time"),
            listening_time,
        ):
            continue

        if not contains_value(
            enrichment.get("occasion"),
            occasion,
        ):
            continue

        if not contains_value(
            song.get("discovery_category_hint"),
            category,
        ):
            continue

        results.append({
            "musicbrainz_id": song["musicbrainz_id"],
            "title": song["title"],
            "artists": song.get("artists", []),
            "genre": enrichment.get("genre"),
            "mood": enrichment.get("mood", []),
            "listening_time": enrichment.get(
                "listening_time", []
            ),
            "occasion": enrichment.get("occasion", []),
            "category_hint": song.get(
                "discovery_category_hint"
            ),
        })


        results = rank_and_deduplicate(
            results,
            unique_titles=unique_titles,
        )

    return results[:limit] 
