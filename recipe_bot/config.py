"""Configuration for the recipe bot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API token from environment variables
API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise ValueError("API_TOKEN not found in environment variables. Please create a .env file with your API token.")

CATEGORY_URLS = {
    'soups': 'https://www.povarenok.ru/recipes/category/3/',
    'salads': 'https://www.povarenok.ru/recipes/category/1/',
    'porridge': 'https://www.povarenok.ru/recipes/category/24/',
    'sides': 'https://www.povarenok.ru/recipes/category/22/',
    'fish': 'https://www.povarenok.ru/recipes/category/17/',
    'meat': 'https://www.povarenok.ru/recipes/category/14/',
    'dessert': 'https://www.povarenok.ru/recipes/category/30/'
}

FMA_GENRES = {
    "Electronic": "https://freemusicarchive.org/genre/Electronic/",
    "Jazz": "https://freemusicarchive.org/genre/Jazz/",
    "Classical": "https://freemusicarchive.org/genre/Classical/",
    "Rock": "https://freemusicarchive.org/genre/Rock/",
    "Hip-Hop": "https://freemusicarchive.org/genre/Hip-Hop/",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
