# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend.agent_query_understanding import SongSearchIntent
from backend.song_search_agent import run_song_agent
from backend.api_models import SongSearchResponse


@pytest.mark.parametrize(
    "category",
    [
        "garba",
        "krishna_bhajan",
        "devotional",
        "folk",
        "patriotic",
    ],
)
def test_valid_category(category):
    intent = SongSearchIntent(
        semantic_query="Find songs",
        category=category,
    )

    assert intent.category == category


def test_invalid_category():
    with pytest.raises(ValidationError):
        SongSearchIntent(
            semantic_query="Find songs",
            category="unsupported_category",
        )


def test_missing_category():
    intent = SongSearchIntent(
        semantic_query="Find romantic songs",
        genre="romantic",
    )

    assert intent.category is None
    assert intent.genre == "romantic"


@pytest.mark.parametrize(
    "category, genre",
    [
        ("garba", None),
        ("krishna_bhajan", None),
        ("garba", "folk"),
        (None, "romantic"),
    ],
)
def test_agent_category_propagation(category, genre):

    intent = SongSearchIntent(
        semantic_query="Find matching songs",
        category=category,
        genre=genre,
        limit=5,
    )

    with patch(
        "backend.song_search_agent.understand_query",
        return_value=intent,
    ), patch(
        "backend.song_search_agent.hybrid_search",
        return_value=[],
    ) as mock_search:

        response = run_song_agent(
            "Find matching songs"
        )

    mock_search.assert_called_once_with(
        query="Find matching songs",
        genre=genre,
        mood=None,
        listening_time=None,
        occasion=None,
        category=category,
        limit=5,
    )

    assert response["intent"]["category"] == category
    assert response["results"] == []


@pytest.mark.parametrize(
    "category",
    ["garba", "krishna_bhajan", None],
)
def test_api_category_serialization(category):

    intent = SongSearchIntent(
        semantic_query="Find matching songs",
        category=category,
    )

    response = SongSearchResponse(
        query="Find matching songs",
        intent=intent.model_dump(),
        results=[
            {
                "musicbrainz_id": "test-recording-001",
                "title": "Test Song",
                "similarity": 0.75,
                "structured_match": True,
                "category": category,
            }
        ],
    )

    payload = response.model_dump()

    assert payload["intent"]["category"] == category
    assert payload["results"][0]["category"] == category
