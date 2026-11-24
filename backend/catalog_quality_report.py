# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from pathlib import Path

import numpy as np
import pandas as pd

from backend.incremental_enrichment_service import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CATALOG_FILE = PROJECT_ROOT / "data/hindi_songs_catalog.json"
ENRICHED_FILE = PROJECT_ROOT / "data/hindi_songs_incremental.json"


def build_quality_report(catalog, enriched):
    """Analyze song catalog quality without modifying source data."""

    catalog_df = pd.DataFrame(catalog)

    if catalog_df.empty:
        raise ValueError("Song catalog is empty")

    required_columns = {
        "musicbrainz_id",
        "title",
        "artists",
    }

    missing_columns = required_columns - set(catalog_df.columns)

    if missing_columns:
        raise ValueError(
            f"Catalog missing required columns: {sorted(missing_columns)}"
        )

    # Count duplicate IDs before attempting the join.
    duplicate_ids = int(
        catalog_df["musicbrainz_id"].duplicated().sum()
    )

    enrichment_rows = []

    for song in enriched:
        metadata = song.get("enrichment") or {}

        enrichment_rows.append({
            "musicbrainz_id": song["musicbrainz_id"],
            "genre": metadata.get("genre"),
            "classification_source": metadata.get(
                "classification_source"
            ),
        })

    enrichment_df = pd.DataFrame(
        enrichment_rows,
        columns=[
            "musicbrainz_id",
            "genre",
            "classification_source",
        ],
    )

    # Preserve every recording from the master catalog.
    # Reject duplicate IDs to prevent incorrect join results.
    merged_df = catalog_df.merge(
        enrichment_df,
        on="musicbrainz_id",
        how="left",
        validate="one_to_one",
    )

    total = len(merged_df)

    classified_mask = (
        merged_df["classification_source"]
        .eq("gemini_suggestion")
        .fillna(False)
    )

    classified = int(classified_mask.sum())

    missing_titles = int(
        merged_df["title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    missing_artists = int(
        merged_df["artists"]
        .apply(
            lambda artists: (
                not isinstance(artists, list)
                or not any(
                    isinstance(artist, str) and artist.strip()
                    for artist in artists
                )
            )
        )
        .sum()
    )

    coverage = float(
        np.round(
            (classified / total) * 100,
            2,
        )
    )

    genre_distribution = (
        merged_df.loc[classified_mask, "genre"]
        .fillna("unknown")
        .value_counts()
        .to_dict()
    )

    return {
        "total_recordings": total,
        "classified_recordings": classified,
        "unclassified_recordings": total - classified,
        "enrichment_coverage_percent": coverage,
        "missing_titles": missing_titles,
        "missing_artists": missing_artists,
        "duplicate_musicbrainz_ids": duplicate_ids,
        "genre_distribution": genre_distribution,
    }


def main():
    catalog = load_json(CATALOG_FILE)
    enriched = load_json(ENRICHED_FILE)

    report = build_quality_report(catalog, enriched)

    print("\n========== HINDI SONG DATA QUALITY ==========")

    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

