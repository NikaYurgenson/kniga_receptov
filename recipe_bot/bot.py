"""Recipe and Music Telegram bot module."""

from io import BytesIO
import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from recipe_bot.config import API_TOKEN
from recipe_bot.parser import get_random_recipe
from recipe_bot.music import get_random_fma_track, download_track

# Configure logging
logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    """Form state for recipe category selection."""
    category = State()


class MusicStates(StatesGroup):
    """Form states for music selection."""
    waiting_for_genre = State()


def create_category_keyboard():
    """Create inline keyboard with recipe categories."""
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton(text='Супы', callback_data='category_soups'),
        InlineKeyboardButton(text='Салаты', callback_data='category_salads'),
        InlineKeyboardButton(text='Каши', callback_data='category_porridge'),
        InlineKeyboardButton(text='Гарниры', callback_data='category_sides'),
        InlineKeyboardButton(text='Рыба', callback_data='category_fish'),
        InlineKeyboardButton(text='Мясо', callback_data='category_meat'),
        InlineKeyboardButton(text='Десерты', callback_data='category_dessert')
    )
    return kb


def create_genre_keyboard():
    """Create inline keyboard with music genres."""
    from recipe_bot.config import FMA_GENRES
    kb = InlineKeyboardMarkup(row_width=3)
    for genre in FMA_GENRES.keys():
        kb.insert(InlineKeyboardButton(text=genre, callback_data=f"genre_{genre}"))
    return kb


