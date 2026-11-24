# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SongSearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=500,
        description="Natural-language Hindi song search request",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be blank")
        return value


class SongSearchIntent(BaseModel):
    genre: Optional[str] = None
    mood: Optional[str] = None
    listening_time: Optional[str] = None
    occasion: Optional[str] = None
    subject: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(ge=1, le=50)
    semantic_query: str


class SongResult(BaseModel):
    musicbrainz_id: str
    title: str
    similarity: float = Field(ge=-1, le=1)
    structured_match: bool
    category: Optional[str] = None


class SongSearchResponse(BaseModel):
    query: str
    intent: SongSearchIntent
    results: list[SongResult]

