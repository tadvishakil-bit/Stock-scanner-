import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pytz
import requests
import time

# Secrets access (Streamlit settings mein save karein)
TOKEN = st.secrets.get("TOKEN", "YOUR_TELEGRAM_TOKEN")
CHAT_ID = st.secrets.get("CHAT_ID", "YOUR_CHAT_ID")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

def add_indicators(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

st.set_page_config(page_title="Pro Stock Scanner", layout="wide")
st.title("📈 Pro Swing Trading Scanner")

category = st.radio("Select Index:", ("Nifty 500 (Top 200)", "Midcap (Top 200)", "Smallcap (Top 200)"), horizontal=True)
strategy = st.radio("Strategy:", ("Breakout", "Reversal"), horizontal=True)

if st.button("🚀 Scan Shuru Karein"):
    # Symbols list (Yahan aap apni list fetch logic rakhein)
    stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'SBIN.NS'] # Example list
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Batch processing to avoid crash
    for i, symbol in enumerate(stocks):
        status_text.text(f"Scanning {symbol} ({i+1}/{len(stocks)})...")
        try:
            df = yf.download(symbol, period="1y", interval="1d", progress=False)
            if not df.empty:
                df = add_indicators(df)
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                if strategy == "Breakout":
                    if prev['Close'] < prev['SMA_50'] and latest['Close'] > latest['SMA_50']:
                        results.append({'Symbol': symbol, 'Price': round(latest['Close'], 2)})
                        send_telegram_msg(f"🚀 Breakout: {symbol}")
        except:
            continue
        progress_bar.progress((i + 1) / len(stocks))

    status_text.text("Scan Complete!")
    if results:
        st.table(pd.DataFrame(results))
    else:
        st.info("No stocks found.")
        
