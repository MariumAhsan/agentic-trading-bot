# data/market_data.py

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")

# Alpaca data client (works for free users too)
client = StockHistoricalDataClient(API_KEY, API_SECRET)


def get_latest_price(symbol="AAPL"):
    """Fetch latest available daily closing price."""

    end = datetime.now()
    start = end - timedelta(days=5)   # Enough buffer to ensure at least 1 bar returned

    request = StockBarsRequest(
        symbol_or_symbols=[symbol],    # MUST be a list in alpaca-py
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed="iex"                     # Free market data feed
    )

    try:
        bars = client.get_stock_bars(request)

        # Convert to df
        if hasattr(bars, "df"):
            df = bars.df
        else:
            print("❌ No .df in API response")
            return None

        if df.empty:
            print("❌ No price data returned.")
            return None

        # Extract latest close
        latest_close = df["close"].iloc[-1]
        latest_close = float(latest_close)

        print(f"✅ Latest {symbol} close price: {latest_close}")

        return latest_close

    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return None
