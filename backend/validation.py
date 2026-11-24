# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import json

with open("data/hindi_songs_catalog.json", encoding="utf-8") as f:
    songs = json.load(f)

print(f"Total recordings: {len(songs)}")
print("-" * 65)

for index, song in enumerate(songs, start=1):
    artists = ", ".join(
        artist for artist in song.get("artists", [])
        if artist
    )

    print(f"{index:02d}. {song.get('title')}")
    print(f"    Artist: {artists or 'Unknown'}")
    print(f"    Search term: {song.get('search_term')}")
