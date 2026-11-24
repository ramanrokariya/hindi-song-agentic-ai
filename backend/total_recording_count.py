# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book


import json

with open("data/hindi_songs_catalog.json", encoding="utf-8") as file:
    catalog = json.load(file)

ids = [song["musicbrainz_id"] for song in catalog]

print("Total recordings:", len(catalog))
print("Unique MusicBrainz IDs:", len(set(ids)))
print("Duplicates:", len(ids) - len(set(ids)))

