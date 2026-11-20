import os
import sys
import pytest
import requests
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "backend")
)

from musicbrainz_client import MusicBrainzClient


def test_search_songs_success():

    mock_response = Mock()
    mock_response.json.return_value = {
        "recordings": [
            {
                "id": "test-123",
                "title": "Lag Ja Gale"
            }
        ]
    }

    with patch.dict(
        os.environ,
        {"MUSICBRAINZ_CONTACT_EMAIL": "ramanrokariya@gmail.com"}
    ):
        client = MusicBrainzClient()

        with patch.object(
            client.session,
            "get",
            return_value=mock_response
        ) as mock_get:

            songs = client.search_songs(
                "Lag Ja Gale",
                limit=3
            )

    assert len(songs) == 1
    assert songs[0]["title"] == "Lag Ja Gale"
    assert songs[0]["id"] == "test-123"

    mock_response.raise_for_status.assert_called_once()

    mock_get.assert_called_once()


def test_search_songs_http_503():

    mock_response = Mock()
    mock_response.status_code = 503
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(
            "503 Service Temporarily Unavailable",
            response=mock_response
        )
    )

    with patch.dict(
        os.environ,
        {"MUSICBRAINZ_CONTACT_EMAIL": "ramanrokariya@gmail.com"}
    ):
        client = MusicBrainzClient()

        with patch.object(
            client.session,
            "get",
            return_value=mock_response
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                client.search_songs("Lag Ja Gale")



def test_missing_contact_email():

    with patch.dict(os.environ, {}, clear=True):

        with pytest.raises(
            ValueError,
            match="Set MUSICBRAINZ_CONTACT_EMAIL"
        ):
            MusicBrainzClient()
