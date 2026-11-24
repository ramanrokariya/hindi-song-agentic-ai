# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import json

with open("data/hindi_songs_three_sample.json", encoding="utf-8") as f:
    songs = json.load(f)

ids = [song["musicbrainz_id"] for song in songs]

print("Total records:", len(songs))
print("Unique IDs:", len(set(ids)))

for song in songs:
    print(
        song["title"],
        "|",
        song["enrichment"]["classification_source"]
    )
