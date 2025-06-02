"""Command Line Interface for Recipe Bot."""

from recipe_bot.bot import RecipeBot


def main():
    """Run the recipe bot as a CLI command."""
    print("Starting Recipe & Music Telegram Bot...")
    bot = RecipeBot()
    bot.run()


if __name__ == "__main__":
    main()
