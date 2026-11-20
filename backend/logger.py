import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }

        if hasattr(record, "event"):
            log_entry["event"] = record.event

        if hasattr(record, "song_title"):
            log_entry["song_title"] = record.song_title

        if record.exc_info:
            log_entry["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(log_entry, ensure_ascii=False)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    logger.propagate = False
    return logger
