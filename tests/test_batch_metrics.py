
import pytest

from backend.batch_metrics import calculate_batch_metrics


def make_summary(
    attempts=3,
    succeeded=3,
    failed=0,
    skipped=9,
    retry_blocked=0,
):
    return {
        "attempts": attempts,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "retry_blocked": retry_blocked,
    }


def test_all_successful_batch():
    summary = make_summary()

    metrics = calculate_batch_metrics(
        summary,
        duration_seconds=30,
    )

    assert metrics["attempts"] == 3
    assert metrics["success_rate_percent"] == 100.0
    assert metrics["failure_rate_percent"] == 0.0
    assert metrics["throughput_per_minute"] == 6.0
    assert metrics["skipped"] == 9


def test_mixed_success_and_failure():
    summary = make_summary(
        attempts=3,
        succeeded=2,
        failed=1,
        retry_blocked=1,
    )

    metrics = calculate_batch_metrics(
        summary,
        duration_seconds=30,
    )

    assert metrics["success_rate_percent"] == 66.67
    assert metrics["failure_rate_percent"] == 33.33
    assert metrics["retry_blocked"] == 1
    assert metrics["throughput_per_minute"] == 6.0


def test_empty_batch():
    summary = make_summary(
        attempts=0,
        succeeded=0,
        failed=0,
    )

    metrics = calculate_batch_metrics(
        summary,
        duration_seconds=10,
    )

    assert metrics["success_rate_percent"] == 0.0
    assert metrics["failure_rate_percent"] == 0.0
    assert metrics["throughput_per_minute"] == 0.0


def test_zero_duration():
    summary = make_summary()

    metrics = calculate_batch_metrics(
        summary,
        duration_seconds=0,
    )

    assert metrics["duration_seconds"] == 0
    assert metrics["throughput_per_minute"] == 0.0


def test_invalid_attempt_counts():
    summary = make_summary(
        attempts=3,
        succeeded=2,
        failed=2,
    )

    with pytest.raises(ValueError):
        calculate_batch_metrics(
            summary,
            duration_seconds=30,
        )


def test_negative_duration_rejected():
    summary = make_summary()

    with pytest.raises(ValueError):
        calculate_batch_metrics(
            summary,
            duration_seconds=-5,
        )

