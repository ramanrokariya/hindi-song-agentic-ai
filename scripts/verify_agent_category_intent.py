# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import argparse

from backend.agent_query_understanding import understand_query


TEST_CASES = [
    (
        "garba",
        "Find traditional Garba songs for Dandiya",
        "garba",
        None,
    ),
    (
        "krishna",
        "Find Krishna Bhajans",
        "krishna_bhajan",
        None,
    ),
    (
        "romantic",
        "Find romantic songs",
        None,
        "romantic",
    ),
    (
        "devotional",
        "Find devotional songs",
        None,
        "devotional",
    ),
    (
        "folk_garba",
        "Find folk Garba songs",
        "garba",
        "folk",
    ),
]


def main():
    parser = argparse.ArgumentParser(
        description="Verify Gemini category interpretation"
    )

    parser.add_argument(
        "--case",
        choices=["all"] + [case[0] for case in TEST_CASES],
        default="all",
        help="Select an individual verification scenario",
    )

    args = parser.parse_args()

    selected = [
        case for case in TEST_CASES
        if args.case == "all" or case[0] == args.case
    ]

    passed = 0
    failed = 0

    for name, query, expected_category, expected_genre in selected:

        print("\n" + "=" * 60)
        print("Scenario:", name)
        print("Query:", query)

        try:
            intent = understand_query(query)

            print(intent.model_dump_json(indent=2))

            print("Expected category:", expected_category)
            print("Actual category:", intent.category)

            print("Expected genre:", expected_genre)
            print("Actual genre:", intent.genre)

            assert intent.category == expected_category, (
                "Category interpretation mismatch"
            )

            assert intent.genre == expected_genre, (
                "Genre interpretation mismatch"
            )

            passed += 1
            print("PASS: Query interpretation verified")

        except Exception as exc:
            failed += 1
            print("FAIL:", exc)

    print("\n========== VERIFICATION SUMMARY ==========")
    print("Total scenarios:", len(selected))
    print("Passed:", passed)
    print("Failed:", failed)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
