
from backend.agent_query_understanding import understand_query
from backend.postgres_hybrid_search import hybrid_search


def run_song_agent(user_query):
    # Step 1: Gemini interprets the natural-language query.
    intent = understand_query(user_query)

    # Step 2: PostgreSQL handles structured metadata filtering
    # and pgvector cosine similarity ranking together.
    results = hybrid_search(
        query=intent.semantic_query or user_query,
        genre=intent.genre,
        mood=intent.mood,
        listening_time=intent.listening_time,
        occasion=intent.occasion,
        category=intent.category,
        limit=intent.limit,
    )

    # Step 3: Preserve the existing agent response contract.
    return {
        "query": user_query,
        "intent": intent.model_dump(),
        "results": results,
    }


def main():
    print("\n========== HINDI SONG AI AGENT ==========")
    print("Type 'exit' to quit.")

    while True:
        try:
            query = input("\nAI Agent> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            response = run_song_agent(query)
        except Exception as exc:
            print("Agent error:", exc)
            continue

        print("\nGemini understood:")
        print(response["intent"])

        print("\nRecommended songs:")

        if not response["results"]:
            print("No songs matched all structured filters.")

        for index, song in enumerate(
            response["results"],
            start=1,
        ):
            print(
                f"{index}. {song['title']} "
                f"| Similarity: {song['similarity']:.4f} "
                f"| Structured match: "
                f"{song['structured_match']}"
            )


if __name__ == "__main__":
    main()

