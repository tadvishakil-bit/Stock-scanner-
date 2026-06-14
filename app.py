import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="Advance Swing Scanner", layout="centered")
st.title("📊 Strong Fundamental Reversal Scanner")
st.write("DMA, VWAP, RSI (30-40), Volume Spike aur Fundamentals ke basis par.")

# Watchlist - Isme aap aur bhi Nifty 50/500 ke stocks add kar sakte hain
watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "SBIN.NS"]

if st.button("🔍 Start Advanced Scan"):
    with st.spinner('Fundamentals aur Technicals scan ho rahe hain... (Isme 1-2 minute lag sakte hain)'):
        selected_stocks = []
        
        for ticker in watchlist:
            try:
                # 1. Fundamental Check Karna (ROE acha ho, Udhaari/Debt kam ho)
                ticker_obj = yf.Ticker(ticker)
                stock_info = ticker_obj.info
                roe = stock_info.get('returnOnEquity', 0)
                debt_eq = stock_info.get('debtToEquity', 100) # Default high debt if data missing
                
                if roe is None: roe = 0
                if debt_eq is None: debt_eq = 100
                
                # Agar ROE 10% se kam hai ya Debt zyada hai, toh stock reject kar do
                if roe < 0.10 or debt_eq > 150: 
                    continue 
                    
                # 2. Technical Data Fetch Karna
                df = yf.download(ticker, period="6mo", interval="1d", progress=False)
                if len(df) < 50:
                    continue
                    
                # Indicators lagana
                df['DMA_20'] = ta.sma(df['Close'], length=20)
                df['DMA_50'] = ta.sma(df['Close'], length=50)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['Vol_SMA'] = ta.sma(df['Volume'], length=20)
                
                # VWAP Calculation (Price x Volume / Total Volume)
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
                
                # --- AAPKI STRATEGY KI CONDITIONS ---
                
                # Rule 1: RSI 29, 30, 40 ke aas-paas ho (Humne 28 se 45 ki range li hai)
                cond_rsi = 28 <= rsi <= 45
                
                # Rule 2: Volume me spike ho (Average se 1.5x guna zyada volume ho)
                cond_vol = vol > (vol_sma * 1.5)
                
                # Rule 3: Price DMA 20 aur 50 ke upar ho YA cross karne ke nazdeek ho (3% ke andar ho)
                cond_dma = (latest_close >= dma20 * 0.97) and (latest_close >= dma50 * 0.97)
                
                # Rule 4: Price VWAP ke upar ho YA nazdeek ho
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
        
        # Result Show Karna
        if len(selected_stocks) > 0:
            st.success("✅ Perfect Match Found! Ye rahe aapke stocks:")
            st.table(pd.DataFrame(selected_stocks))
        else:
            st.warning("⚠️ Aaj market me kisi stock me ye saari conditions match nahi ho rahi hain.")
              
