# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import re
import unicodedata

import pandas as pd

from backend.catalog_quality_report import CATALOG_FILE
from backend.incremental_enrichment_service import load_json


def normalize_title(value):
    """Normalize a title for basic comparison."""
    if not isinstance(value, str):
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = value.casefold()

    return re.sub(r"[^\w]+", " ", value).strip()


def validate_discovered_songs(catalog):
    """Review newly discovered records without modifying them."""

    df = pd.DataFrame(catalog)

    required = [
        "musicbrainz_id",
        "title",
        "artists",
        "search_term",
        "discovery_category_hint",
    ]

    # Older catalog records don't have discovery hints.
    # Only examine records added by expanded ingestion.
    if "discovery_category_hint" not in df.columns:
        return pd.DataFrame(columns=required + ["title_match"])

    discovered = df.loc[
        df["discovery_category_hint"].notna()
    ].copy()

    if discovered.empty:
        return pd.DataFrame(columns=required + ["title_match"])

    discovered["title_match"] = (
        discovered["title"].map(normalize_title)
        == discovered["search_term"].map(normalize_title)
    )

    return discovered[
        required + ["title_match"]
    ].reset_index(drop=True)


def main():
    catalog = load_json(CATALOG_FILE)
    reviewed = validate_discovered_songs(catalog)

    print("\n========== DISCOVERY VALIDATION ==========")
    print("Newly discovered:", len(reviewed))

    if reviewed.empty:
        print("No discovered recordings to review.")
        return

    counts = (
        reviewed["discovery_category_hint"]
        .value_counts()
        .sort_index()
    )

    print("\nDiscovery category distribution:")
    print(counts.to_string())

    matches = int(reviewed["title_match"].sum())
    mismatches = len(reviewed) - matches

    print("\nExact normalized title matches:", matches)
    print("Title mismatches for review:", mismatches)

    if mismatches:
        print("\nRecords requiring title review:")
        columns = [
            "musicbrainz_id",
            "title",
            "search_term",
        ]

        print(
            reviewed.loc[
                ~reviewed["title_match"],
                columns,
            ].to_string(index=False)
        )

    print("\nNo catalog records were modified.")


if __name__ == "__main__":
    main()

