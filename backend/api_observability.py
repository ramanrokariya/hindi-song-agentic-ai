
import json
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        for field in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
        ):
            if hasattr(record, field):
                payload[field] = getattr(record, field)

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(payload)


def configure_logging():
    logger = logging.getLogger("hindi_song_api")

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger


logger = configure_logging()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            # The centralized exception handler logs failures.
            raise

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "HTTP request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response

