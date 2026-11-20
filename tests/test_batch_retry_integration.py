
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from backend.batch_enrichment_service import process_batch


def make_song(recording_id):
    return {
        "musicbrainz_id": recording_id,
        "title": f"Test Song {recording_id}",
        "artists": ["Test Artist"],
    }


def make_failure(recording_id, attempts, timestamp):
    return {
        "musicbrainz_id": recording_id,
        "title": f"Test Song {recording_id}",
        "attempt_count": attempts,
        "last_error": "Gemini timeout",
        "last_attempt_at": timestamp,
    }


def make_classification():
    result = Mock()
    result.genre = "romantic"
    result.model_dump.return_value = {
        "genre": "romantic",
        "mood": ["romantic"],
        "listening_time": ["evening"],
        "occasion": ["relaxation"],
    }
    return result


def test_cooldown_blocks_gemini_call(tmp_path):
    """A recent failure must not trigger Gemini."""

    song = make_song("id-1")
    now = datetime.now(timezone.utc).isoformat()

    failures = {
        "id-1": make_failure("id-1", 1, now)
    }

    with patch(
        "backend.batch_enrichment_service.classify_song"
    ) as mock_classify:
        summary = process_batch(
            catalog=[song],
            checkpoint={},
            client=Mock(),
            max_attempts=3,
            output_file=tmp_path / "checkpoint.json",
            failures=failures,
            failure_file=tmp_path / "failures.json",
        )

    mock_classify.assert_not_called()
    assert summary["attempts"] == 0
    assert summary["retry_blocked"] == 1


def test_max_failures_blocks_gemini_call(tmp_path):
    """Three previous failures must block automatic retry."""

    song = make_song("id-2")

    failures = {
        "id-2": make_failure(
            "id-2",
            3,
            "2020-01-01T00:00:00+00:00",
        )
    }

    with patch(
        "backend.batch_enrichment_service.classify_song"
    ) as mock_classify:
        summary = process_batch(
            catalog=[song],
            checkpoint={},
            client=Mock(),
            max_attempts=3,
            output_file=tmp_path / "checkpoint.json",
            failures=failures,
            failure_file=tmp_path / "failures.json",
        )

    mock_classify.assert_not_called()
    assert summary["attempts"] == 0
    assert summary["retry_blocked"] == 1


def test_blocked_recording_does_not_consume_attempt(tmp_path):
    """An eligible recording should run after a blocked one."""

    blocked_song = make_song("id-blocked")
    eligible_song = make_song("id-eligible")

    failures = {
        "id-blocked": make_failure(
            "id-blocked",
            3,
            "2020-01-01T00:00:00+00:00",
        )
    }

    with (
        patch(
            "backend.batch_enrichment_service.classify_song",
            return_value=make_classification(),
        ) as mock_classify,
        patch("backend.batch_enrichment_service.time.sleep"),
    ):
        summary = process_batch(
            catalog=[blocked_song, eligible_song],
            checkpoint={},
            client=Mock(),
            max_attempts=1,
            output_file=tmp_path / "checkpoint.json",
            failures=failures,
            failure_file=tmp_path / "failures.json",
        )

    mock_classify.assert_called_once()
    assert mock_classify.call_args.args[1]["musicbrainz_id"] == (
        "id-eligible"
    )

    assert summary["attempts"] == 1
    assert summary["succeeded"] == 1
    assert summary["retry_blocked"] == 1
    assert summary["total_saved"] == 1

