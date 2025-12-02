import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load environment variables from .env
load_dotenv()

# Set up API credentials
API_KEY = os.getenv("PK0TF0AMLIV8EOFE6INU")
API_SECRET = os.getenv("tJslyaWNGYKywYf2Ov4GzhaDyWkaowvfzpn9EKAr")
BASE_URL = os.getenv("https://paper-api.alpaca.markets")

# Connect to Alpaca
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL)

# Test: Get account details
account = api.get_account()
print("Connection successful!")
print(f"Account status: {account.status}")
print(f"Buying power: ${account.buying_power}")

# test_price_fetch.py
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load environment variables
load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

if not API_KEY or not API_SECRET or not BASE_URL:
    print("❌ Missing API credentials. Check your .env file.")
    exit(1)

# Initialize API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Test account connection
try:
    account = api.get_account()
    print("✅ API connection successful.")
    print(f"Account status: {account.status}")
    print(f"Buying power: {account.buying_power}")
except Exception as e:
    print(f"❌ Failed to connect to API: {e}")
    exit(1)

# Test price fetch
try:
    symbol = "AAPL"
    bars = api.get_bars(symbol, timeframe="1Min", limit=1)
    if bars and len(bars) > 0:
        print(f"✅ Latest {symbol} close price: {bars[0].c}")
    else:
        print(f"⚠️ No bars returned for {symbol}.")
except Exception as e:
    print(f"❌ Error fetching bars for {symbol}: {e}")
