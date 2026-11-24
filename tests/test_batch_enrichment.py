# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from unittest.mock import Mock, patch
from backend.batch_enrichment_service import process_batch


def make_song(recording_id):
    return {
        "musicbrainz_id": recording_id,
        "title": f"Test Song {recording_id}",
        "artists": ["Test Artist"],
    }


def make_classification():
    classification = Mock()
    classification.genre = "romantic"
    classification.model_dump.return_value = {
        "genre": "romantic",
        "mood": ["romantic"],
        "listening_time": ["evening"],
        "occasion": ["relaxation"],
    }
    return classification


def test_batch_stops_after_three_successes(tmp_path):
    """Verify that the batch processes only three new songs."""

    catalog = [make_song(f"id-{i}") for i in range(1, 7)]
    checkpoint = {}

    with (
        patch(
            "backend.batch_enrichment_service.classify_song",
            return_value=make_classification(),
        ) as mock_classify,
        patch("backend.batch_enrichment_service.time.sleep"),
    ):
        summary = process_batch(
            catalog=catalog,
            checkpoint=checkpoint,
            client=Mock(),
            max_attempts=3,
            output_file=tmp_path / "checkpoint.json",
        )

    assert mock_classify.call_count == 3
    assert summary["attempts"] == 3
    assert summary["succeeded"] == 3
    assert summary["failed"] == 0
    assert summary["total_saved"] == 3


def test_batch_stops_even_when_requests_fail(tmp_path):
    """Verify that failures also count toward the attempt limit."""

    catalog = [make_song(f"id-{i}") for i in range(1, 7)]
    checkpoint = {}

    with (
        patch(
            "backend.batch_enrichment_service.classify_song",
            side_effect=[
                RuntimeError("Gemini unavailable"),
                RuntimeError("Gemini timeout"),
                make_classification(),
            ],
        ) as mock_classify,
        patch("backend.batch_enrichment_service.time.sleep"),
    ):
        summary = process_batch(
            catalog=catalog,
            checkpoint=checkpoint,
            client=Mock(),
            max_attempts=3,
            output_file=tmp_path / "checkpoint.json",
        )

    assert mock_classify.call_count == 3
    assert summary["attempts"] == 3
    assert summary["succeeded"] == 1
    assert summary["failed"] == 2
    assert summary["total_saved"] == 1


def test_previously_classified_songs_are_skipped(tmp_path):
    """Verify that previously classified songs are skipped."""

    catalog = [make_song(f"id-{i}") for i in range(1, 7)]

    previously_classified = make_song("id-1")
    previously_classified["enrichment"] = {
        "genre": "romantic",
        "classification_source": "gemini_suggestion",
        "review_status": "pending",
    }

    checkpoint = {"id-1": previously_classified}

    with (
        patch(
            "backend.batch_enrichment_service.classify_song",
            return_value=make_classification(),
        ) as mock_classify,
        patch("backend.batch_enrichment_service.time.sleep"),
    ):
        summary = process_batch(
            catalog=catalog,
            checkpoint=checkpoint,
            client=Mock(),
            max_attempts=3,
            output_file=tmp_path / "checkpoint.json",
        )

    assert mock_classify.call_count == 3
    assert summary["attempts"] == 3
    assert summary["skipped"] == 1
    assert summary["succeeded"] == 3
    assert summary["total_saved"] == 4

