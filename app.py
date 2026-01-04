import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ---------------- CONFIG ----------------
RSI_PERIOD = 14

# ---------------- FETCH S&P 500 TICKERS ----------------
@st.cache_data(ttl=86400)
def get_sp500_tickers():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
    df = pd.read_csv(url)
    return df["Symbol"].str.replace(".", "-", regex=False).tolist()

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
st.set_page_config(page_title="S&P 500 RSI + DMA Screener", layout="wide")
st.title("📉 S&P 500 RSI + DMA Screener")
st.caption("RSI • 50/100/200 DMA • Distance from 200 DMA")

run = st.button("🚀 Run Scanner")

if run:
    tickers = get_sp500_tickers()
    results = []

    progress = st.progress(0)

    for i, ticker in enumerate(tickers):
        try:
            data = yf.Ticker(ticker).history(period="1y")

            if data.empty or "Close" not in data or len(data) < 200:
                continue

            close = data["Close"]

            cmp = round(close.iloc[-1], 2)
            date = close.index[-1].date()

            rsi = round(calculate_rsi(close), 2)

            dma_50 = round(close.rolling(50).mean().iloc[-1], 2)
            dma_100 = round(close.rolling(100).mean().iloc[-1], 2)
            dma_200 = round(close.rolling(200).mean().iloc[-1], 2)

            diff_200 = round(cmp - dma_200, 2)
            diff_200_pct = round((diff_200 / dma_200) * 100, 2)

            status = (
                "Oversold" if rsi < 30 else
                "Overbought" if rsi > 70 else
                "Neutral"
            )

            results.append({
                "Ticker": ticker,
                "CMP": cmp,
                "Date": date,
                "RSI": rsi,
                "50 DMA": dma_50,
                "100 DMA": dma_100,
                "200 DMA": dma_200,
                "CMP - 200 DMA": diff_200,
                "% from 200 DMA": diff_200_pct,
                "Status": status
            })

        except Exception:
            pass

        progress.progress((i + 1) / len(tickers))

    df = pd.DataFrame(results)

    if df.empty:
        st.error("No data fetched. Try again (Yahoo rate limit).")
        st.stop()

    # -------- FORCE COLUMN ORDER --------
    df = df[
        [
            "Ticker",
            "CMP",
            "Date",
            "RSI",
            "50 DMA",
            "100 DMA",
            "200 DMA",
            "CMP - 200 DMA",
            "% from 200 DMA",
            "Status",
        ]
    ]

    df = df.sort_values("% from 200 DMA")

    st.success(f"Scan complete — {len(df)} stocks processed")

    st.dataframe(df, use_container_width=True)

