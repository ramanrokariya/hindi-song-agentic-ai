"""Automated FastAPI endpoint and error-handling tests."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.headers.get("X-Request-ID")


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_successful_song_search(client):
    query = "Find Garba songs"

    mock_result = {
        "query": query,
        "intent": {
            "genre": None,
            "mood": None,
            "listening_time": None,
            "occasion": None,
            "subject": None,
            "category": "garba",
            "limit": 5,
            "semantic_query": query,
        },
        "results": [
            {
                "musicbrainz_id": "test-recording-id",
                "title": "Test Garba Song",
                "category": "garba",
                "similarity": 0.85,
                "structured_match": True,
            }
        ],
    }

    with patch(
        "backend.main.run_song_agent",
        return_value=mock_result,
    ) as mock_agent:
        response = client.post(
            "/api/v1/songs/search",
            json={"query": query},
        )

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")

    body = response.json()

    assert body["query"] == query
    assert body["intent"]["category"] == "garba"
    assert len(body["results"]) == 1
    assert body["results"][0]["category"] == "garba"
    assert body["results"][0]["similarity"] == 0.85

    mock_agent.assert_called_once_with(query)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"query": ""},
        {"query": "   "},
        {"query": "a" * 501},
    ],
)
def test_invalid_search_request(client, payload):
    with patch(
        "backend.main.run_song_agent"
    ) as mock_agent:
        response = client.post(
            "/api/v1/songs/search",
            json=payload,
        )

    assert response.status_code == 422
    assert response.headers.get("X-Request-ID")

    mock_agent.assert_not_called()


def test_internal_server_error(client):
    with patch(
        "backend.main.run_song_agent",
        side_effect=RuntimeError(
            "Simulated agent failure"
        ),
    ):
        response = client.post(
            "/api/v1/songs/search",
            json={"query": "Find devotional songs"},
        )

    assert response.status_code == 500

    body = response.json()
    request_id = response.headers.get("X-Request-ID")

    assert body["error"] == "INTERNAL_SERVER_ERROR"
    assert body["message"] == "An internal error occurred."
    assert request_id
    assert request_id != "unknown"
    assert body["request_id"] == request_id
    assert "Simulated agent failure" not in response.text


def test_unique_request_ids(client):
    first_response = client.get("/health")
    second_response = client.get("/health")

    first_id = first_response.headers.get("X-Request-ID")
    second_id = second_response.headers.get("X-Request-ID")

    assert first_id
    assert second_id
    assert first_id != second_id
