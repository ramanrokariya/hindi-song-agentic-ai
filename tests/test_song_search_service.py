
import json

import pytest
from pandas.errors import MergeError

from backend.song_search_service import (
    contains_value,
    matches_mood,
    build_search_dataframe,
    search_songs,
)


def create_test_files(tmp_path):
    catalog = [
        {
            "musicbrainz_id": "MB001",
            "title": "Raghupati Raghav Raja Ram",
            "artists": ["Singer A"],
            "discovery_category_hint": "devotional",
        },
        {
            "musicbrainz_id": "MB002",
            "title": "Tara Vina Shyam",
            "artists": ["Singer B"],
            "discovery_category_hint": "garba",
        },
        {
            "musicbrainz_id": "MB003",
            "title": "Vande Mataram",
            "artists": ["Singer C"],
            "discovery_category_hint": "patriotic",
        },
    ]

    enriched = [
        {
            "musicbrainz_id": "MB001",
            "enrichment": {
                "genre": "devotional",
                "mood": ["peaceful"],
                "listening_time": ["morning"],
                "occasion": ["prayer"],
            },
        },
        {
            "musicbrainz_id": "MB002",
            "enrichment": {
                "genre": "folk",
                "mood": ["energetic"],
                "listening_time": ["evening"],
                "occasion": ["Navratri"],
            },
        },
        {
            "musicbrainz_id": "MB003",
            "enrichment": {
                "genre": "patriotic",
                "mood": ["inspiring"],
                "listening_time": ["morning"],
                "occasion": ["Independence Day"],
            },
        },
    ]

    catalog_file = tmp_path / "catalog.json"
    enriched_file = tmp_path / "enriched.json"

    catalog_file.write_text(
        json.dumps(catalog), encoding="utf-8"
    )
    enriched_file.write_text(
        json.dumps(enriched), encoding="utf-8"
    )

    return catalog_file, enriched_file


def run_search(tmp_path, **filters):
    catalog_file, enriched_file = create_test_files(tmp_path)

    return search_songs(
        catalog_file=catalog_file,
        enriched_file=enriched_file,
        **filters,
    )


def test_contains_value_case_insensitive():
    assert contains_value("Devotional", "devotional")
    assert contains_value(["Morning", "Evening"], "morning")
    assert not contains_value(["Morning"], "night")


def test_search_by_genre(tmp_path):
    results = run_search(tmp_path, genre="devotional")

    assert len(results) == 1
    assert results[0]["musicbrainz_id"] == "MB001"


def test_search_by_category(tmp_path):
    results = run_search(tmp_path, category="garba")

    assert len(results) == 1
    assert results[0]["musicbrainz_id"] == "MB002"


def test_search_by_mood(tmp_path):
    results = run_search(tmp_path, mood="energetic")

    assert len(results) == 1
    assert results[0]["musicbrainz_id"] == "MB002"


def test_search_by_listening_time(tmp_path):
    results = run_search(tmp_path, listening_time="morning")

    assert len(results) == 2


def test_search_by_occasion(tmp_path):
    results = run_search(
        tmp_path, occasion="Independence Day"
    )

    assert len(results) == 1
    assert results[0]["musicbrainz_id"] == "MB003"


def test_combined_filters(tmp_path):
    results = run_search(
        tmp_path,
        genre="folk",
        category="garba",
        occasion="Navratri",
    )

    assert len(results) == 1
    assert results[0]["musicbrainz_id"] == "MB002"


def test_no_matching_songs(tmp_path):
    results = run_search(tmp_path, genre="classical")

    assert results == []


def test_result_limit(tmp_path):
    results = run_search(
        tmp_path, listening_time="morning", limit=1
    )

    assert len(results) == 1


def test_invalid_limit(tmp_path):
    with pytest.raises(ValueError):
        run_search(tmp_path, limit=0)


def test_dataframe_join(tmp_path):
    catalog_file, enriched_file = create_test_files(tmp_path)

    df = build_search_dataframe(
        catalog_file, enriched_file
    )

    assert len(df) == 3
    assert "enrichment" in df.columns


def test_duplicate_enrichment_ids_rejected(tmp_path):
    catalog_file, enriched_file = create_test_files(tmp_path)

    enriched = json.loads(
        enriched_file.read_text(encoding="utf-8")
    )

    enriched.append(enriched[0])

    enriched_file.write_text(
        json.dumps(enriched), encoding="utf-8"
    )

    with pytest.raises(MergeError):
        build_search_dataframe(
            catalog_file, enriched_file
        )


def test_sad_mood_synonyms():
    assert matches_mood(["melancholic"], "sad")
    assert matches_mood(["melancholy"], "sad")
    assert matches_mood(["heartbroken"], "sad")


def test_sad_mood_excludes_broad_emotions():
    assert not matches_mood(["nostalgic"], "sad")
    assert not matches_mood(["emotional"], "sad")
    assert not matches_mood(["soulful"], "sad")


def test_mood_case_insensitive():
    assert matches_mood(["Melancholic"], "SAD")
    assert matches_mood(["JOYFUL"], "happy")


def test_missing_mood():
    assert not matches_mood(None, "sad")
    assert not matches_mood([], "sad")
    assert matches_mood(None, None)



