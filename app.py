import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Advance Swing Scanner", layout="centered")
st.title("📊 Strong Fundamental Reversal Scanner")
st.write("DMA, VWAP, RSI (30-40), Volume Spike aur Fundamentals ke basis par.")

# Watchlist 
watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "SBIN.NS"]

# Khud ka RSI formula (Bina kisi extra library ke)
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if st.button("🔍 Start Advanced Scan"):
    with st.spinner('Fundamentals aur Technicals scan ho rahe hain... (Isme 1-2 minute lag sakte hain)'):
        selected_stocks = []
        
        for ticker in watchlist:
            try:
                # 1. Fundamental Check 
                ticker_obj = yf.Ticker(ticker)
                info = ticker_obj.info
                roe = info.get('returnOnEquity', 0) or 0
                debt_eq = info.get('debtToEquity', 100) or 100
                
                if roe < 0.10 or debt_eq > 150: 
                    continue 
                    
                # 2. Technical Data Fetch
                df = yf.download(ticker, period="6mo", interval="1d", progress=False)
                if len(df) < 50:
                    continue
                    
                # Pure Pandas Calculations (No pandas_ta needed)
                df['DMA_20'] = df['Close'].rolling(window=20).mean()
                df['DMA_50'] = df['Close'].rolling(window=50).mean()
                df['RSI'] = calculate_rsi(df['Close'], 14)
                df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()
                
                # VWAP Calculation
                df['Typ_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
                df['VWAP'] = (df['Typ_Price'] * df['Volume']).rolling(window=14).sum() / df['Volume'].rolling(window=14).sum()
                
                # Aaj ki (Latest) values
                latest_close = float(df['Close'].iloc[-1])
                dma20 = float(df['DMA_20'].iloc[-1])
                dma50 = float(df['DMA_50'].iloc[-1])
                rsi = float(df['RSI'].iloc[-1])
                vol = float(df['Volume'].iloc[-1])
                vol_sma = float(df['Vol_SMA'].iloc[-1])
                vwap = float(df['VWAP'].iloc[-1])
                
                # --- STRATEGY CONDITIONS ---
                cond_rsi = 28 <= rsi <= 45
                cond_vol = vol > (vol_sma * 1.5)
                cond_dma = (latest_close >= dma20 * 0.97) and (latest_close >= dma50 * 0.97)
                cond_vwap = (latest_close >= vwap * 0.98)
                
                if cond_rsi and cond_vol and cond_dma and cond_vwap:
                    selected_stocks.append({
                        "Stock": ticker.replace(".NS", ""),
                        "Price (₹)": round(latest_close, 2),
                        "RSI": round(rsi, 2),
                        "ROE (%)": round(roe * 100, 2)
                    })
            except Exception as e:
                pass
        
        # Result Show
        if len(selected_stocks) > 0:
            st.success("✅ Perfect Match Found! Ye rahe aapke stocks:")
            st.table(pd.DataFrame(selected_stocks))
        else:
            st.warning("⚠️ Aaj market me kisi stock me ye saari conditions match nahi ho rahi hain.")
            
