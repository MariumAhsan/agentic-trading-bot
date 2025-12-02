# tests/test_price_fetch.py
from data.market_data import get_latest_price

if __name__ == "__main__":
    price = get_latest_price("AAPL")
    if price:
        print(f"Latest AAPL price: {price}")
    else:
        print("Failed to fetch price.")
