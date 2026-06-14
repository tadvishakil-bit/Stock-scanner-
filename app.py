import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import io
import datetime
import time

st.set_page_config(page_title="Ultimate Hybrid Scanner", layout="wide")
st.title("🎯 Pro Hybrid Swing Scanner")

mode = st.radio("Select Mode:", ("Technical (Online - DMA/RSI/VWAP)", "Breakout (Offline - Bhavcopy)"), horizontal=True)
category = st.selectbox("Select Index:", ["Nifty 500", "Nifty Midcap 150", "Nifty Smallcap 250"])

if st.button("🚀 Run Scan"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    # --- ONLINE MODE (Technical Indicators) ---
    if mode == "Technical (Online - DMA/RSI/VWAP)":
        index_urls = {"Nifty 500": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
                      "Nifty Midcap 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
                      "Nifty Smallcap 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"}
        df_list = pd.read_csv(index_urls[category])
        symbols = [s + ".NS" for s in df_list['Symbol'].tolist()[:30]] # 30 stocks for speed
        
        for i, sym in enumerate(symbols):
            progress = (i + 1) / len(symbols)
            progress_bar.progress(progress)
            status_text.markdown(f"**Scanning Technicals:** {int(progress * 100)}% ({sym})")
            
            try:
                df = yf.download(sym, period="1y", progress=False)
                if len(df) < 60: continue
                
                latest = df.iloc[-1]
                sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                
                # RSI Calculation
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                
                # Logic: 50DMA Support + RSI Oversold
                if abs((latest['Close'] - sma_50)/sma_50) < 0.03 and rsi < 40:
                    results.append({'Symbol': sym.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2)})
            except: continue

    # --- OFFLINE MODE (Bhavcopy Breakout) ---
    else:
        status_text.markdown("**Downloading Bhavcopy...**")
        date = datetime.datetime.now().strftime("%d%m%Y")
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date}.csv"
        try:
            bhav = pd.read_csv(io.StringIO(requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text))
            progress_bar.progress(50)
            
            # Logic: Price > Prev Close by 5%
            bhav['CLOSE'] = pd.to_numeric(bhav['CLOSE'], errors='coerce')
            bhav['PREV_CLOSE'] = pd.to_numeric(bhav['PREV_CLOSE'], errors='coerce')
            results = bhav[bhav['CLOSE'] > bhav['PREV_CLOSE'] * 1.05][['SYMBOL', 'CLOSE', 'PREV_CLOSE']]
            progress_bar.progress(100)
        except: 
            st.error("Bhavcopy not available yet. Try after market hours.")

    status_text.markdown("**✅ Scan Completed!**")
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("No matching stocks found.")
        
