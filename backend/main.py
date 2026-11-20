
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.api_models import (
    SongSearchRequest,
    SongSearchResponse,
)
from backend.api_observability import (
    RequestLoggingMiddleware,
    logger,
)
from backend.song_search_agent import run_song_agent


app = FastAPI(
    title="Hindi Song AI Search API",
    description=(
        "AI-powered Hindi song discovery using "
        "Gemini and PostgreSQL pgvector"
    ),
    version="1.0.0",
)

app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(Exception)
async def internal_error_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    logger.error(
        "Internal API error",
        exc_info=(type(exc), exc, exc.__traceback__),
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred.",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.get("/")
def root():
    return {
        "application": "Hindi Song AI Search",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "hindi-song-ai-api",
    }


@app.post(
    "/api/v1/songs/search",
    response_model=SongSearchResponse,
)
def search_songs_api(request: SongSearchRequest):
    return run_song_agent(request.query)

