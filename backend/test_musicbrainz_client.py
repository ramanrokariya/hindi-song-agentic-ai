# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import os
from musicbrainz_client import MusicBrainzClient

client = MusicBrainzClient()

songs = client.search_songs("Lag Ja Gale", limit=3)

for song in songs:
    print("Title:", song.get("title"))
    print("MusicBrainz ID:", song.get("id"))
    print("-" * 40)

print(f"Total recordings returned: {len(songs)}")
