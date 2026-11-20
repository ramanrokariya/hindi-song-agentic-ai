
from datetime import datetime, timedelta, timezone


MAX_FAILURES = 3
COOLDOWN_MINUTES = 15


def evaluate_retry(
    failure_record,
    max_failures=MAX_FAILURES,
    cooldown_minutes=COOLDOWN_MINUTES,
    now=None,
):
    """
    Decide whether a recording can be retried in a future batch.

    Returns:
        (allowed: bool, reason: str)
    """

    if max_failures < 1:
        raise ValueError("max_failures must be at least 1")

    if cooldown_minutes < 0:
        raise ValueError("cooldown_minutes cannot be negative")

    if failure_record is None:
        return True, "new_recording"

    attempt_count = failure_record["attempt_count"]

    if attempt_count >= max_failures:
        return False, "max_failures_reached"

    last_attempt_at = datetime.fromisoformat(
        failure_record["last_attempt_at"]
    )

    if last_attempt_at.tzinfo is None:
        raise ValueError("last_attempt_at must include a timezone")

    current_time = now or datetime.now(timezone.utc)

    if current_time.tzinfo is None:
        raise ValueError("now must include a timezone")

    next_retry_at = last_attempt_at + timedelta(
        minutes=cooldown_minutes
    )

    if current_time < next_retry_at:
        return False, "cooldown_active"

    return True, "retry_allowed"

