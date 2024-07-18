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

