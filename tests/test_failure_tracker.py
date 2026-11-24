# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from backend.failure_tracker import (
    load_failures,
    save_failures,
    record_failure,
    clear_failure,
)


def make_song():
    return {
        "musicbrainz_id": "test-recording-001",
        "title": "Lag Ja Gale",
        "artists": ["Test Artist"],
    }


def test_load_missing_file_returns_empty_dict(tmp_path):
    failure_file = tmp_path / "failures.json"

    failures = load_failures(failure_file)

    assert failures == {}


def test_record_first_failure():
    failures = {}
    song = make_song()

    record = record_failure(
        failures,
        song,
        RuntimeError("Gemini timeout"),
    )

    assert record["musicbrainz_id"] == "test-recording-001"
    assert record["title"] == "Lag Ja Gale"
    assert record["attempt_count"] == 1
    assert record["last_error"] == "Gemini timeout"
    assert "last_attempt_at" in record

    assert "test-recording-001" in failures


def test_failure_count_survives_restart(tmp_path):
    failure_file = tmp_path / "failures.json"
    song = make_song()

    # Simulate first application execution.
    failures = {}
    record_failure(
        failures,
        song,
        RuntimeError("Gemini timeout"),
    )
    save_failures(failure_file, failures)

    # Simulate restarting the application.
    failures_after_restart = load_failures(failure_file)

    assert (
        failures_after_restart["test-recording-001"]["attempt_count"]
        == 1
    )

    # The same recording fails again.
    record_failure(
        failures_after_restart,
        song,
        RuntimeError("Gemini unavailable"),
    )
    save_failures(failure_file, failures_after_restart)

    # Verify persistence across another restart.
    final_failures = load_failures(failure_file)

    record = final_failures["test-recording-001"]

    assert record["attempt_count"] == 2
    assert record["last_error"] == "Gemini unavailable"


def test_clear_failure_after_success(tmp_path):
    failure_file = tmp_path / "failures.json"
    song = make_song()

    failures = {}

    record_failure(
        failures,
        song,
        RuntimeError("Temporary API error"),
    )

    save_failures(failure_file, failures)

    # Simulate successful classification.
    clear_failure(
        failures,
        "test-recording-001",
    )

    save_failures(failure_file, failures)

    reloaded_failures = load_failures(failure_file)

    assert reloaded_failures == {}

