"""Recipe parser module."""

import httpx
from bs4 import BeautifulSoup
import random

from recipe_bot.config import HEADERS, CATEGORY_URLS


def parse_full_recipe(recipe_url):
    """Parse a recipe from povarenok.ru website."""
    response = httpx.get(recipe_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Без названия"

    ingredients = []
    ingr_section = soup.find('div', class_='ingredients') or soup.find('div', class_='ingredients-bl')
    if ingr_section:
        for li in ingr_section.find_all('li'):
            ingr_text = li.get_text(separator=' ', strip=True)
            if ingr_text:
                ingredients.append(ingr_text)

    steps = []
    ul = soup.find('ul', itemprop='recipeInstructions')
    if ul:
        for li in ul.find_all('li', class_='cooking-bl'):
            p = li.find('p')
            if p:
                steps.append(p.get_text(separator=' ', strip=True))

    text = f"🍽 <b>{title}</b>\n\n"
    text += "🛒 <b>Ингредиенты:</b>\n"
    text += "".join(f"  • {ingr}\n" for ingr in ingredients) if ingredients else "  Нет данных.\n"

    text += "\n👩‍🍳 <b>Приготовление:</b>\n"
    if steps:
        for i, step in enumerate(steps, 1):
            text += f"  {i}. {step}\n\n"
    else:
        text += "  Нет данных.\n"

    text += f"\n🔗 <i>Источник: <a href='{recipe_url}'>Povarenok.ru</a></i>"

    return text


def get_recipes_from_category(category, limit=10):
    """Get recipe URLs from a specific category."""
    url = CATEGORY_URLS.get(category)
    if not url:
        return []

    response = httpx.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='item-bl')

    recipes = []
    for article in articles[:limit]:
        a_tag = article.find('a')
        if not a_tag:
            continue
        link = a_tag['href']
        if not link.startswith('http'):
            link = "https://www.povarenok.ru" + link
        recipes.append(link)

    return recipes


def get_random_recipe(category):
    """Get a random recipe from the specified category."""
    recipes = get_recipes_from_category(category)
    if not recipes:
        return None

    recipe_url = random.choice(recipes)
    return parse_full_recipe(recipe_url)
