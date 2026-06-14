import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pytz
import requests
import time

# --- 1. Telegram Alert Function ---
def send_telegram_msg(message):
    token = "8458962752:AAHCcvV-n_BxGN3GgAM827Q_eV8566_-lcA"
    chat_id = "8458962752"
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- 2. Indicators ---
def add_indicators(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# --- 3. Stocks List (Top 50) ---
@st.cache_data(ttl=86400)
def get_stocks(category):
    urls = {
        "Nifty 500 (Top 50)": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
        "Midcap (Top 50)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap100list.csv",
        "Smallcap (Top 50)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap100list.csv"
    }
    df = pd.read_csv(urls[category])
    return [s + ".NS" for s in df['Symbol'].head(50).tolist()]

# --- 4. UI Setup ---
st.set_page_config(page_title="Pro Stock Scanner", layout="wide")
st.title("📈 Pro Swing Trading Scanner")

category = st.radio("Select Index:", ("Nifty 500 (Top 50)", "Midcap (Top 50)", "Smallcap (Top 50)"), horizontal=True)
strategy = st.radio("Strategy:", ("Breakout", "Reversal"), horizontal=True)

# --- 5. Scanning Engine ---
if st.button("🚀 Scan Shuru Karein"):
    stocks = get_stocks(category)
    results = []
    
    with st.spinner("Scanning..."):
        data = yf.download(stocks, period="1y", interval="1d", group_by="ticker", threads=True, progress=False)
        
        for symbol in stocks:
            try:
                df = data[symbol].dropna()
                df = add_indicators(df)
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                if strategy == "Breakout":
                    vol_spike = latest['Volume'] > (1.5 * latest['Vol_SMA_20'])
                    if prev['Close'] < prev['SMA_50'] and latest['Close'] > latest['SMA_50'] and vol_spike and latest['Close'] > latest['VWAP']:
                        sl = round(df['Low'].tail(5).min(), 2)
                        target = round(latest['Close'] * 1.04, 2)
                        msg = f"🚀 Breakout: {symbol.replace('.NS','')}\nPrice: {round(latest['Close'], 2)}"
                        send_telegram_msg(msg)
                        time.sleep(1)
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'SL': sl, 'Target': target})
                
                elif strategy == "Reversal":
                    if prev['RSI'] < 30 and latest['RSI'] > 30 and latest['Close'] > latest['SMA_200']:
                        sl = round(latest['Close'] * 0.96, 2)
                        target = round(latest['Close'] * 1.05, 2)
                        msg = f"🔄 Reversal: {symbol.replace('.NS','')}\nPrice: {round(latest['Close'], 2)}"
                        send_telegram_msg(msg)
                        time.sleep(1)
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'SL': sl, 'Target': target})
            except:
                continue
    
    if results:
        st.success(f"Scan Complete: {len(results)} setups found.")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("No matching stocks found.")
                        
