import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# --- FUNCTION: Get Stock List ---
@st.cache_data(ttl=86400)
def get_stock_list(category):
    urls = {
        "Large Cap (Nifty 100)": "https://niftyindices.com/IndexConstituent/ind_nifty100list.csv",
        "Midcap (Nifty 150)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
        "Smallcap (Nifty 250)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
    }
    df = pd.read_csv(urls[category])
    return [s + ".NS" for s in df['Symbol'].head(100).tolist()]

# --- FUNCTION: Telegram Alert ---
def send_telegram_msg(message):
    try:
        token = st.secrets["TOKEN"]
        chat_id = st.secrets["CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url, timeout=5)
    except:
        pass

# --- APP UI ---
st.set_page_config(page_title="Pro Algo Scanner", layout="wide")
st.title("🎯 Pro Algo Swing Scanner")

category = st.radio("Select Index:", ("Large Cap (Nifty 100)", "Midcap (Nifty 150)", "Smallcap (Nifty 250)"), horizontal=True)
strategy = st.radio("Select Strategy:", ("Reversal & Trend Start", "52-Week Breakout"), horizontal=True)

# --- SCANNER ENGINE ---
if st.button("🚀 Run Algorithm"):
    stocks = get_stock_list(category)
    results = []
    
    # Progress Setup
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_stocks = len(stocks)
    
    batch_size = 20
    for i in range(0, total_stocks, batch_size):
        batch = stocks[i:i + batch_size]
        
        # Percentage Calculation & Status Update
        percentage = int(((i + len(batch)) / total_stocks) * 100)
        status_text.text(f"Scanning: {percentage}% complete ({i+1} to {min(i + batch_size, total_stocks)} of {total_stocks} stocks)")
        progress_bar.progress(percentage / 100)
        
        data = yf.download(batch, period="1y", group_by="ticker", progress=False)
        
        for symbol in batch:
            try:
                df = data[symbol].dropna()
                latest = df.iloc[-1]
                
                # Indicators
                sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                vol_sma_20 = df['Volume'].rolling(20).mean().iloc[-1]
                vwap = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
                vwap_val = vwap.iloc[-1]
                
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                
                dist_from_sma50 = round(((latest['Close'] - sma_50) / sma_50) * 100, 2)
                vol_spike = latest['Volume'] > (1.5 * vol_sma_20)
                
                # Strategy Logic
                if strategy == "Reversal & Trend Start":
                    if (rsi < 45) and (abs(latest['Close'] - vwap_val)/vwap_val < 0.02) and vol_spike:
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2), 'Dist_SMA50_%': dist_from_sma50, 'Vol_Spike': 'Yes'})
                        send_telegram_msg(f"✅ Trend Start: {symbol.replace('.NS','')}")
                
                elif strategy == "52-Week Breakout":
                    high_52w = df['High'].rolling(252).max().iloc[-1]
                    if (latest['Close'] >= high_52w * 0.98) and vol_spike:
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2), 'Dist_SMA50_%': dist_from_sma50, 'Vol_Spike': 'Yes'})
                        send_telegram_msg(f"🚀 Breakout: {symbol.replace('.NS','')}")
            except:
                continue
                        
