import json

with open("data/hindi_songs_incremental.json", encoding="utf-8") as f:
    songs = json.load(f)

ids = [song["musicbrainz_id"] for song in songs]

print("Total saved:", len(songs))
print("Unique IDs:", len(set(ids)))
print("Duplicates:", len(ids) - len(set(ids)))

