# dashboard/app.py
import os
import sys
import joblib
import streamlit as st
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import numpy as np

# Add project root to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# ----------------------------
# Project Imports
# ----------------------------
from data.market_data import get_latest_price
from strategies.basic_strategy import simple_moving_average_decision
from trading.execute import place_order
from stable_baselines3 import PPO
from training.env import TradingEnv

# ----------------------------
# Streamlit UI Configuration
# ----------------------------
st.set_page_config(page_title="Agentic AI Trading Bot", layout="wide")
st.title("🧠 Agentic AI Trading Bot (Dashboard)")
st.write("Monitor prices, simulate trades, and track performance.")

# ----------------------------
# Sidebar Controls
# ----------------------------
st.sidebar.header("⚙️ Controls")
symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")

if st.sidebar.button("Fetch Latest Price"):
    st.session_state["price"] = get_latest_price(symbol)

price = st.session_state.get("price", None)

# ----------------------------
# Display Latest Price
# ----------------------------
st.subheader(f"📈 Current Price for {symbol}")
if price:
    st.metric(label="Latest Price", value=f"${price:.2f}")
else:
    st.warning("No price available yet. Press 'Fetch Latest Price'.")

# ----------------------------
# Load Historical Data for Chart & ML
# ----------------------------
try:
    df = pd.read_csv(f"data/prepared_{symbol}.csv")
except FileNotFoundError:
    st.error(f"Prepared dataset for {symbol} not found.")
    st.stop()

closes = df['close'].tolist()
dates = df['timestamp'].tolist()

fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=closes, mode="lines", name="Close Price"))
for ma in ['ma_5', 'ma_20']:
    if ma in df.columns:
        fig.add_trace(go.Scatter(x=dates, y=df[ma], mode="lines", name=ma.upper()))
st.subheader("📊 Price History with Moving Averages")
st.plotly_chart(fig, width='stretch')

# ----------------------------
# Load ML Models
# ----------------------------
ml_models = {}
ml_folder = os.path.join(ROOT_DIR, "training", "models", "ml")
if os.path.exists(ml_folder):
    for model_file in os.listdir(ml_folder):
        if model_file.endswith(".pkl"):
            name = model_file.replace(".pkl", "")
            ml_models[name] = joblib.load(os.path.join(ml_folder, model_file))
else:
    st.warning("ML models folder not found. Train ML models first.")

# ----------------------------
# Load RL Model
# ----------------------------
rl_model = None
rl_env = None
rl_model_path = os.path.join(ROOT_DIR, "training", "models", "rl", f"ppo_{symbol.lower()}_final.zip")
if os.path.exists(rl_model_path):
    rl_env = TradingEnv(df)  # v1 environment
    rl_model = PPO.load(rl_model_path, env=rl_env)
    st.info("✅ RL model loaded and ready.")
else:
    st.warning("RL model not found. Train RL model in training/train_rl_bot.py")

# ----------------------------
# Trading Signals
# ----------------------------
st.subheader("🤖 Trading Decision")

