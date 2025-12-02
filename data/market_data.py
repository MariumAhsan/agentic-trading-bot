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

client = StockHistoricalDataClient(API_KEY, API_SECRET)


def get_latest_price(symbol="AAPL"):
    """Fetch latest daily close price (works even on weekends)."""

    end = datetime.now()
    start = end - timedelta(days=5)

    request = StockBarsRequest(
        symbol_or_symbols=[symbol],   # LIST is required in new version
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed="iex"
    )

    try:
        bars = client.get_stock_bars(request)
        df = bars.df

        if df.empty:
            print("❌ No price data returned.")
            return None

        latest_close = df['close'].iloc[-1]
        print(f"✅ Latest {symbol} close price: {latest_close}")

        return float(latest_close)

    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return None
