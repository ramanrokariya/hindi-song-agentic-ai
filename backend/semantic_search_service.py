
from pathlib import Path

import numpy as np

from backend.embedding_service import generate_embedding
from backend.incremental_enrichment_service import load_json


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_FILE = (
    PROJECT_ROOT / "data/hindi_song_embeddings.json"
)


def semantic_search(query, limit=5):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must not be empty")

    if limit < 1:
        raise ValueError("Limit must be at least 1")

    records = load_json(EMBEDDINGS_FILE)

    if not records:
        return []

    # Convert the user's query into a vector.
    query_vector = np.asarray(
        generate_embedding(
            query,
            task_type="RETRIEVAL_QUERY",
        ),
        dtype=np.float32,
    )

    # Build a matrix containing all song vectors.
    song_matrix = np.asarray(
        [record["embedding"] for record in records],
        dtype=np.float32,
    )

    # Cosine similarity calculation.
    query_norm = np.linalg.norm(query_vector)
    song_norms = np.linalg.norm(
        song_matrix,
        axis=1,
    )

    denominators = song_norms * query_norm

    similarities = np.divide(
        song_matrix @ query_vector,
        denominators,
        out=np.zeros(len(records), dtype=np.float32),
        where=denominators != 0,
    )

    # Highest similarity first.
    ranked_indices = np.argsort(similarities)[::-1]

    results = []

    for index in ranked_indices[:limit]:
        record = records[int(index)]

        results.append({
            "musicbrainz_id": record["musicbrainz_id"],
            "title": record["title"],
            "similarity": round(
                float(similarities[index]), 4
            ),
            "description": record["description"],
        })

    return results


def main():
    print("\n========== HINDI SONG SEMANTIC SEARCH ==========")
    print("Type 'exit' to quit.")

    while True:
        try:
            query = input("\nSemantic Search> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if query.casefold() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            continue

        try:
            results = semantic_search(query)
        except Exception as exc:
            print("Search error:", exc)
            continue

        print("\nResults returned:", len(results))

        for position, song in enumerate(results, start=1):
            print(
                f"{position}. {song['title']} "
                f"| Similarity: {song['similarity']:.4f}"
            )


if __name__ == "__main__":
    main()

