# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from backend.incremental_enrichment_service import (
    build_checkpoint,
    is_classified,
)


def make_song(recording_id, classified=False):
    """Create a sample MusicBrainz recording."""

    song = {
        "musicbrainz_id": recording_id,
        "title": "Test Hindi Song",
        "artists": ["Test Artist"],
    }

    if classified:
        song["enrichment"] = {
            "genre": "romantic",
            "classification_source": "gemini_suggestion",
            "review_status": "pending",
        }

    return song


def test_classified_record_detection():
    """Check successful and unclassified records."""

    classified = make_song("id-101", classified=True)
    unclassified = make_song("id-102")

    assert is_classified(classified) is True
    assert is_classified(unclassified) is False


def test_checkpoint_merges_unique_ids():
    """Duplicate IDs must not create duplicate records."""

    catalog = [
        make_song("id-101"),
        make_song("id-102"),
    ]

    samples = [
        make_song("id-101", classified=True),
    ]

    existing = [
        make_song("id-101", classified=True),
        make_song("id-102", classified=True),
    ]

    checkpoint = build_checkpoint(
        catalog,
        samples,
        existing
    )

    assert len(checkpoint) == 2
    assert set(checkpoint.keys()) == {"id-101", "id-102"}


def test_successful_classification_takes_priority():
    """A successful classification replaces an unclassified one."""

    catalog = [make_song("id-101")]

    samples = [make_song("id-101")]

    existing = [
        make_song("id-101", classified=True)
    ]

    checkpoint = build_checkpoint(
        catalog,
        samples,
        existing
    )

    assert is_classified(checkpoint["id-101"]) is True


def test_unknown_recording_is_excluded():
    """Exclude recordings not present in the source catalog."""

    catalog = [make_song("id-101")]

    samples = [
        make_song("id-101", classified=True),
        make_song("id-999", classified=True),
    ]

    checkpoint = build_checkpoint(
        catalog,
        samples,
        []
    )

    assert len(checkpoint) == 1
    assert "id-999" not in checkpoint


def test_unclassified_record_remains_retryable():
    """Failed or unclassified records should not be skipped."""

    song = make_song("id-101")

    song["enrichment"] = {
        "genre": "unknown",
        "classification_source": "unclassified",
        "review_status": "pending",
    }

    assert is_classified(song) is False

