# trading/execute.py
from dotenv import load_dotenv
import os
import time

# Alpaca SDK imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Load environment variables
load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

# Initialize the Alpaca client
client = TradingClient(API_KEY, API_SECRET, paper=True)  # paper=True for paper trading

# ----------------------------
# Place Market Order
# ----------------------------
def place_order(symbol, qty, side):
    """
    Place a market order (BUY or SELL) for a given symbol and quantity.
    """
    try:
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.GTC  # Good Till Cancelled
        )

        order = client.submit_order(order_request)
        print(f"{side.upper()} order for {qty} {symbol} placed. id={order.id}")
        return order

    except Exception as e:
        print(f"Error placing order: {e}")
        return None

# ----------------------------
# Get Account Info
# ----------------------------
def get_account():
    """
    Fetch account details like equity, cash, buying power.
    """
    try:
        account = client.get_account()
        print(f"Account status: {account.status}")
        print(f"Buying Power: {account.buying_power}")
        print(f"Cash: {account.cash}")
        return account
    except Exception as e:
        print(f"Error fetching account info: {e}")
        return None