if price:
    # SMA Signal
    moving_average = sum(closes[-5:]) / 5 if len(closes) >= 5 else None
    sma_decision = simple_moving_average_decision(price, moving_average)

    # ML Predictions
    ml_predictions = {}
    features = df.iloc[-1:].drop(columns=['timestamp', 'future_return'], errors='ignore')
    for name, model in ml_models.items():
        try:
            pred = model.predict(features)[0]
        except Exception:
            pred = np.nan
        ml_predictions[name] = pred

    st.write(f"**SMA Signal:** {sma_decision}")
    st.write("**ML Predictions:**")
    for name, pred in ml_predictions.items():
        st.write(f"{name}: {pred:.4f}" if not np.isnan(pred) else f"{name}: N/A")

    # Combined Decision (SMA + ML)
    actions = []
    if sma_decision == "BUY" or any(pred > price for pred in ml_predictions.values() if not np.isnan(pred)):
        actions.append("BUY")
    elif sma_decision == "SELL" or any(pred < price for pred in ml_predictions.values() if not np.isnan(pred)):
        actions.append("SELL")
    else:
        actions.append("HOLD")

    final_decision = max(set(actions), key=actions.count)
    st.info(f"**Combined Signal (SMA + ML):** {final_decision}")

    # Quantity for ML/SMA
    qty = st.number_input("Quantity (ML/SMA)", min_value=1, value=1)

    if st.button(f"Execute {final_decision} Order"):
        if final_decision in ["BUY", "SELL"]:
            order = place_order(symbol, qty, final_decision.lower())
            if order:
                if "trade_logs" not in st.session_state:
                    st.session_state["trade_logs"] = []
                st.session_state["trade_logs"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": symbol,
                    "action": final_decision,
                    "qty": qty,
                    "price": price,
                    "type": "ML/SMA"
                })
                st.success(f"{final_decision} order executed for {qty} shares of {symbol}. Logged automatically.")
        else:
            st.warning("No action (HOLD).")

    # ----------------------------
    # RL Decision
    # ----------------------------
    rl_action_str = None
    if rl_model and rl_env:
        obs = rl_env._get_obs()
        action, _ = rl_model.predict(obs, deterministic=True)
        rl_action_str = ["HOLD", "BUY", "SELL"][action]
        st.write(f"**RL Suggestion:** {rl_action_str}")

        # Quantity for RL
        qty_rl = st.number_input("Quantity (RL)", min_value=1, value=1, key="rl_qty")
        if st.button(f"Execute RL {rl_action_str} Order"):
            if rl_action_str in ["BUY", "SELL"]:
                order = place_order(symbol, qty_rl, rl_action_str.lower())
                if order:
                    if "trade_logs" not in st.session_state:
                        st.session_state["trade_logs"] = []
                    st.session_state["trade_logs"].append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "symbol": symbol,
                        "action": rl_action_str,
                        "qty": qty_rl,
                        "price": price,
                        "type": "RL",
                        "reward": (rl_env.balance + rl_env.shares * price) - 10000  # reward based on initial_balance
                    })
                    st.success(f"RL {rl_action_str} executed for {qty_rl} shares of {symbol}. Logged automatically.")

# ----------------------------
# Compare Signals
# ----------------------------
st.subheader("⚖️ Strategy Comparison")
ml_signal = final_decision if price else "N/A"
executed_trades = st.session_state.get("trade_logs", [])

st.write(f"- **ML Signal:** {ml_signal}")
st.write(f"- **RL Signal:** {rl_action_str if rl_action_str else 'N/A'}")
st.write("- **Executed Trades:**")
if executed_trades:
    trades_df = pd.DataFrame(executed_trades)
    st.dataframe(trades_df)
else:
    st.write("No trades executed yet.")

# Highlight conflicts
if rl_action_str and ml_signal != rl_action_str:
    st.warning("⚠ ML and RL signals disagree! Consider tracking this for reward feedback.")

# ----------------------------
# Account Summary
# ----------------------------
st.subheader("💰 Account Summary")
from alpaca.trading.client import TradingClient

load_dotenv()
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
api = TradingClient(API_KEY, API_SECRET, paper=True)

try:
    account = api.get_account()
    st.metric("Buying Power", f"${float(account.buying_power):,.2f}")
    st.metric("Equity", f"${float(account.equity):,.2f}")
    st.metric("Cash", f"${float(account.cash):,.2f}")
except Exception as e:
    st.error(f"Could not fetch account info: {e}")
# ----------------------------
# Update P/L for executed trades
# ----------------------------
if "trade_logs" in st.session_state and price:
    updated_logs = []
    for trade in st.session_state["trade_logs"]:
        # Calculate current equity
        if trade["type"] == "RL":
            # RL reward based on initial balance
            initial_balance = 10000
            current_equity = (trade["qty"] if trade["action"]=="BUY" else -trade["qty"]) * price + initial_balance
            trade["reward"] = current_equity - initial_balance
        elif trade["type"] == "ML/SMA":
            # For ML trades, approximate P/L if you want
            trade["reward"] = (price - trade["price"]) * trade["qty"] if trade["action"]=="BUY" else (trade["price"] - price) * trade["qty"]
        updated_logs.append(trade)
    st.session_state["trade_logs"] = updated_logs

# Display updated logs with P/L
st.subheader("📝 Trade Logs (Updated P/L)")
logs_df = pd.DataFrame(st.session_state.get("trade_logs", []))
if not logs_df.empty:
    st.dataframe(logs_df)
else:
    st.write("No trades executed yet.")
