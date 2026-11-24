# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import json
from pathlib import Path
from collections import Counter

files = [
    "data/hindi_songs_catalog.json",
    "data/hindi_songs_incremental.json",
]

for filename in files:
    records = json.loads(Path(filename).read_text())

    categories = Counter(
        song.get("discovery_category_hint") or "MISSING"
        for song in records
    )

    print("\nFile:", filename)
    print("Total records:", len(records))

    print("\nCategory distribution:")
    for category, count in categories.most_common():
        print(f"  {category}: {count}")

    print("\nSongs without category hints:")
    for song in records:
        if not song.get("discovery_category_hint"):
            print(f"  {song['title']}")
