import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command

API_TOKEN = '1718355118:AAFkuoOFyJVkVy21CarleBjeaM_3O55G680'
GAME_SHORT_NAME = "Flop"
GAME_URL = "https://flappybird-telegram.vercel.app/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command(commands=['start', 'play']))
async def send_game(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Играть", callback_game=types.CallbackGame())]
    ])
    await message.answer_game(game_short_name=GAME_SHORT_NAME, reply_markup=keyboard)


@dp.callback_query(lambda c: c.game_short_name == GAME_SHORT_NAME)
async def process_callback(callback_query: CallbackQuery):
    await bot.answer_callback_query(
        callback_query.id,
        url=GAME_URL
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # ⬅️ отключаем webhook
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
