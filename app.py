import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pytz

# 1. Indicators Calculation
def add_indicators(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    # VWAP Calculation
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# 2. Stocks List Fetching
@st.cache_data(ttl=86400)
def get_stocks(category):
    urls = {
        "Nifty 500 (Top 200)": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
        "Midcap (Top 200)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap200list.csv",
        "Smallcap (Top 200)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap200list.csv"
    }
    df = pd.read_csv(urls[category])
    return [s + ".NS" for s in df['Symbol'].head(200).tolist()]

# 3. UI Setup
st.set_page_config(page_title="Pro Stock Scanner", layout="wide")
st.title("📈 Pro Swing Trading Scanner")

category = st.radio("Select Index:", ("Nifty 500 (Top 200)", "Midcap (Top 200)", "Smallcap (Top 200)"), horizontal=True)
strategy = st.radio("Strategy:", ("Breakout", "Reversal"), horizontal=True)

# 4. Main Scanning Engine
if st.button("🚀 Scan Shuru Karein"):
    stocks = get_stocks(category)
    results = []
    
    with st.spinner("Scanning 200 stocks..."):
        data = yf.download(stocks, period="1y", interval="1d", group_by="ticker", threads=True, progress=False)
        
        for symbol in stocks:
            try:
                df = data[symbol].dropna()
                df = add_indicators(df)
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                # Logic: Breakout
                if strategy == "Breakout":
                    vol_spike = latest['Volume'] > (1.5 * latest['Vol_SMA_20'])
                    if prev['Close'] < prev['SMA_50'] and latest['Close'] > latest['SMA_50'] and vol_spike and latest['Close'] > latest['VWAP']:
                        sl = round(df['Low'].tail(5).min(), 2)
                        target = round(latest['Close'] * 1.04, 2)
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'SL': sl, 'Target': target, 'RSI': round(latest['RSI'], 2), 'VWAP': round(latest['VWAP'], 2)})
                
                # Logic: Reversal
                elif strategy == "Reversal":
                    if prev['RSI'] < 30 and latest['RSI'] > 30 and latest['Close'] > latest['SMA_200']:
                        sl = round(latest['Close'] * 0.96, 2)
                        target = round(latest['Close'] * 1.05, 2)
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'SL': sl, 'Target': target, 'RSI': round(latest['RSI'], 2)})
            except:
                continue
    
    if results:
        st.success(f"Setup found: {len(results)} stocks")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)
        st.json(df_results.to_json(orient='records'))
    else:
        st.info("No matching stocks found.")

# 5. Auto-Refresh
import time
if 9 <= datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour < 16:
    st.info("Market is Live. Auto-refreshing in 5 mins...")
    time.sleep(300)
    st.rerun()
    
