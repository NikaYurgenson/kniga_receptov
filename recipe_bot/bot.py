"""Recipe Telegram bot module."""

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from recipe_bot.config import API_TOKEN
from recipe_bot.parser import get_random_recipe


class Form(StatesGroup):
    """Form state for category selection."""
    category = State()


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


class RecipeBot:
    """Recipe Telegram bot class."""

    def __init__(self):
        self.bot = Bot(token=API_TOKEN)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.category_kb = create_category_keyboard()
        self._register_handlers()

    def _register_handlers(self):
        """Register message and callback handlers."""
        self.dp.register_message_handler(self.cmd_start, commands=['start'])
        self.dp.register_callback_query_handler(
            self.process_category,
            lambda c: c.data and c.data.startswith('category_'),
            state=Form.category
        )

    async def cmd_start(self, message: types.Message):
        """Handle /start command."""
        await message.answer(
            "Привет! Я ваш кулинарный помощник. Выберите категорию рецептов.",
            reply_markup=self.category_kb
        )
        await Form.category.set()

    async def process_category(self, callback_query: types.CallbackQuery, state: FSMContext):
        """Process category selection."""
        category = callback_query.data.split('_')[1]
        await callback_query.answer()

        try:
            recipe_text = get_random_recipe(category)
            if recipe_text:
                await callback_query.message.answer(
                    recipe_text,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
            else:
                await callback_query.message.answer("Рецепты не найдены.")
        except Exception as e:
            await callback_query.message.answer("Произошла ошибка при загрузке рецепта.")
            print(f"Error: {e}")

        await state.finish()

    def run(self):
        """Start the bot."""
        executor.start_polling(self.dp, skip_updates=True)
