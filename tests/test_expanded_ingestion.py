
import json
from unittest.mock import Mock

from backend.expanded_ingestion_service import (
    expand_catalog,
    normalize_musicbrainz_record,
)


def make_catalog_song(recording_id, title="Test Song"):
    """Our application's internal song format."""
    return {
        "musicbrainz_id": recording_id,
        "title": title,
        "artists": ["Test Artist"],
        "search_term": title,
    }


def make_raw_record(recording_id, title="Test Song"):
    """Raw MusicBrainz API response format."""
    return {
        "id": recording_id,
        "title": title,
        "artist-credit": [
            {
                "artist": {
                    "name": "Test Artist",
                }
            }
        ],
    }


def make_seed(title="Test Song", category="devotional"):
    return {
        "title": title,
        "category_hint": category,
    }


def write_catalog(path, songs):
    path.write_text(
        json.dumps(songs),
        encoding="utf-8",
    )


def read_catalog(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_normalize_raw_musicbrainz_record():
    raw = make_raw_record("MB001", "Raghupati Raghav")

    normalized = normalize_musicbrainz_record(
        raw,
        search_term="Raghupati Raghav",
        category_hint="devotional",
    )

    assert normalized["musicbrainz_id"] == "MB001"
    assert normalized["title"] == "Raghupati Raghav"
    assert normalized["artists"] == ["Test Artist"]
    assert normalized["discovery_category_hint"] == "devotional"


def test_existing_catalog_preserved(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    existing = make_catalog_song("MB001", "Existing Song")

    write_catalog(catalog_file, [existing])

    client = Mock()
    client.search_songs.return_value = []

    summary = expand_catalog(
        client=client,
        seeds=[make_seed()],
        catalog_file=catalog_file,
        request_delay=0,
    )

    assert summary["initial_recordings"] == 1
    assert summary["new_recordings"] == 0
    assert read_catalog(catalog_file) == [existing]


def test_new_recording_added(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    write_catalog(catalog_file, [])

    client = Mock()
    client.search_songs.return_value = [
        make_raw_record("MB002", "Raghupati Raghav")
    ]

    summary = expand_catalog(
        client=client,
        seeds=[make_seed("Raghupati Raghav")],
        catalog_file=catalog_file,
        request_delay=0,
    )

    saved = read_catalog(catalog_file)

    assert summary["new_recordings"] == 1
    assert summary["total_recordings"] == 1
    assert saved[0]["musicbrainz_id"] == "MB002"
    assert saved[0]["artists"] == ["Test Artist"]
    assert saved[0]["discovery_category_hint"] == "devotional"


def test_duplicate_recording_not_added(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    existing = make_catalog_song("MB001")

    write_catalog(catalog_file, [existing])

    client = Mock()
    client.search_songs.return_value = [
        make_raw_record("MB001"),
        make_raw_record("MB002"),
    ]

    summary = expand_catalog(
        client=client,
        seeds=[make_seed()],
        catalog_file=catalog_file,
        request_delay=0,
    )

    saved = read_catalog(catalog_file)

    assert summary["duplicate_results"] == 1
    assert summary["new_recordings"] == 1
    assert len(saved) == 2


def test_failed_search_continues(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    write_catalog(catalog_file, [])

    client = Mock()
    client.search_songs.side_effect = [
        RuntimeError("MusicBrainz unavailable"),
        [make_raw_record("MB003", "Vande Mataram")],
    ]

    seeds = [
        make_seed("First Song"),
        make_seed("Vande Mataram", "patriotic"),
    ]

    summary = expand_catalog(
        client=client,
        seeds=seeds,
        catalog_file=catalog_file,
        request_delay=0,
    )

    assert summary["failed_searches"] == 1
    assert summary["completed_searches"] == 1
    assert summary["new_recordings"] == 1
    assert read_catalog(catalog_file)[0]["title"] == "Vande Mataram"


def test_rerun_is_idempotent(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    write_catalog(catalog_file, [])

    client = Mock()
    client.search_songs.return_value = [
        make_raw_record("MB004", "Achyutam Keshavam")
    ]

    seeds = [make_seed("Achyutam Keshavam")]

    first = expand_catalog(
        client=client,
        seeds=seeds,
        catalog_file=catalog_file,
        request_delay=0,
    )

    second = expand_catalog(
        client=client,
        seeds=seeds,
        catalog_file=catalog_file,
        request_delay=0,
    )

    assert first["new_recordings"] == 1
    assert second["new_recordings"] == 0
    assert second["duplicate_results"] == 1
    assert len(read_catalog(catalog_file)) == 1


def test_invalid_record_skipped(tmp_path):
    catalog_file = tmp_path / "catalog.json"
    write_catalog(catalog_file, [])

    client = Mock()
    client.search_songs.return_value = [
        {"title": "Missing ID"},
        make_raw_record("MB005", "Valid Song"),
    ]

    summary = expand_catalog(
        client=client,
        seeds=[make_seed()],
        catalog_file=catalog_file,
        request_delay=0,
    )

    assert summary["invalid_records"] == 1
    assert summary["new_recordings"] == 1
    assert summary["total_recordings"] == 1

