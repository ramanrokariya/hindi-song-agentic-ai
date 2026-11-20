
import os

from google import genai
from google.genai import types

from backend.song_search_agent import run_song_agent


MODEL_NAME = "gemini-2.5-flash"


def create_client():
    return genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.getenv(
            "GOOGLE_CLOUD_LOCATION",
            "us-central1",
        ),
    )


def explain_recommendations(user_query, results):
    if not results:
        return "No matching songs were found in the catalog."

    song_details = "\n".join(
        (
            f"- Title: {song['title']}; "
            f"Similarity: {song['similarity']}; "
            f"Exact structured match: "
            f"{song['structured_match']}"
        )
        for song in results
    )

    prompt = f"""
You are a Hindi music recommendation assistant.

User request:
{user_query}

Retrieved song recordings:
{song_details}

Explain the recommendations in friendly, clear English.

Rules:
- Recommend only titles present in the retrieved results.
- Do not invent artists, raagas, lyrics, or historical facts.
- Do not claim that a song satisfies a particular listening
  time or occasion unless the supplied evidence confirms it.
- A semantic similarity score is not a confidence percentage.
- If structured_match is False, explain that the song is
  a semantic recommendation rather than an exact metadata match.
- Avoid repeating the same title unnecessarily.
- Keep the response concise.
"""

    client = create_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
        ),
    )

    return response.text


def recommend_songs(user_query):
    search_response = run_song_agent(user_query)

    explanation = explain_recommendations(
        user_query,
        search_response["results"],
    )

    return {
        **search_response,
        "explanation": explanation,
    }


def main():
    print("\n========== HINDI SONG AI RECOMMENDATION AGENT ==========")
    print("Type 'exit' to quit.")

    while True:
        try:
            query = input("\nRecommendation Agent> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            response = recommend_songs(query)

            print("\nRecommended songs:")

            for index, song in enumerate(
                response["results"],
                start=1,
            ):
                print(
                    f"{index}. {song['title']} "
                    f"| Similarity: {song['similarity']:.4f}"
                )

            print("\n========== GEMINI EXPLANATION ==========")
            print(response["explanation"])

        except Exception as exc:
            print("Recommendation error:", exc)


if __name__ == "__main__":
    main()

