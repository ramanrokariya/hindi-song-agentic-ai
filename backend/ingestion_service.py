# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import json
import time
from pathlib import Path

from musicbrainz_client import MusicBrainzClient

from logger import get_logger

logger = get_logger("song_ingestion")


class SongIngestionService:

    def __init__(self):
        self.client = MusicBrainzClient()

    def ingest(self, song_titles):
        catalog = []
        seen_ids = set()

        for title in song_titles:
            #print(f"Searching: {title}")
            logger.info(
            "Searching song metadata",
            extra={
                "event": "song_search_started",
                "song_title": title
            }
           )
            try:
                recordings = self.client.search_songs(
                    title, limit=5
                )

                for recording in recordings:
                    recording_id = recording.get("id")

                    if not recording_id or recording_id in seen_ids:
                        continue

                    seen_ids.add(recording_id)

                    catalog.append({
                        "musicbrainz_id": recording_id,
                        "title": recording.get("title"),
                        "artists": [
                            artist.get("name")
                            for artist in recording.get(
                                "artist-credit", []
                            )
                            if isinstance(artist, dict)
                        ],
                        "search_term": title
                    })

            except Exception as error:
               # print(f"Failed to retrieve {title}: {error}")
                logger.error(
                "MusicBrainz search failed",
                extra={
                    "event": "song_search_failed",
                    "song_title": title
                },
            exc_info=True
            )
            # Respect MusicBrainz's approximate
            # one-request-per-second rate limit.
            time.sleep(1.2)

        return catalog

 #   def save_catalog(self, catalog):
 #       output_file = Path("data/hindi_songs_catalog.json")
 #       output_file.parent.mkdir(
 #           parents=True, exist_ok=True
 #       )

  #      with output_file.open(
  #          "w", encoding="utf-8"
  #      ) as file:
  #          json.dump(
  #              catalog,
  #              file,
  #              indent=2,
  #              ensure_ascii=False
   #         )

        #print(f"Saved {len(catalog)} recordings")
        #print(f"Location: {output_file}")

    #    logger.info(
    #      f"Saved {len(catalog)} recordings to {output_file}",
    #        extra={
    #        "event": "catalog_saved"
    #       }
    #      )


    def save_catalog(self, catalog):
        output_file = Path("data/hindi_songs_catalog.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        existing_catalog = []

        if output_file.exists():
            with output_file.open("r", encoding="utf-8") as file:
                existing_catalog = json.load(file)

        combined = {}

        for song in existing_catalog + catalog:
            song_id = song.get("musicbrainz_id")

            if song_id:
                combined[song_id] = song

        merged_catalog = list(combined.values())

        temporary_file = output_file.with_suffix(".json.tmp")

        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(
                merged_catalog,
                file,
                indent=2,
                ensure_ascii=False
            )

        temporary_file.replace(output_file)

        logger.info(
            f"Saved {len(merged_catalog)} unique recordings",
            extra={"event": "catalog_saved"}
        )



if __name__ == "__main__":

    song_titles = [
        "Lag Ja Gale",
        "Ajeeb Dastan Hai Yeh",
        "Mere Sapno Ki Rani",
        "Chura Liya Hai Tumne"
    ]

    service = SongIngestionService()

    catalog = service.ingest(song_titles)

    service.save_catalog(catalog)
