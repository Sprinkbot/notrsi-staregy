import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ---------------- CONFIG ----------------
RSI_PERIOD = 14

SP500_150 = [
    "AAPL","MSFT","AMZN","NVDA","GOOGL","META","TSLA","BRK-B","JPM","V",
    "LLY","UNH","XOM","AVGO","JNJ","WMT","PG","MA","COST","HD",
    "ORCL","MRK","ABBV","CRM","BAC","NFLX","CVX","KO","PEP","ADBE",
    "TMO","LIN","AMD","MCD","ACN","DIS","CSCO","WFC","ABT","INTC",
    "DHR","VZ","TXN","PM","COP","IBM","CAT","GE","AMAT","RTX",
    "NOW","ISRG","GS","SPGI","INTU","LOW","UNP","BKNG","ELV","MDT",
    "DE","LMT","ADI","UPS","SCHW","PLD","SYK","BLK","MU","CB",
    "AMGN","CI","BA","MDLZ","GILD","MMC","TGT","MO","SO","PGR",
    "ICE","ZTS","APD","DUK","CL","EOG","BDX","USB","AON","EQIX",
    "PNC","ITW","CCI","SHW","NSC","HUM","FIS","REGN","SLB","WM",
    "GD","TFC","EMR","ETN","FCX","PSA","ADP","SRE","ROP","CMG",
    "CSX","MPC","OXY","AEP","NOC","FDX","KMB","AIG","F","GM"
]

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
st.set_page_config(page_title="RSI Screener", layout="wide")
st.title("📉 S&P 500 RSI Screener (Top 150)")
st.caption("14-Day RSI • Live Yahoo Finance Data")

run = st.button("🚀 Run Scanner")

if run:
    results = []
    progress = st.progress(0)

    for i, ticker in enumerate(SP500_150):
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
            continue

        progress.progress((i + 1) / len(SP500_150))

    df = pd.DataFrame(results)

    if df.empty:
        st.error("No data fetched. Check internet or Yahoo Finance limits.")
        st.stop()

    df = df.sort_values("RSI")

    st.success("Scan complete")

    col1, col2, col3 = st.columns(3)
    col1.metric("Oversold (<30)", len(df[df["RSI"] < 30]))
    col2.metric("Neutral (30–70)", len(df[(df["RSI"] >= 30) & (df["RSI"] <= 70)]))
    col3.metric("Overbought (>70)", len(df[df["RSI"] > 70]))

    st.dataframe(df, use_container_width=True)
