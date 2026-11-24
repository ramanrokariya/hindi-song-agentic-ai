# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


def calculate_batch_metrics(summary, duration_seconds):
    """Calculate operational metrics for one enrichment batch."""

    if duration_seconds < 0:
        raise ValueError("duration_seconds cannot be negative")

    attempts = summary["attempts"]
    succeeded = summary["succeeded"]
    failed = summary["failed"]

    if attempts < 0 or succeeded < 0 or failed < 0:
        raise ValueError("Batch counts cannot be negative")

    if succeeded + failed != attempts:
        raise ValueError(
            "Succeeded plus failed must equal attempts"
        )

    success_rate = (
        round((succeeded / attempts) * 100, 2)
        if attempts else 0.0
    )

    failure_rate = (
        round((failed / attempts) * 100, 2)
        if attempts else 0.0
    )

    throughput_per_minute = (
        round((attempts / duration_seconds) * 60, 2)
        if duration_seconds > 0 else 0.0
    )

    return {
        "attempts": attempts,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": summary.get("skipped", 0),
        "retry_blocked": summary.get("retry_blocked", 0),
        "success_rate_percent": success_rate,
        "failure_rate_percent": failure_rate,
        "duration_seconds": round(duration_seconds, 2),
        "throughput_per_minute": throughput_per_minute,
    }

