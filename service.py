import requests

from config import CRYPTO_API
from exceptions import InvalidCryptoNameException


def get_crypto_price(crypto_name):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': crypto_name,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CRYPTO_API,
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()
    if 'data' not in data or crypto_name not in data['data']:
        raise InvalidCryptoNameException(f"Invalid cryptocurrency name: {crypto_name}")
    return data['data'][crypto_name]['quote']['USD']['price']


async def notify_price_drop(bot, chat_id, crypto_name, min_threshold, current_price):
    await bot.send_message(
        chat_id,
        f"🚨 {crypto_name} упал ниже мин. порога ${min_threshold}. Текущая цена: ${current_price:.2f}"
    )


async def notify_price_rise(bot, chat_id, crypto_name, max_threshold, current_price):
    await bot.send_message(
        chat_id,
        f"🚨 {crypto_name} поднялся выше макс. порога ${max_threshold}. Текущая цена: ${current_price:.2f}"
    )


async def validate_threshold(value: str) -> float:
    try:
        threshold = float(value)
        if threshold < 0:
            raise ValueError("Значение не может быть отрицательным.")
        return threshold
    except ValueError as e:
        raise ValueError(f"Ошибка: {e}. Пожалуйста, введите положительное число.")

