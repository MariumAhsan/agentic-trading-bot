# main.py
import time
from data.market_data import get_latest_price
from strategies.basic_strategy import simple_moving_average_decision
from trading.execute import place_order

symbol = "AAPL"
moving_average = 150  # hardcoded for now
while True:
    current_price = get_latest_price(symbol)
    if current_price is None:
        print("Skipping this cycle due to missing price.")
        time.sleep(60)
        continue

    print(f"Current price of {symbol}: {current_price}")
    decision = simple_moving_average_decision(current_price, moving_average)
    print(f"Decision: {decision}")

    if decision == "BUY":
        place_order(symbol, qty=1, side="buy")
    elif decision == "SELL":
        place_order(symbol, qty=1, side="sell")

    time.sleep(60)