import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
import aiohttp

API_TOKEN = '1718355118:AAFkuoOFyJVkVy21CarleBjeaM_3O55G680'
GAME_SHORT_NAME = "Flop"
# URL of our FastAPI server with hosted web app
GAME_URL = "http://localhost:8000/game.html"
# URL of new frontend for Telegram Web App
WEB_APP_URL = "http://localhost:8000/frontend/index.html"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=['start', 'play']))
async def send_game(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Играть", callback_game=types.CallbackGame())]
    ])
    await message.answer_game(game_short_name=GAME_SHORT_NAME, reply_markup=keyboard)

@dp.message(Command('matchmake'))
async def make_match(message: types.Message):
    """Request matchmaking from the FastAPI server."""
    async with aiohttp.ClientSession() as session:
        resp = await session.post('http://localhost:8000/matchmake', json={'player_id': str(message.from_user.id)})
        data = await resp.json()
    await message.answer(f"Server response: {data}")

@dp.callback_query(lambda c: c.game_short_name == GAME_SHORT_NAME)
async def process_callback(callback_query: CallbackQuery):
    await bot.answer_callback_query(
        callback_query.id,
        url=GAME_URL
    )

@dp.message(Command('app'))
async def send_web_app(message: types.Message):
    """Send keyboard that opens the frontend as a Telegram Web App."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Open Lobby", web_app=types.WebAppInfo(url=WEB_APP_URL))]
        ]
    )
    await message.answer("Открыть приложение", reply_markup=kb)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
