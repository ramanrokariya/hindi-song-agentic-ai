# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json
from datetime import datetime, timezone
from pathlib import Path


def load_failures(file_path):
    """Load saved failure records, indexed by MusicBrainz ID."""

    path = Path(file_path)

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "Failure tracking file must contain a JSON list"
        )

    return {
        record["musicbrainz_id"]: record
        for record in records
    }


def save_failures(file_path, failures):
    """Persist failure records using atomic replacement."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(
            list(failures.values()),
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_path.replace(path)


def record_failure(failures, song, error):
    """Record a failure or increment an existing failure count."""

    recording_id = song["musicbrainz_id"]
    previous = failures.get(recording_id, {})

    failure_record = {
        "musicbrainz_id": recording_id,
        "title": song["title"],
        "attempt_count": previous.get("attempt_count", 0) + 1,
        "last_error": str(error),
        "last_attempt_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    failures[recording_id] = failure_record

    return failure_record


def clear_failure(failures, recording_id):
    """Remove a resolved failure record."""

    return failures.pop(recording_id, None)

