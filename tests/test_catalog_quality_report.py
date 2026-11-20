
import pytest
from pandas.errors import MergeError

from backend.catalog_quality_report import build_quality_report


def make_song(recording_id, title="Test Song", artists=None):
    return {
        "musicbrainz_id": recording_id,
        "title": title,
        "artists": ["Test Artist"] if artists is None else artists,
    }


def make_enriched(song, genre="romantic"):
    return {
        **song,
        "enrichment": {
            "genre": genre,
            "classification_source": "gemini_suggestion",
        },
    }


def test_enrichment_coverage():
    catalog = [
        make_song("MB001"),
        make_song("MB002"),
        make_song("MB003"),
    ]

    enriched = [
        make_enriched(catalog[0]),
        make_enriched(catalog[1]),
    ]

    report = build_quality_report(catalog, enriched)

    assert report["total_recordings"] == 3
    assert report["classified_recordings"] == 2
    assert report["unclassified_recordings"] == 1
    assert report["enrichment_coverage_percent"] == 66.67


def test_missing_title_and_artist():
    catalog = [
        make_song("MB001", title=" ", artists=[]),
        make_song("MB002"),
    ]

    report = build_quality_report(catalog, [])

    assert report["missing_titles"] == 1
    assert report["missing_artists"] == 1


def test_genre_distribution():
    catalog = [
        make_song("MB001"),
        make_song("MB002"),
        make_song("MB003"),
    ]

    enriched = [
        make_enriched(catalog[0], "romantic"),
        make_enriched(catalog[1], "devotional"),
        make_enriched(catalog[2], "romantic"),
    ]

    report = build_quality_report(catalog, enriched)

    assert report["genre_distribution"] == {
        "romantic": 2,
        "devotional": 1,
    }


def test_empty_catalog_rejected():
    with pytest.raises(ValueError, match="empty"):
        build_quality_report([], [])


def test_duplicate_recording_ids_rejected():
    catalog = [
        make_song("MB001"),
        make_song("MB001"),
    ]

    with pytest.raises(MergeError):
        build_quality_report(catalog, [])


def test_unclassified_records_not_counted():
    catalog = [make_song("MB001")]

    enriched = [{
        **catalog[0],
        "enrichment": {
            "genre": "romantic",
            "classification_source": "manual_draft",
        },
    }]

    report = build_quality_report(catalog, enriched)

    assert report["classified_recordings"] == 0
    assert report["unclassified_recordings"] == 1
    assert report["genre_distribution"] == {}

