# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import pandas as pd

from backend.catalog_quality_report import (
    CATALOG_FILE,
    ENRICHED_FILE,
)
from backend.incremental_enrichment_service import load_json


def find_unclassified_songs(catalog, enriched):
    """Return catalog recordings without Gemini classifications."""

    catalog_df = pd.DataFrame(catalog)

    if catalog_df.empty:
        return pd.DataFrame(
            columns=["musicbrainz_id", "title", "artists"]
        )

    classified_ids = {
        song["musicbrainz_id"]
        for song in enriched
        if (song.get("enrichment") or {}).get(
            "classification_source"
        ) == "gemini_suggestion"
    }

    unclassified_df = catalog_df.loc[
        ~catalog_df["musicbrainz_id"].isin(classified_ids),
        ["musicbrainz_id", "title", "artists"],
    ].copy()

    unclassified_df["artists"] = (
        unclassified_df["artists"].apply(
            lambda artists: ", ".join(artists)
            if isinstance(artists, list)
            else ""
        )
    )

    return unclassified_df.reset_index(drop=True)


def main():
    catalog = load_json(CATALOG_FILE)
    enriched = load_json(ENRICHED_FILE)

    unclassified_df = find_unclassified_songs(
        catalog,
        enriched,
    )

    print("\n========== UNCLASSIFIED HINDI SONGS ==========")

    if unclassified_df.empty:
        print("All catalog recordings are classified.")
    else:
        print(unclassified_df.to_string(index=False))

    print("\nTotal unclassified:", len(unclassified_df))


if __name__ == "__main__":
    main()

