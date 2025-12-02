import sys
import os

# Fix imports so Streamlit can find project folders
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import streamlit as st
import plotly.graph_objs as go
from data.market_data import get_latest_price
from strategies.basic_strategy import simple_moving_average_decision
from trading.execute import place_order
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL")

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL)

# ----------------------------
# Streamlit UI Configuration
# ----------------------------
st.set_page_config(
    page_title="Agentic AI Trading Bot",
    layout="wide"
)

st.title("🧠 Agentic AI Trading Bot (Dashboard)")
st.write("Monitor prices, simulate trades, and track performance.")

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.header("⚙️ Controls")

symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")

if st.sidebar.button("Fetch Latest Price"):
    st.session_state["price"] = get_latest_price(symbol)

# Ensure price exists
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
# Get Historical Data (Chart)
# ----------------------------
st.subheader("📊 Price History")

closes = []   # <--- ensures availability outside the try-block

try:
    bars = api.get_bars(symbol, timeframe="1Day", limit=30)

    if bars:
        dates = [bar.t for bar in bars]
        closes = [bar.c for bar in bars]   # <--- now always assigned if data exists

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=closes, mode="lines"))
        fig.update_layout(title=f"{symbol} - Last 30 Days",
                          xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No historical data available.")

except Exception as e:
    st.error(f"Error fetching chart data: {e}")


# ----------------------------
# Trading Signal
# ----------------------------
st.subheader("🤖 Trading Decision")

if price:
    if len(closes) >= 5:
        moving_average = sum(closes[-5:]) / 5  # Simple 5-day MA
        decision = simple_moving_average_decision(price, moving_average)
        st.info(f"**Signal:** {decision}")
    else:
        st.warning("Not enough historical data to compute 5-day MA.")
        decision = "HOLD"

    qty = st.number_input("Quantity", min_value=1, value=1)

    if st.button(f"Execute {decision} Order"):
        if decision in ["BUY", "SELL"]:
            place_order(symbol, qty, decision.lower())
            st.success(f"{decision} order executed for {qty} shares of {symbol}.")
        else:
            st.warning("No action (HOLD).")
else:
    st.info("Price must be fetched before generating a signal.")

# ----------------------------
# Account Information
# ----------------------------
st.subheader("💰 Account Summary")

try:
    account = api.get_account()
    st.metric("Buying Power", f"${float(account.buying_power):,.2f}")
    st.metric("Equity", f"${float(account.equity):,.2f}")
    st.metric("Cash", f"${float(account.cash):,.2f}")
except:
    st.error("Could not fetch account info.")

# ----------------------------
# Trade Logs (Session-Based)
# ----------------------------
st.subheader("📝 Logs")

if "logs" not in st.session_state:
    st.session_state["logs"] = []

if st.button("Log Current Price"):
    st.session_state["logs"].append(f"{symbol}: ${price}")
    st.success("Logged!")

st.write("### Log History:")
st.write(st.session_state["logs"])
