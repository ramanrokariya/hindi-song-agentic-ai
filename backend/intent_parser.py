import os
import random
import time
from google.genai.errors import ClientError, ServerError

from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class SongSearchIntent(BaseModel):
    category: Literal[
        "devotional", "romantic", "folk", "patriotic", "other"
    ]
    listening_time: Literal[
        "morning", "evening", "night", "any"
    ]
    language: str
    requested_count: int = Field(ge=1, le=20)
    raaga: str | None = None


def parse_intent(user_prompt: str) -> SongSearchIntent:
    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location="global",
        http_options=types.HttpOptions(api_version="v1")
    )


    max_attempts = 4

    for attempt in range(1, max_attempts + 1):

        try:
            print(f"Calling Gemini (attempt {attempt}/{max_attempts})")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    "Extract music search criteria from the user's request. "
                    "Do not recommend songs. "
                    "Use 'any' for unspecified listening time, "
                    "'other' for unspecified category, "
                    "and null for unspecified raaga. "
                    "If the user does not specify a song count, use 5. "
                    "User request: " + user_prompt
                ),
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=SongSearchIntent,
                    max_output_tokens=500
                )
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response")

            intent = SongSearchIntent.model_validate_json(
                response.text
            )

            return intent

        except (ClientError, ServerError) as exc:

            # Retry only temporary API failures
            if exc.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_attempts:
                print("Maximum retry attempts reached.")
                raise

            # Exponential backoff with random jitter
            delay = min(2 ** attempt, 30) + random.uniform(0, 1)

            print(
                f"Vertex AI returned HTTP {exc.code}. "
                f"Retrying in {delay:.1f} seconds..."
            )

            time.sleep(delay)

        finally:
            # Close the client after all retries, not per attempt.
            pass

    raise RuntimeError("Gemini request failed unexpectedly")



if __name__ == "__main__":
    prompt = "Find 3 devotional Hindi songs for morning listening"

    intent = parse_intent(prompt)

    print(intent.model_dump_json(indent=2))
