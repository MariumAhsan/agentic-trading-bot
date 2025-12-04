import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Define symbol and time range
symbol = "AAPL"
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)  # ~5 years

# Fetch historical data
df = yf.download(symbol, start=start_date, end=end_date, interval="1d")

# Reset index to get 'Date' as column
df.reset_index(inplace=True)

# Optional: rename columns for consistency
df = df.rename(columns={
    "Date": "timestamp",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume"
})

# Save to CSV for training
df.to_csv("data/AAPL_5y.csv", index=False)

print("✅ 5-year AAPL data downloaded and saved to data/AAPL_5y.csv")
