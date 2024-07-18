from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_API = os.getenv('TG_BOT_API')
CRYPTO_API = os.getenv('COIN_MARKET_API')

