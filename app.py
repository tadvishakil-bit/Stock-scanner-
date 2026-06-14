import streamlit as st
import pandas as pd
import yfinance as yf

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ultimate Swing Scanner", layout="wide")
st.title("🎯 Pro Algo Swing Scanner (50 DMA & Breakout)")

# --- FUNCTIONS ---
@st.cache_data(ttl=86400)
def get_stock_list(category):
    urls = {
        "Large Cap (Nifty 100)": "https://niftyindices.com/IndexConstituent/ind_nifty100list.csv",
        "Midcap (Nifty 150)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
        "Smallcap (Nifty 250)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
    }
    df = pd.read_csv(urls[category])
    return [s + ".NS" for s in df['Symbol'].head(100).tolist()]

# --- UI ELEMENTS ---
category = st.radio("Select Index:", ("Large Cap (Nifty 100)", "Midcap (Nifty 150)", "Smallcap (Nifty 250)"), horizontal=True)
strategy = st.radio("Select Strategy:", ("RSI < 30 & 50DMA Support", "52-Week Breakout + Vol Spike"), horizontal=True)

# --- SCANNER LOGIC ---
if st.button("🚀 Run Scan"):
    stocks = get_stock_list(category)
    results = []
    
    # Progress Setup
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_stocks = len(stocks)
    
    batch_size = 20
    for i in range(0, total_stocks, batch_size):
        batch = stocks[i:i + batch_size]
        
        # Percentage Update
        percentage = int(((i + len(batch)) / total_stocks) * 100)
        status_text.text(f"Scanning: {percentage}% complete ({i+1} to {min(i + batch_size, total_stocks)} of {total_stocks})")
        progress_bar.progress(percentage / 100)
        
        data = yf.download(batch, period="1y", group_by="ticker", progress=False)
        
        for symbol in batch:
            try:
                df = data[symbol].dropna()
                latest = df.iloc[-1]
                vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
                
                # --- STRATEGY 1: RSI < 30 & 50 DMA Support ---
                if strategy == "RSI < 30 & 50DMA Support":
                    sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                    
                    if rsi < 30 and abs((latest['Close'] - sma_50)/sma_50) < 0.02 and latest['Volume'] > 1.5 * vol_avg:
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2), 'Condition': 'Oversold Support'})

                # --- STRATEGY 2: 52-Week Breakout + Volume Spike ---
                elif strategy == "52-Week Breakout + Vol Spike":
                    high_52w = df['High'].rolling(252).max().iloc[-1]
                    if latest['Close'] >= high_52w * 0.98 and latest['Volume'] > 1.5 * vol_avg:
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'Condition': 'Breakout'})
            except:
                continue
    
    status_text.text("Scan Completed Successfully!")
    
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("No matching stocks found for selected criteria.")
        
