
import json
import os

from pydantic import BaseModel, Field
from google import genai
from google.genai import types


MODEL_NAME = "gemini-2.5-flash"


class SongSearchIntent(BaseModel):
    genre: str | None = None
    mood: str | None = None
    listening_time: str | None = None
    occasion: str | None = None
    subject: str | None = None
    limit: int = Field(default=5, ge=1, le=50)
    semantic_query: str


def create_client():
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.getenv(
            "GOOGLE_CLOUD_LOCATION",
            "us-central1",
        ),
    )


def understand_query(user_query):
    if not isinstance(user_query, str) or not user_query.strip():
        raise ValueError("Query must not be empty")

    client = create_client()

    prompt = f"""
You are the query-understanding component of a
Hindi music discovery application.

Extract the user's song-search requirements.

Rules:
- Do not recommend songs.
- Do not invent user preferences.
- Use null for unspecified filters.
- Genre examples: devotional, romantic, folk, patriotic.
- Mood examples: peaceful, sad, happy, energetic.
- Listening time examples: morning, afternoon, evening, night.
- Occasion examples: Janmashtami, Navratri, Independence Day.
- Subject examples: Krishna, Rama, Shiva, Mata Rani.
- Limit defaults to 5, maximum 50.
- semantic_query should preserve the user's musical intent
  as a natural-language sentence.
- Return only information supported by the user's request.

User request:
{user_query}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SongSearchIntent,
            temperature=0,
        ),
    )

    return SongSearchIntent.model_validate_json(
        response.text
    )


def main():
    print("\n========== GEMINI SONG QUERY UNDERSTANDING ==========")
    print("Type 'exit' to quit.")

    while True:
        try:
            query = input("\nAgent Query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            intent = understand_query(query)
            print(
                json.dumps(
                    intent.model_dump(),
                    indent=2,
                    ensure_ascii=False,
                )
            )
        except Exception as exc:
            print("Query understanding failed:", exc)


if __name__ == "__main__":
    main()

