import streamlit as st
import pandas as pd
import yfinance as yf

# Function to get Nifty index constituent lists
@st.cache_data(ttl=86400)
def get_stock_list(category):
    urls = {
        "Large Cap (Nifty 100)": "https://niftyindices.com/IndexConstituent/ind_nifty100list.csv",
        "Midcap (Nifty 150)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
        "Smallcap (Nifty 250)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
    }
    df = pd.read_csv(urls[category])
    return [s + ".NS" for s in df['Symbol'].head(100).tolist()]

st.set_page_config(page_title="Pro Algo Scanner", layout="wide")
st.title("🎯 Pro Algo Swing Scanner")

# UI Elements
category = st.radio("Select Index:", ("Large Cap (Nifty 100)", "Midcap (Nifty 150)", "Smallcap (Nifty 250)"), horizontal=True)
strategy = st.radio("Select Strategy:", ("Reversal & Trend Start", "52-Week Breakout"), horizontal=True)

if st.button("🚀 Run Algorithm"):
    stocks = get_stock_list(category)
    results = []
    progress_bar = st.progress(0)
    
    batch_size = 20
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i + batch_size]
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
                
                # RSI Calculation
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                
                # Metrics
                dist_from_sma50 = round(((latest['Close'] - sma_50) / sma_50) * 100, 2)
                vol_spike = latest['Volume'] > (1.5 * vol_sma_20)
                
                # Strategy Logic
                if strategy == "Reversal & Trend Start":
                    # RSI < 45, Near VWAP, Volume Spike
                    if (rsi < 45) and (abs(latest['Close'] - vwap_val)/vwap_val < 0.02) and vol_spike:
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2), 'Dist_SMA50_%': dist_from_sma50, 'Vol_Spike': 'Yes'})
                
                elif strategy == "52-Week Breakout":
                    high_52w = df['High'].rolling(252).max().iloc[-1]
                    # Price near 52w high + Volume Spike
                    if (latest['Close'] >= high_52w * 0.98) and vol_spike:
                        results.append({'Symbol': symbol.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2), 'Dist_SMA50_%': dist_from_sma50, 'Vol_Spike': 'Yes'})
            except:
                continue
        
        progress_bar.progress((i + batch_size) / len(stocks))
    
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("No matching stocks found for selected criteria.")
        
