import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from pathlib import Path


URL = "https://musicbrainz.org/ws/2/recording/"

session = requests.Session()

session.headers.update({
    "User-Agent": "HindiSongAILab/0.1 (ramanrokariya@gmail.com)"
})

retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)

params = {
    "query": 'recording:"Lag Ja Gale"',
    "fmt": "json",
    "limit": 5
}

try:
    response = session.get(
        URL,
        params=params,
        timeout=(5, 20)
    )

    response.raise_for_status()

    data = response.json()

    output_file = Path("data/musicbrainz_songs.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Metadata successfully saved to: {output_file}")

    for song in data.get("recordings", []):
        print("Title:", song.get("title"))

        artists = [
            artist.get("name", "")
            for artist in song.get("artist-credit", [])
            if isinstance(artist, dict)
        ]

        print("Artists:", ", ".join(artists))
        print("MusicBrainz ID:", song.get("id"))
        print("-" * 40)

except requests.exceptions.RequestException as error:
    print("MusicBrainz API request failed.")
    print("Error:", error)
