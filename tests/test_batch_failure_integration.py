
from unittest.mock import Mock, patch

from backend.batch_enrichment_service import process_batch
from backend.failure_tracker import load_failures


def make_song():
    return {
        "musicbrainz_id": "recording-001",
        "title": "Lag Ja Gale",
        "artists": ["Test Artist"],
    }


def make_classification():
    result = Mock()
    result.genre = "romantic"
    result.model_dump.return_value = {
        "genre": "romantic",
        "mood": ["nostalgic"],
        "listening_time": ["evening"],
        "occasion": ["relaxation"],
    }
    return result


def test_failure_persisted_then_cleared_after_success(tmp_path):
    """A failed recording should recover in a later batch."""

    catalog = [make_song()]
    checkpoint = {}

    failure_file = tmp_path / "failures.json"
    output_file = tmp_path / "checkpoint.json"

    # Batch 1: Simulate Gemini failure.
    failures = load_failures(failure_file)

    with (
        patch(
            "backend.batch_enrichment_service.classify_song",
            side_effect=RuntimeError("Gemini timeout"),
        ) as mock_classify,
        patch("backend.batch_enrichment_service.time.sleep"),
    ):
        first_summary = process_batch(
            catalog=catalog,
            checkpoint=checkpoint,
            client=Mock(),
            max_attempts=1,
            output_file=output_file,
            failures=failures,
            failure_file=failure_file,
        )

    assert mock_classify.call_count == 1
    assert first_summary["attempts"] == 1
    assert first_summary["failed"] == 1
    assert first_summary["succeeded"] == 0

    # Verify failure persisted to disk.
    saved_failures = load_failures(failure_file)

    assert saved_failures["recording-001"]["attempt_count"] == 1
    assert saved_failures["recording-001"]["last_error"] == (
        "Gemini timeout"
    )

    # Batch 2: Simulate application restart and recovery.
    failures = load_failures(failure_file)
    
    # Simulate that the cooldown period has elapsed.
    failures["recording-001"]["last_attempt_at"] = (
        "2020-01-01T00:00:00+00:00"
    )

    with (
        patch(
            "backend.batch_enrichment_service.classify_song",
            return_value=make_classification(),
        ) as mock_classify,
        patch("backend.batch_enrichment_service.time.sleep"),
    ):
        second_summary = process_batch(
            catalog=catalog,
            checkpoint=checkpoint,
            client=Mock(),
            max_attempts=1,
            output_file=output_file,
            failures=failures,
            failure_file=failure_file,
        )

    assert mock_classify.call_count == 1
    assert second_summary["succeeded"] == 1
    assert second_summary["failed"] == 0

    # Verify successful checkpoint and cleared failure.
    assert output_file.exists()
    assert checkpoint["recording-001"]["enrichment"]["genre"] == (
        "romantic"
    )
    assert load_failures(failure_file) == {}

