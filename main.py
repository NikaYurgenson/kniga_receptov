#!/usr/bin/env python
"""Main entry point for the recipe bot."""

from recipe_bot.bot import RecipeBot


def main():
    """Run the recipe bot."""
    bot = RecipeBot()
    print("Starting Recipe Telegram Bot...")
    bot.run()


if __name__ == "__main__":
    main()
