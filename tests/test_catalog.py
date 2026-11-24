# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import json
from pathlib import Path


CATALOG_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "hindi_songs_catalog.json"
)


def test_catalog_is_not_empty():
    with CATALOG_FILE.open(encoding="utf-8") as file:
        catalog = json.load(file)

    assert len(catalog) > 0


def test_musicbrainz_ids_are_unique():
    with CATALOG_FILE.open(encoding="utf-8") as file:
        catalog = json.load(file)

    ids = [
        song["musicbrainz_id"]
        for song in catalog
    ]

    assert len(ids) == len(set(ids))


def test_every_recording_has_title():
    with CATALOG_FILE.open(encoding="utf-8") as file:
        catalog = json.load(file)

    for song in catalog:
        assert song.get("title")
