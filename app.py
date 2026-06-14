import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# ---------------------------
# Indicators
# ---------------------------
def add_indicators(df):

    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()

    df['Vol_SMA_20'] = df['Volume'].rolling(20).mean()

    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (tp * df['Volume']).cumsum() / df['Volume'].cumsum()

    delta = df['Close'].diff()

    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df


# ---------------------------
# NSE Stocks
# ---------------------------
NSE_TOP_STOCKS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "ICICIBANK",
    "INFY",
    "ITC",
    "SBIN",
    "LT",
    "AXISBANK",
    "KOTAKBANK",
    "BAJFINANCE",
    "ASIANPAINT",
    "MARUTI",
    "SUNPHARMA",
    "ULTRACEMCO",
    "NTPC",
    "POWERGRID",
    "TITAN",
    "TATAMOTORS",
    "WIPRO",
    "HCLTECH",
    "TECHM",
    "INDUSINDBK",
    "NESTLEIND",
    "HINDUNILVR",
    "ONGC",
    "COALINDIA",
    "ADANIPORTS",
    "BAJAJFINSV",
    "JSWSTEEL",
    "TATASTEEL",
    "CIPLA",
    "GRASIM",
    "EICHERMOT",
    "BRITANNIA",
    "SHRIRAMFIN",
    "HEROMOTOCO",
    "DRREDDY",
    "APOLLOHOSP",
    "HDFCLIFE",
    "SBILIFE",
    "BPCL",
    "ADANIENT",
    "DIVISLAB",
    "TRENT",
    "PIDILITIND",
    "DABUR",
    "GODREJCP",
    "INDIGO"
]

# ---------------------------
# UI
# ---------------------------
st.set_page_config(
    page_title="NSE Stock Scanner",
    layout="wide"
)

st.title("📈 NSE Breakout & Reversal Scanner")

strategy = st.radio(
    "Select Strategy",
    ["Breakout", "Reversal", "Both"],
    horizontal=True
)

# ---------------------------
# Scanner
# ---------------------------
if st.button("🚀 Start Scan"):

    results = []

    progress = st.progress(0)

    for i, stock in enumerate(NSE_TOP_STOCKS):

        progress.progress((i + 1) / len(NSE_TOP_STOCKS))

        symbol = stock + ".NS"

        try:

            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                auto_adjust=True,
                progress=False
            )

            if df.empty:
                continue

            if len(df) < 220:
                continue

            df = add_indicators(df)

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # -------------------
            # Breakout
            # -------------------
            if strategy in ["Breakout", "Both"]:

                vol_spike = (
                    latest["Volume"]
                    > 1.5 * latest["Vol_SMA_20"]
                )

                breakout = (
                    prev["Close"] < prev["SMA_50"]
                    and latest["Close"] > latest["SMA_50"]
                    and latest["Close"] > latest["VWAP"]
                    and vol_spike
                )

                if breakout:

                    results.append({
                        "Type": "Breakout",
                        "Symbol": stock,
                        "Price": round(float(latest["Close"]), 2),
                        "RSI": round(float(latest["RSI"]), 2),
                        "SL": round(float(df["Low"].tail(5).min()), 2),
                        "Target": round(float(latest["Close"] * 1.04), 2)
                    })

            # -------------------
            # Reversal
            # -------------------
            if strategy in ["Reversal", "Both"]:

                reversal = (
                    prev["RSI"] < 30
                    and latest["RSI"] > 30
                    and latest["Close"] > latest["SMA_200"]
                )

                if reversal:

                    results.append({
                        "Type": "Reversal",
                        "Symbol": stock,
                        "Price": round(float(latest["Close"]), 2),
                        "RSI": round(float(latest["RSI"]), 2),
                        "SL": round(float(latest["Close"] * 0.96), 2),
                        "Target": round(float(latest["Close"] * 1.05), 2)
                    })

        except Exception:
            continue

    # ---------------------------
    # Output
    # ---------------------------
    if results:

        result_df = pd.DataFrame(results)

        st.success(
            f"✅ Scan Complete - {len(result_df)} Setups Found"
        )

        st.dataframe(
            result_df,
            use_container_width=True
        )

        csv = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download CSV",
            csv,
            "scanner_results.csv",
            "text/csv"
        )

    else:
        st.info("No matching stocks found.")
