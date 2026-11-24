# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import pandas as pd

from backend.discovery_validation_report import (
    normalize_title,
    validate_discovered_songs,
)


def make_song(
    recording_id,
    title,
    search_term=None,
    category_hint=None,
):
    song = {
        "musicbrainz_id": recording_id,
        "title": title,
        "artists": ["Test Artist"],
        "search_term": search_term or title,
    }

    if category_hint is not None:
        song["discovery_category_hint"] = category_hint

    return song


def test_normalize_title():
    assert normalize_title("  Vande Mataram! ") == "vande mataram"
    assert normalize_title("LAG JA GALE") == "lag ja gale"
    assert normalize_title(None) == ""


def test_matching_discovered_record():
    catalog = [
        make_song(
            "MB001",
            "Vande Mataram",
            "vande mataram",
            "patriotic",
        )
    ]

    report = validate_discovered_songs(catalog)

    assert len(report) == 1
    assert bool(report.iloc[0]["title_match"]) is True


def test_mismatched_title_detected():
    catalog = [
        make_song(
            "MB002",
            "Different Song",
            "Raghupati Raghav Raja Ram",
            "devotional",
        )
    ]

    report = validate_discovered_songs(catalog)

    assert len(report) == 1
    assert bool(report.iloc[0]["title_match"]) is False


def test_original_catalog_records_excluded():
    catalog = [
        make_song("MB001", "Lag Ja Gale"),
        make_song(
            "MB002",
            "Tara Vina Shyam",
            category_hint="garba",
        ),
    ]

    report = validate_discovered_songs(catalog)

    assert len(report) == 1
    assert report.iloc[0]["musicbrainz_id"] == "MB002"


def test_no_discovery_records():
    catalog = [
        make_song("MB001", "Lag Ja Gale"),
    ]

    report = validate_discovered_songs(catalog)

    assert isinstance(report, pd.DataFrame)
    assert report.empty


def test_empty_catalog():
    report = validate_discovered_songs([])

    assert report.empty
    assert "title_match" in report.columns

