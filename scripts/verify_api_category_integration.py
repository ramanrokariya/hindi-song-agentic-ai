from fastapi.testclient import TestClient

from backend.main import app


TEST_CASES = [
    (
        "Find traditional Garba songs for Dandiya",
        "garba",
        None,
    ),
    (
        "Find Krishna Bhajans",
        "krishna_bhajan",
        None,
    ),
    (
        "Find devotional songs",
        None,
        "devotional",
    ),
]


def main():
    passed = 0
    failed = 0

    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:

        for query, category, genre in TEST_CASES:

            print("\n" + "=" * 60)
            print("Query:", query)

            try:
                response = client.post(
                    "/api/v1/songs/search",
                    json={"query": query},
                )

                print("HTTP status:", response.status_code)

                request_id = response.headers.get(
                    "X-Request-ID"
                )

                print("Request ID:", request_id)

                body = response.json()

                print("Response:", body)

                assert response.status_code == 200
                assert request_id
                assert body["query"] == query

                intent = body["intent"]
                results = body["results"]

                assert intent["category"] == category
                assert intent["genre"] == genre

                assert 0 < len(results) <= intent["limit"]

                for song in results:
                    assert song["musicbrainz_id"]
                    assert song["title"]
                    assert -1 <= song["similarity"] <= 1
                    assert song["structured_match"] is True
                    assert "category" in song

                    if category is not None:
                        assert song["category"] == category

                scores = [
                    song["similarity"]
                    for song in results
                ]

                assert scores == sorted(
                    scores,
                    reverse=True,
                )

                passed += 1

                print("Songs returned:", len(results))
                print("PASS: End-to-end verification")

            except Exception as exc:
                failed += 1
                print("FAIL:", repr(exc))

    print("\n========== VERIFICATION SUMMARY ==========")
    print("Total scenarios:", len(TEST_CASES))
    print("Passed:", passed)
    print("Failed:", failed)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
