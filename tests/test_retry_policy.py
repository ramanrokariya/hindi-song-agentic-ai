# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from datetime import datetime, timezone

import pytest

from backend.retry_policy import evaluate_retry


NOW = datetime(
    2026, 10, 19, 15, 0, 0,
    tzinfo=timezone.utc,
)


def make_failure(attempt_count, last_attempt_at):
    return {
        "musicbrainz_id": "test-recording-001",
        "attempt_count": attempt_count,
        "last_attempt_at": last_attempt_at,
    }


def test_new_recording_is_allowed():
    allowed, reason = evaluate_retry(
        failure_record=None,
        now=NOW,
    )

    assert allowed is True
    assert reason == "new_recording"


def test_retry_blocked_during_cooldown():
    failure = make_failure(
        attempt_count=1,
        last_attempt_at="2026-10-19T14:50:00+00:00",
    )

    allowed, reason = evaluate_retry(
        failure,
        now=NOW,
    )

    assert allowed is False
    assert reason == "cooldown_active"


def test_retry_allowed_after_cooldown():
    failure = make_failure(
        attempt_count=1,
        last_attempt_at="2026-10-19T14:40:00+00:00",
    )

    allowed, reason = evaluate_retry(
        failure,
        now=NOW,
    )

    assert allowed is True
    assert reason == "retry_allowed"


def test_retry_allowed_exactly_at_cooldown_boundary():
    failure = make_failure(
        attempt_count=2,
        last_attempt_at="2026-10-19T14:45:00+00:00",
    )

    allowed, reason = evaluate_retry(
        failure,
        now=NOW,
    )

    assert allowed is True
    assert reason == "retry_allowed"


def test_retry_blocked_after_max_failures():
    failure = make_failure(
        attempt_count=3,
        last_attempt_at="2026-10-19T12:00:00+00:00",
    )

    allowed, reason = evaluate_retry(
        failure,
        now=NOW,
    )

    assert allowed is False
    assert reason == "max_failures_reached"


def test_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        evaluate_retry(
            None,
            max_failures=0,
            now=NOW,
        )

    with pytest.raises(ValueError):
        evaluate_retry(
            None,
            cooldown_minutes=-1,
            now=NOW,
        )


def test_timestamp_without_timezone_is_rejected():
    failure = make_failure(
        attempt_count=1,
        last_attempt_at="2026-10-19T14:40:00",
    )

    with pytest.raises(ValueError):
        evaluate_retry(
            failure,
            now=NOW,
        )

