import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command

from exceptions import InvalidCryptoNameException
from models import CryptoTrackInfo
from service import get_crypto_price, notify_price_drop, notify_price_rise, validate_threshold
from config import TELEGRAM_API


bot = Bot(token=TELEGRAM_API)
dp = Dispatcher()


class TrackCrypto(StatesGroup):
    waiting_for_crypto_name = State()
    waiting_for_min_threshold = State()
    waiting_for_max_threshold = State()


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Привет! \n Для остлеживания криптовалюты используй команду /track")


@dp.message(Command("track"))
async def track_crypto(message: types.Message, state: FSMContext):
    await message.answer("Введите тикер криптовалюты для остлеживания: \n"
                         "(пример1: BTC, пример2: ETH)")
    await state.set_state(TrackCrypto.waiting_for_crypto_name)


@dp.message(TrackCrypto.waiting_for_crypto_name)
async def crypto_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(crypto_name=message.text.upper())
    await message.answer("Введите минимальную пороговую сумму в USD: \n"
                         "пример1: 65300, пример2: 3400")
    await state.set_state(TrackCrypto.waiting_for_min_threshold)


@dp.message(TrackCrypto.waiting_for_min_threshold)
async def min_threshold_entered(message: types.Message, state: FSMContext):
    min_threshold = await validate_threshold(message.text)

    await state.update_data(min_threshold=min_threshold)
    await message.answer("Введите максимальную пороговую сумму в USD: \n"
                         "пример1: 73780, пример2: 4878")
    await state.set_state(TrackCrypto.waiting_for_max_threshold)


@dp.message(TrackCrypto.waiting_for_max_threshold)
async def max_threshold_entered(message: types.Message, state: FSMContext):
    max_threshold = await validate_threshold(message.text)

    user_data = await state.get_data()
    min_threshold = user_data['min_threshold']

    if max_threshold <= min_threshold:
        await message.reply("Ошибка: Максимальная пороговая сумма должна быть больше минимальной.")
        return

    crypto_name = user_data['crypto_name']
    chat_id = message.chat.id

    await CryptoTrackInfo.add_crypto_threshold(
        crypto_name=crypto_name,
        min_threshold=min_threshold,
        max_threshold=max_threshold,
        chat_id=chat_id
    )
    await message.answer(
        f"Готово! \n "
        f"Отслеживаю {crypto_name} с мин. порогом ${min_threshold} и макс. порогом ${max_threshold}.")
    await state.clear()


async def check_prices():
    while True:
        thresholds = await CryptoTrackInfo.find_all_unchecked()

        for threshold in thresholds:
            try:
                current_price = get_crypto_price(threshold.crypto_name)
            except InvalidCryptoNameException as e:
                logging.error(f"Error fetching price for {threshold.crypto_name}: {e}")
                continue

            if current_price <= threshold.min_threshold and not threshold.min_notified:
                await notify_price_drop(bot, threshold.chat_id, threshold.crypto_name, threshold.min_threshold,current_price)
                await CryptoTrackInfo.update_crypto_thresholds_by_id(threshold.id, min_notified=True)

            if current_price >= threshold.max_threshold and not threshold.max_notified:
                await notify_price_rise(bot, threshold.chat_id, threshold.crypto_name, threshold.max_threshold, current_price)
                await CryptoTrackInfo.update_crypto_thresholds_by_id(threshold.id, max_notified=True)

           # print(threshold.chat_id, threshold.min_notified, threshold.max_notified, current_price)
        await asyncio.sleep(30)


async def main() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(check_prices())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
