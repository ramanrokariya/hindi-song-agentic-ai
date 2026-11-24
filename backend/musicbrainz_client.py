# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MusicBrainzClient:

    BASE_URL = "https://musicbrainz.org/ws/2/recording/"

    def __init__(self):
        contact_email = os.environ.get("MUSICBRAINZ_CONTACT_EMAIL")

        if not contact_email:
            raise ValueError(
                "Set MUSICBRAINZ_CONTACT_EMAIL before running."
            )

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"HindiSongAILab/0.1 ({contact_email})"
        })

        retry_policy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True
        )

        adapter = HTTPAdapter(max_retries=retry_policy)

        self.session.mount("https://", adapter)



    def search_songs(self, song_title, limit=5):
        params = {
            "query": f'recording:"{song_title}"',
            "fmt": "json",
            "limit": limit
        }

        response = self.session.get(
            self.BASE_URL,
            params=params,
            timeout=(5, 20)
        )

        response.raise_for_status()
        return response.json().get("recordings", [])
