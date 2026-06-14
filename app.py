import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import io
import datetime

st.set_page_config(page_title="Ultimate Pro Scanner", layout="wide")
st.title("🎯 Pro Hybrid Scanner (Top 50 Stocks)")

# 1. Index URL Mapping
index_urls = {
    "Nifty 500": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
    "Midcap 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "Smallcap 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
}

mode = st.radio("Select Mode:", ("Technical (Online)", "Breakout (Offline)"), horizontal=True)
category = st.selectbox("Select Index:", list(index_urls.keys()))

if st.button("🚀 Run Scan"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    
    # Load Index List
    df_list = pd.read_csv(index_urls[category])
    # Top 50 Stocks extraction
    symbols = [s + ".NS" for s in df_list['Symbol'].tolist()[:50]]
    
    # --- ONLINE MODE ---
    if mode == "Technical (Online)":
        data = yf.download(symbols, period="1y", group_by="ticker", progress=False)
        for i, sym in enumerate(symbols):
            progress_bar.progress((i + 1) / len(symbols))
            status_text.markdown(f"**Scanning Technicals:** {int(((i+1)/len(symbols))*100)}% - {sym}")
            try:
                df = data[sym].dropna()
                if len(df) < 60: continue
                latest = df.iloc[-1]
                sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                rsi = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean()))).iloc[-1]
                
                if abs((latest['Close'] - sma_50)/sma_50) < 0.03 and rsi < 40:
                    results.append({'Symbol': sym.replace('.NS',''), 'Price': round(latest['Close'], 2), 'RSI': round(rsi, 2)})
            except: continue

    # --- OFFLINE MODE ---
    else:
        status_text.markdown("**Downloading Bhavcopy...**")
        date = datetime.datetime.now().strftime("%d%m%Y")
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date}.csv"
        try:
            bhav = pd.read_csv(io.StringIO(requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text))
            bhav['CLOSE'] = pd.to_numeric(bhav['CLOSE'], errors='coerce')
            bhav['PREV_CLOSE'] = pd.to_numeric(bhav['PREV_CLOSE'], errors='coerce')
            # 5% Breakout Logic
            filtered = bhav[bhav['SYMBOL'].isin([s.replace('.NS','') for s in symbols])]
            results = filtered[filtered['CLOSE'] > filtered['PREV_CLOSE'] * 1.05][['SYMBOL', 'CLOSE']]
            progress_bar.progress(100)
        except: st.error("Bhavcopy not available.")

    status_text.markdown("**✅ Scan Completed!**")
    st.dataframe(pd.DataFrame(results), use_container_width=True)
    
