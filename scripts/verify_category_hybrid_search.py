# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

from backend.postgres_hybrid_search import hybrid_search


def verify_category(query, category, expected_count):
    print("\n" + "=" * 60)
    print("Query:", query)
    print("Category:", category)

    results = hybrid_search(
        query=query,
        category=category,
        limit=10,
    )

    print("Expected results:", expected_count)
    print("Actual results:", len(results))

    assert len(results) == expected_count, (
        f"Expected {expected_count} results, "
        f"received {len(results)}"
    )

    assert all(
        song["category"] == category
        for song in results
    ), "Unexpected category found"

    assert all(
        song["structured_match"] is True
        for song in results
    ), "Structured matching flag is incorrect"

    scores = [
        song["similarity"]
        for song in results
    ]

    assert all(
        -1.0 <= score <= 1.0
        for score in scores
    ), "Invalid cosine similarity score"

    assert scores == sorted(
        scores, reverse=True
    ), "Results are not ranked correctly"

    for index, song in enumerate(results, start=1):
        print(
            f"{index}. {song['title']} "
            f"| Category: {song['category']} "
            f"| Genre: {song['genre']} "
            f"| Similarity: {song['similarity']:.4f}"
        )

    print("PASS: Category hybrid search verified")


def main():
    verify_category(
        query="Traditional Garba songs for Dandiya",
        category="garba",
        expected_count=7,
    )

    verify_category(
        query="Devotional bhajans dedicated to Lord Krishna",
        category="krishna_bhajan",
        expected_count=7,
    )

    verify_category(
        query="Songs for a nonexistent category",
        category="nonexistent_test_category",
        expected_count=0,
    )

    print("\nALL CATEGORY HYBRID SEARCH CHECKS PASSED")


if __name__ == "__main__":
    main()