def create_main_keyboard():
    """Create main menu keyboard."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text='🍲 Рецепты', callback_data='menu_recipes'),
        InlineKeyboardButton(text='🎵 Музыка', callback_data='menu_music')
    )
    return kb


class RecipeBot:
    """Recipe and Music Telegram bot class."""

    def __init__(self):
        self.bot = Bot(token=API_TOKEN)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.category_kb = create_category_keyboard()
        self.genre_kb = create_genre_keyboard()
        self.main_kb = create_main_keyboard()
        self._register_handlers()

    def _register_handlers(self):
        """Register message and callback handlers."""
        # Basic commands
        self.dp.register_message_handler(self.cmd_start, commands=['start'])
        self.dp.register_message_handler(self.cmd_help, commands=['help'])

        # Main menu navigation
        self.dp.register_callback_query_handler(
            self.process_main_menu,
            lambda c: c.data and c.data.startswith('menu_'),
            state="*"
        )

        # Recipe handlers
        self.dp.register_callback_query_handler(
            self.process_recipe_category,
            lambda c: c.data and c.data.startswith('category_'),
            state=Form.category
        )

        # Music handlers
        self.dp.register_callback_query_handler(
            self.process_music_genre,
            lambda c: c.data and c.data.startswith('genre_'),
            state=MusicStates.waiting_for_genre
        )

    async def cmd_start(self, message: types.Message):
        """Handle /start command."""
        await message.answer(
            "👋 Привет! Я ваш помощник для рецептов и музыки. Выберите, что вам нужно:",
            reply_markup=self.main_kb
        )

    async def cmd_help(self, message: types.Message):
        """Handle /help command."""
        help_text = (
            "🤖 <b>Доступные команды:</b>\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку\n\n"
            "📋 <b>Возможности:</b>\n"
            "• 🍲 <b>Рецепты</b> - получайте рецепты по категориям\n"
            "• 🎵 <b>Музыка</b> - слушайте музыку по жанрам\n"
        )
        await message.answer(help_text, parse_mode="HTML")

    async def process_main_menu(self, callback_query: types.CallbackQuery, state: FSMContext):
        """Process main menu selection."""
        await callback_query.answer()
        choice = callback_query.data.split('_')[1]

        if choice == "recipes":
            await callback_query.message.answer(
                "Выберите категорию рецептов:",
                reply_markup=self.category_kb
            )
            await Form.category.set()

        elif choice == "music":
            await callback_query.message.answer(
                "Выберите жанр музыки:",
                reply_markup=self.genre_kb
            )
            await MusicStates.waiting_for_genre.set()

    async def process_recipe_category(self, callback_query: types.CallbackQuery, state: FSMContext):
        """Process recipe category selection."""
        category = callback_query.data.split('_')[1]
        await callback_query.answer()

        await callback_query.message.answer("⏳ Ищу рецепт...")

        try:
            recipe_text, image_url = get_random_recipe(category)
            if recipe_text:
                # If we have an image, send it with caption or separately
                if image_url:
                    try:
                        await self.bot.send_photo(
                            callback_query.message.chat.id,
                            photo=image_url,
                            caption=recipe_text if len(recipe_text) <= 1024 else "Рецепт в следующем сообщении",
                            parse_mode='HTML'
                        )
                        if len(recipe_text) > 1024:
                            await callback_query.message.answer(
                                recipe_text,
                                parse_mode='HTML',
                                disable_web_page_preview=True
                            )
                    except Exception:
                        # If image sending fails, just send text
                        await callback_query.message.answer(
                            recipe_text,
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        )
                else:
                    # No image, send text only
                    await callback_query.message.answer(
                        recipe_text,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )

                # Ask if user wants another recipe
                kb = InlineKeyboardMarkup()
                kb.add(
                    InlineKeyboardButton("🔄 Еще рецепт", callback_data=f"category_{category}"),
                    InlineKeyboardButton("📋 Главное меню", callback_data="menu_recipes")
                )
                await callback_query.message.answer("Хотите еще рецепт?", reply_markup=kb)
            else:
                await callback_query.message.answer("Рецепты не найдены.")
                await self.cmd_start(callback_query.message)
        except Exception as e:
            await callback_query.message.answer("Произошла ошибка при загрузке рецепта.")
            logging.error(f"Error: {e}")
            await self.cmd_start(callback_query.message)

        await state.finish()

    async def process_music_genre(self, callback_query: types.CallbackQuery, state: FSMContext):
        """Process music genre selection."""
        genre = callback_query.data.split('_')[1]
        await callback_query.answer()

        await callback_query.message.answer(f"⏳ Ищу трек в жанре {genre}...")

        try:
            track, used_genre = await get_random_fma_track(genre)
            if not track or 'playbackUrl' not in track:
                await callback_query.message.answer("😞 Не удалось найти трек. Попробуйте позже.")
                await self.cmd_start(callback_query.message)
                await state.finish()
                return

            stream_url = track['playbackUrl']
            title = track.get("title", "Unknown Track")
            artist = track.get("artistName", "Unknown Artist")

            music_data = await download_track(stream_url)
            if not music_data:
                await callback_query.message.answer("😞 Не удалось скачать трек. Попробуйте позже.")
                await state.finish()
                return

            filename = f"{artist} - {title}.mp3"

            # Send track info and file
            caption = f"🎵 <b>{title}</b>\n👤 {artist}\n🎧 Жанр: {used_genre}"
            await self.bot.send_audio(
                callback_query.message.chat.id,
                audio=InputFile(BytesIO(music_data), filename=filename),
                title=title,
                performer=artist,
                caption=caption,
                parse_mode="HTML"
            )

            # Ask if user wants another track
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton("🔄 Еще трек", callback_data=f"genre_{used_genre}"),
                InlineKeyboardButton("🎸 Другой жанр", callback_data="menu_music"),
                InlineKeyboardButton("📋 Главное меню", callback_data="menu_recipes")
            )
            await callback_query.message.answer("Хотите еще музыки?", reply_markup=kb)
        except Exception as e:
            await callback_query.message.answer("Произошла ошибка при загрузке трека.")
            logging.error(f"Error: {e}")
            await self.cmd_start(callback_query.message)

        await state.finish()

    def run(self):
        """Start the bot."""
        executor.start_polling(self.dp, skip_updates=True)

