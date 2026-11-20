
import re

from backend.song_search_service import search_songs


def parse_query(query):
    """
    Convert a simple natural-language request
    into structured search filters.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")

    text = query.casefold()

    filters = {}

    filters["unique_titles"] = True

    # Extract requested number of songs.
    count_match = re.search(
        r"\b(?:find|show|give me|list)\s+(\d+)\b",
        text,
    )

    filters["limit"] = (
        min(int(count_match.group(1)), 50)
        if count_match else 5
    )

    if filters["limit"] < 1:
        raise ValueError("Requested song count must be positive")

    # Discovery categories.
    if "garba" in text or "dandiya" in text:
        filters["category"] = "garba"
    elif "krishna" in text or "kanha" in text:
        filters["category"] = "krishna_bhajan"

    # Genre.
    if "devotional" in text or "bhajan" in text:
        filters["genre"] = "devotional"
    elif "patriotic" in text:
        filters["genre"] = "patriotic"
    elif "romantic" in text:
        filters["genre"] = "romantic"
    elif "folk" in text:
        filters["genre"] = "folk"

    # Listening time.
    if "morning" in text:
        filters["listening_time"] = "morning"
    elif "evening" in text:
        filters["listening_time"] = "evening"
    elif "night" in text:
        filters["listening_time"] = "night"

    # Occasions.
    if "navratri" in text:
        filters["occasion"] = "Navratri"
    elif "independence day" in text:
        filters["occasion"] = "Independence Day"

    # Mood.

    # Mood.
    if re.search(r"\b(sad|sadness|melancholic|melancholy)\b", text):
        filters["mood"] = "sad"
    elif re.search(r"\b(peaceful|calm|relaxing)\b", text):
        filters["mood"] = "peaceful"
    elif re.search(r"\b(energetic|upbeat|lively)\b", text):
        filters["mood"] = "energetic"
    elif re.search(r"\b(happy|cheerful|joyful)\b", text):
        filters["mood"] = "happy"

    return filters


def natural_language_search(query):
    """
    Parse the query and search the local catalog.
    """
    filters = parse_query(query)

    # Return filters alongside results for transparency.
    return {
        "query": query,
        "filters": filters,
        "results": search_songs(**filters),
    }


def main():
    print("\n========== HINDI SONG AI SEARCH ==========")
    print("Enter a request or type 'exit' to quit.")

    while True:
        try:
            query = input("\nSearch> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            response = natural_language_search(query)
        except ValueError as exc:
            print("Invalid query:", exc)
            continue

        print("\nParsed filters:", response["filters"])
        print("Results returned:", len(response["results"]))

        for index, song in enumerate(
            response["results"], start=1
        ):
            artists = ", ".join(song["artists"])

            print(
                f"{index}. {song['title']} "
                f"| {artists} "
                f"| Genre: {song['genre']}"
            )


if __name__ == "__main__":
    main()

