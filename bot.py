import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command

from exceptions import InvalidCryptoNameException
from service import get_crypto_price
from config import TELEGRAM_API

bot = Bot(token=TELEGRAM_API)
dp = Dispatcher()


class TrackCrypto(StatesGroup):
    waiting_for_crypto_name = State()
    waiting_for_min_threshold = State()
    waiting_for_max_threshold = State()


crypto_thresholds = {}


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Welcome! Use /track to track a cryptocurrency.")


@dp.message(Command("track"))
async def track_crypto(message: types.Message, state: FSMContext):
    await message.answer("Please enter the cryptocurrency symbol (e.g., ETH):")
    await state.set_state(TrackCrypto.waiting_for_crypto_name)


@dp.message(TrackCrypto.waiting_for_crypto_name)
async def crypto_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(crypto_name=message.text.upper())
    await message.answer("Please enter the minimum threshold (e.g., 30000):")
    await state.set_state(TrackCrypto.waiting_for_min_threshold)


@dp.message(TrackCrypto.waiting_for_min_threshold)
async def min_threshold_entered(message: types.Message, state: FSMContext):
    await state.update_data(min_threshold=float(message.text))
    await message.answer("Please enter the maximum threshold (e.g., 60000):")
    await state.set_state(TrackCrypto.waiting_for_max_threshold)


@dp.message(TrackCrypto.waiting_for_max_threshold)
async def max_threshold_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    crypto_name = user_data['crypto_name']
    min_threshold = user_data['min_threshold']
    max_threshold = float(message.text)

    if crypto_name not in crypto_thresholds:
        crypto_thresholds[crypto_name] = []
    crypto_thresholds[crypto_name].append({
        'min_threshold': min_threshold,
        'max_threshold': max_threshold,
        'chat_id': message.chat.id
    })

    await message.answer(
        f"Tracking {crypto_name} with min threshold {min_threshold} and max threshold {max_threshold}.")
    await state.clear()


async def check_prices():
    while True:
        for crypto_name, thresholds in crypto_thresholds.items():
            try:
                current_price = get_crypto_price(crypto_name)
            except InvalidCryptoNameException as e:
                logging.error(f"Error fetching price for {crypto_name}: {e}")
                continue

            for threshold in thresholds:
                if current_price <= threshold['min_threshold']:
                    await bot.send_message(threshold['chat_id'], f"🚨 {crypto_name} has dropped below {threshold['min_threshold']}. Current price: ${current_price:.2f}")
                if current_price >= threshold['max_threshold']:
                    await bot.send_message(threshold['chat_id'], f"🚨 {crypto_name} has risen above {threshold['max_threshold']}. Current price: ${current_price:.2f}")
        print(crypto_thresholds)
        await asyncio.sleep(10)


async def main() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(check_prices())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
