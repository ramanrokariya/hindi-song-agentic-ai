# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import pandas as pd

from backend.incremental_enrichment_service import load_json
from backend.song_search_service import ENRICHED_FILE


def build_mood_report(songs):
    records = []

    for song in songs:
        enrichment = song.get("enrichment") or {}
        moods = enrichment.get("mood") or []

        if isinstance(moods, str):
            moods = [moods]

        for mood in moods:
            records.append({
                "title": song.get("title", ""),
                "mood": str(mood).strip().casefold(),
            })

    return pd.DataFrame(records, columns=["title", "mood"])


def main():
    songs = load_json(ENRICHED_FILE)
    df = build_mood_report(songs)

    print("\n========== MOOD DISTRIBUTION ==========")

    if df.empty:
        print("No mood classifications found.")
        return


    print(
        df["mood"]
        .value_counts()
        .sort_index(ascending=True)
        .to_string()
        )   


    print("\n========== SAD-RELATED MOOD EXAMPLES ==========")

    keywords = [
        "sad",
        "melanchol",
        "nostalg",
        "soulful",
        "emotional",
        "heartbreak",
        "longing",
    ]

    matches = df[
        df["mood"].apply(
            lambda mood: any(
                keyword in mood for keyword in keywords
            )
        )
    ]

    if matches.empty:
        print("No sad-related mood labels found.")
    else:
        print(matches.to_string(index=False))


if __name__ == "__main__":
    main()

