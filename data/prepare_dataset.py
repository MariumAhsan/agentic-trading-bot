import pandas as pd
import numpy as np

# -----------------------------
# FEATURE ENGINEERING FUNCTIONS
# -----------------------------

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def prepare_stock_dataset(df):
    # Sort by date
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Basic returns
    df["return"] = df["close"].pct_change()

    # Moving averages
    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_20"] = df["close"].rolling(20).mean()
    df["ma_50"] = df["close"].rolling(50).mean()

    # RSI
    df["rsi_14"] = compute_rsi(df["close"], 14)

    # Volatility
    df["volatility_10"] = df["return"].rolling(10).std()

    # Target: future return (next day)
    df["future_return"] = df["close"].shift(-1).pct_change()

    # Drop rows with missing values from rolling calculations
    df = df.dropna()

    return df


# -----------------------------
# MAIN SCRIPT
# -----------------------------

input_path = "data/AAPL_5y.csv"
output_path = "data/prepared_AAPL.csv"

print("📥 Loading raw CSV...")
df = pd.read_csv(input_path)

print("🛠 Preparing dataset...")
prepared = prepare_stock_dataset(df)

print("💾 Saving processed data...")
prepared.to_csv(output_path, index=False)

print("✅ Done! Saved to:", output_path)
