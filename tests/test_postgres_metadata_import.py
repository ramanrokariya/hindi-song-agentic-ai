# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import json
from unittest.mock import MagicMock

import pytest

from backend import postgres_metadata_import as importer


@pytest.mark.parametrize(
    "category_hint",
    ["garba", "krishna_bhajan", None],
)
def test_category_metadata_mapping(
    tmp_path,
    monkeypatch,
    category_hint,
):
    song = {
        "musicbrainz_id": "test-recording-001",
        "title": "Test Song",
        "artists": ["Test Artist"],
        "enrichment": {
            "genre": "devotional",
            "mood": ["peaceful"],
            "listening_time": ["morning"],
            "occasion": ["prayer"],
            "category": "incorrect_nested_category",
        },
    }

    if category_hint is not None:
        song["discovery_category_hint"] = category_hint

    catalog_file = tmp_path / "test_catalog.json"

    catalog_file.write_text(
        json.dumps([song])
    )

    monkeypatch.setattr(
        importer,
        "CATALOG_FILE",
        catalog_file,
    )

    monkeypatch.setattr(
        importer,
        "load_password",
        lambda: "mock-password",
    )

    mock_connect = MagicMock()

    connection = (
        mock_connect.return_value
        .__enter__.return_value
    )

    cursor = (
        connection.cursor.return_value
        .__enter__.return_value
    )

    cursor.rowcount = 1

    monkeypatch.setattr(
        importer.psycopg,
        "connect",
        mock_connect,
    )

    importer.main()

    cursor.execute.assert_called_once()

    sql, parameters = cursor.execute.call_args.args

    assert "UPDATE song_embeddings" in sql
    assert "category = %s" in sql

    assert parameters == (
        "devotional",
        ["peaceful"],
        ["morning"],
        ["prayer"],
        category_hint,
        ["Test Artist"],
        "test-recording-001",
    )

    connection.commit.assert_called_once()


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (None, None),
        ([], []),
        ("morning", ["morning"]),
        (
            ["morning", "evening"],
            ["morning", "evening"],
        ),
        (
            ["morning", None],
            ["morning"],
        ),
        ([123], ["123"]),
    ],
)
def test_as_text_array(input_value, expected):
    assert importer.as_text_array(input_value) == expected
