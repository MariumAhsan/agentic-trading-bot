# backtest/backtest_sma.py
import pandas as pd
import numpy as np
from data.market_data import api  # careful: this imports the Alpaca client
from strategies.basic_strategy import simple_moving_average_decision

def backtest_sma(df, window=20, initial_cash=10000):
    """
    df must have 'close' column and datetime index sorted ascending.
    Returns a results dict with portfolio history.
    """
    df = df.copy()
    df['sma'] = df['close'].rolling(window).mean()
    cash = initial_cash
    position = 0
    portfolio_values = []

    for idx, row in df.iterrows():
        price = row['close']
        sma = row['sma']
        decision = simple_moving_average_decision(price, sma)
        # naive fixed-size trading for demonstration
        if decision == "BUY" and cash >= price:
            qty = int(cash // price)
            if qty > 0:
                position += qty
                cash -= qty * price
        elif decision == "SELL" and position > 0:
            cash += position * price
            position = 0
        total = cash + position * price
        portfolio_values.append(total)

    df['portfolio'] = portfolio_values
    return df

# Example usage (offline):
if __name__ == "__main__":
    # load csv historical OHLC (you can download from Alpaca or other sources)
    df = pd.read_csv("data/AAPL_daily.csv", parse_dates=['timestamp'], index_col='timestamp')
    res = backtest_sma(df, window=20)
    print(res[['close','sma','portfolio']].tail())
