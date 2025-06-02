"""Music parser module for FMA (Free Music Archive)."""

import json
import random
import logging
import httpx
from bs4 import BeautifulSoup

from recipe_bot.config import HEADERS, FMA_GENRES


async def get_random_fma_track(genre=None):
    """Get a random track from FMA based on genre."""
    if genre is None or genre not in FMA_GENRES:
        genre = random.choice(list(FMA_GENRES.keys()))
    url = FMA_GENRES[genre]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
            html = resp.text
        except httpx.HTTPStatusError as e:
            logging.error(f"Error HTTP {e.response.status_code} when loading genre {genre}")
            return None, genre

    soup = BeautifulSoup(html, "html.parser")
    track_divs = soup.find_all("div", class_="play-item")
    track_data_list = []

    for div in track_divs:
        data_attr = div.get("data-track-info")
        if data_attr:
            try:
                track_data = json.loads(data_attr.replace("&quot;", '"'))
                track_data_list.append(track_data)
            except json.JSONDecodeError:
                continue

    if not track_data_list:
        return None, genre

    return random.choice(track_data_list), genre


async def download_track(stream_url):
    """Download a track from the given URL."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(stream_url, headers=HEADERS)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            logging.error(f"Failed to download track: {e}")
            return None
