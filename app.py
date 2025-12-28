import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ---------------- CONFIG ----------------
RSI_PERIOD = 14

# ---------------- FETCH S&P 500 TICKERS ----------------
@st.cache_data(ttl=86400)
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]
    return table["Symbol"].str.replace(".", "-", regex=False).tolist()

# ---------------- RSI FUNCTION ----------------
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="S&P 500 RSI Screener", layout="wide")
st.title("📉 S&P 500 RSI Screener")
st.caption("14-Day RSI • All 500 Stocks • Live Data")

run = st.button("🚀 Run Scanner")

if run:
    tickers = get_sp500_tickers()
    results = []

    progress = st.progress(0)

    for i, ticker in enumerate(tickers):
        try:
            data = yf.Ticker(ticker).history(period="3mo")

            if data.empty or "Close" not in data or len(data) < RSI_PERIOD:
                continue

            rsi = round(calculate_rsi(data["Close"]), 2)

            status = (
                "Oversold" if rsi < 30 else
                "Overbought" if rsi > 70 else
                "Neutral"
            )

            results.append({
                "Ticker": ticker,
                "RSI": rsi,
                "Status": status
            })

        except Exception:
            pass

        progress.progress((i + 1) / len(tickers))

    df = pd.DataFrame(results)

    if df.empty:
        st.error("No data fetched. Yahoo Finance rate-limit hit.")
        st.stop()

    df = df.sort_values("RSI")

    st.success(f"Scan complete — {len(df)} stocks processed")

    col1, col2, col3 = st.columns(3)
    col1.metric("Oversold (<30)", len(df[df["RSI"] < 30]))
    col2.metric("Neutral (30–70)", len(df[(df["RSI"] >= 30) & (df["RSI"] <= 70)]))
    col3.metric("Overbought (>70)", len(df[df["RSI"] > 70]))

    st.dataframe(df, use_container_width=True)

