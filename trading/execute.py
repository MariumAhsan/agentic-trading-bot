# trading/execute.py
from dotenv import load_dotenv
import os
import alpaca_trade_api as tradeapi
import time

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def place_order(symbol, qty, side, order_type="market", time_in_force="gtc"):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side.lower(),
            type=order_type,
            time_in_force=time_in_force
        )
        print(f"{side.upper()} order for {qty} {symbol} placed. id={order.id}")
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None

def get_account():
    try:
        return api.get_account()
    except Exception as e:
        print(f"Error fetching account: {e}")
        return None
