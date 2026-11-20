"""Run example searches against the local Hindi song catalog.

Run from the project root:
    python -m tests.test_song_search_manual
or place this file in project root and run:
    python test_song_search.py

Requires backend/song_search_service.py and the catalog/enrichment JSON files.
No Gemini API calls are made.
"""

from backend.song_search_service import search_songs


def main():
    queries = [
        ("DEVOTIONAL SONGS", {"genre": "devotional"}),
        ("GARBA SONGS", {"category": "garba"}),
        ("PATRIOTIC SONGS", {"genre": "patriotic"}),
        ("MORNING SONGS", {"listening_time": "morning"}),
    ]

    for label, filters in queries:
        print(f"\n========== {label} ==========")
        songs = search_songs(**filters, limit=5)
        print(f"Results returned: {len(songs)}")

        for song in songs:
            artists = song.get("artists") or []
            artist_text = ", ".join(map(str, artists))
            print(
                f"{song['title']} | {artist_text} | "
                f"Genre: {song.get('genre')}"
            )


if __name__ == "__main__":
    main()
