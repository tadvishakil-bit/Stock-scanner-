import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Stock Scanner", layout="centered")
st.title("⚡ Smart Swing Scanner")
st.write("Apna tool chunein: RSI Reversal ya Volume Breakout.")

# Nifty 500 ke Top Liquid Stocks (Aap isme aur stocks .NS laga kar add kar sakte hain)
watchlist = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "INFY.NS", "ITC.NS", "RELIANCE.NS", "SBIN.NS", "TCS.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "ZOMATO.NS", "JIOFIN.NS", "IRFC.NS", "RVNL.NS", "BHEL.NS", "HAL.NS",
    "LTIM.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "SUNPHARMA.NS",
    "BEL.NS", "DLF.NS", "PNB.NS", "BANKBARODA.NS", "INDIGO.NS", "TRENT.NS", "CHOLAFIN.NS",
    "HDFCAMC.NS", "MUTHOOTFIN.NS", "SRF.NS", "PIIND.NS", "POLYCAB.NS", "DIXON.NS",
    "LUPIN.NS", "AUROPHARMA.NS", "AMBUJACEM.NS", "ACC.NS", "NYKAA.NS", "POLICYBZR.NS"
]

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Fundamental Check Function (Sirf paas hue stocks ke liye)
def check_fundamentals(ticker):
    try:
        info = yf.Ticker(ticker).info
        roe = info.get('returnOnEquity', 0) or 0
        debt_eq = info.get('debtToEquity', 100) or 100
        # Condition: ROE > 10% aur Debt to Equity < 150%
        if roe >= 0.10 and debt_eq <= 150:
            return True
        return False
    except:
        return False

st.markdown("---")
# 🔘 DO SEPARATE SCANNERS KA OPTION
strategy = st.radio(
    "Aapko kaunsa Scanner use karna hai?",
    ["📉 1. Only RSI Reversal Scanner", "🚀 2. Only Breakout Scanner"]
)
st.markdown("---")

if st.button("🔍 Start Scanning"):
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    selected_stocks = []
    total_stocks = len(watchlist)
    
    for i, ticker in enumerate(watchlist):
        try:
            progress_text.text(f"Scanning {ticker} ({i+1}/{total_stocks})...")
            progress_bar.progress((i + 1) / total_stocks)
            
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if len(df) < 50:
                continue
                
            df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()
            df['RSI'] = calculate_rsi(df['Close'], 14)
            
            latest_close = float(df['Close'].iloc[-1])
            latest_vol = float(df['Volume'].iloc[-1])
            vol_sma = float(df['Vol_SMA'].iloc[-1])
            rsi = float(df['RSI'].iloc[-1])
            
            # ==========================================
            # SCANNER 1: ONLY RSI REVERSAL
            # ==========================================
            if strategy == "📉 1. Only RSI Reversal Scanner":
                df['DMA_20'] = df['Close'].rolling(window=20).mean()
                dma20 = float(df['DMA_20'].iloc[-1])
                
                cond_rsi = 28 <= rsi <= 45
                cond_vol = latest_vol > (vol_sma * 1.5)
                cond_dma = latest_close >= (dma20 * 0.97) # DMA ke aas-paas ho
                
                if cond_rsi and cond_vol and cond_dma:
                    # Technical Pass hone par hi Fundamental check karo (Time save!)
                    if check_fundamentals(ticker):
                        selected_stocks.append({
                            "Stock": ticker.replace(".NS", ""),
                            "Price (₹)": round(latest_close, 2),
                            "RSI": round(rsi, 2),
                            "Type": "RSI Reversal"
                        })
            
            # ==========================================
            # SCANNER 2: ONLY BREAKOUT
            # ==========================================
            elif strategy == "🚀 2. Only Breakout Scanner":
                df['20_Day_High'] = df['High'].shift(1).rolling(window=20).max()
                prev_20_high = float(df['20_Day_High'].iloc[-1])
                
                cond_price_breakout = latest_close > prev_20_high
                cond_high_volume = latest_vol > (vol_sma * 1.5)
                cond_rsi_strong = rsi > 60
                
                if cond_price_breakout and cond_high_volume and cond_rsi_strong:
                    # Technical Pass hone par hi Fundamental check karo
                    if check_fundamentals(ticker):
                        selected_stocks.append({
                            "Stock": ticker.replace(".NS", ""),
                            "Price (₹)": round(latest_close, 2),
                            "RSI": round(rsi, 2),
                            "Type": "Breakout"
                        })
                        
        except Exception as e:
            pass
            
    progress_text.text("Scan Complete! ✅")
    
    # Result Dikhana
    if len(selected_stocks) > 0:
        st.success(f"🎉 Perfect Fundamental + Technical Matches Found:")
        st.table(pd.DataFrame(selected_stocks))
    else:
        st.warning("⚠️ Aaj market me kisi strong fundamental stock me ye setup nahi mila.")
        
