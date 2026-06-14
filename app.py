import streamlit as st
import pandas as pd
import yfinance as yf
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ultimate Swing Scanner", layout="wide")
st.title("🎯 Pro Algo Swing Scanner")

# --- FUNCTIONS ---
@st.cache_data(ttl=86400)
def get_stock_list(category):
    urls = {
        "Large Cap (Nifty 100)": "https://niftyindices.com/IndexConstituent/ind_nifty100list.csv",
        "Midcap (Nifty 150)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
        "Smallcap (Nifty 250)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
    }
    df = pd.read_csv(urls[category])
    return [s + ".NS" for s in df['Symbol'].head(50).tolist()] # Limit 50 for speed

# --- UI ELEMENTS ---
category = st.radio("Select Index:", ("Large Cap (Nifty 100)", "Midcap (Nifty 150)", "Smallcap (Nifty 250)"), horizontal=True)
strategy = st.radio("Select Strategy:", ("RSI < 30 & 50DMA Support", "52-Week Breakout + Vol Spike"), horizontal=True)

# --- SCANNER LOGIC ---
if st.button("🚀 Run Scan"):
    stocks = get_stock_list(category)
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_stocks = len(stocks)
    
    batch_size = 10 
    for i in range(0, total_stocks, batch_size):
        batch = stocks[i:i + batch_size]
        progress = (i + len(batch)) / total_stocks
        progress_bar.progress(progress)
        status_text.markdown(f"**Scanning:** {int(progress * 100)}% complete")
        
        try:
            data = yf.download(batch, period="1y", group_by="ticker", progress=False)
            
            for symbol in batch:
                try:
                    # Data validation
                    if symbol not in data.columns.levels[1]: continue
                    df = data[symbol].dropna()
                    if len(df) < 60: continue # Data kam hai toh skip karein
                    
                    latest = df.iloc[-1]
                    prev_vol = df['Volume'].rolling(20).mean().iloc[-1]
                    
                    if strategy == "RSI < 30 & 50DMA Support":
                        sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                        
                        if rsi < 35 and abs((latest['Close'] - sma_50)/sma_50) < 0.05:
                            results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2)})

                    elif strategy == "52-Week Breakout + Vol Spike":
                        high_52w = df['High'].rolling(252).max().iloc[-1]
                        if latest['Close'] >= high_52w * 0.95 and latest['Volume'] > prev_vol:
                            results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'Type': 'Breakout'})
                except:
                    continue
        except:
            continue
            
    progress_bar.progress(1.0)
    status_text.markdown("**✅ Scan Completed!**")
    
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("No matching stocks found. Try changing the Index or Strategy.")
        
