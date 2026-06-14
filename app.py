import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Advance Swing Scanner", layout="centered")
st.title("📊 Nifty 500 Reversal Scanner")
st.write("DMA, VWAP, RSI (28-45) aur Volume Spike ke basis par super-fast scan.")

# Nifty 500 ke Top Liquid Stocks ki List (Aap isme aur bhi add kar sakte hain)
watchlist = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
    "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS", "HAL.NS", "BEL.NS",
    "IRCTC.NS", "ZOMATO.NS", "JIOFIN.NS", "PAYTM.NS", "TVSMOTOR.NS", "BHEL.NS",
    "DLF.NS", "PNB.NS", "BANKBARODA.NS", "INDIGO.NS", "TRENT.NS", "CHOLAFIN.NS",
    "HDFCAMC.NS", "MUTHOOTFIN.NS", "SRF.NS", "PIIND.NS", "POLYCAB.NS", "DIXON.NS",
    "LUPIN.NS", "AUROPHARMA.NS", "AMBUJACEM.NS", "ACC.NS", "NYKAA.NS", "POLICYBZR.NS",
    "HINDPETRO.NS", "IOC.NS", "GAIL.NS", "SAIL.NS", "VEDL.NS", "NMDC.NS",
    "IDFCFIRSTB.NS", "FEDERALBNK.NS", "BANDHANBNK.NS", "AUBANK.NS", "ABCAPITAL.NS",
    "M&MFIN.NS", "MANAPPURAM.NS", "BOSCHLTD.NS", "CUMMINSIND.NS", "ESCORTS.NS",
    "APOLLOTYRE.NS", "MRF.NS", "ASHOKLEY.NS", "TATACHEM.NS", "COROMANDEL.NS",
    "IGL.NS", "MGL.NS", "GUJGASLTD.NS", "PETRONET.NS", "CONCOR.NS", "MFSL.NS",
    "MAXHEALTH.NS", "SYNGENE.NS", "LAURUSLABS.NS", "IPCALAB.NS", "ALKEM.NS",
    "ASTRAL.NS", "SUPREMEIND.NS", "PAGEIND.NS", "BATAINDIA.NS", "VOLTAS.NS",
    "HAVELLS.NS", "CROMPTON.NS", "WHIRLPOOL.NS", "JUBLFOOD.NS", "DEVYANI.NS",
    "NAUKRI.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "TATAELXSI.NS"
]

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if st.button("🔍 Start Nifty 500 Scan"):
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    selected_stocks = []
    total_stocks = len(watchlist)
    
    for i, ticker in enumerate(watchlist):
        try:
            # Update Progress Bar
            progress_text.text(f"Scanning {ticker} ({i+1}/{total_stocks})... Please wait.")
            progress_bar.progress((i + 1) / total_stocks)
            
            # Technical Data Fetch (Fast)
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if len(df) < 50:
                continue
                
            # Calculations
            df['DMA_20'] = df['Close'].rolling(window=20).mean()
            df['DMA_50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = calculate_rsi(df['Close'], 14)
            df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()
            
            df['Typ_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
            df['VWAP'] = (df['Typ_Price'] * df['Volume']).rolling(window=14).sum() / df['Volume'].rolling(window=14).sum()
            
            latest_close = float(df['Close'].iloc[-1])
            dma20 = float(df['DMA_20'].iloc[-1])
            dma50 = float(df['DMA_50'].iloc[-1])
            rsi = float(df['RSI'].iloc[-1])
            vol = float(df['Volume'].iloc[-1])
            vol_sma = float(df['Vol_SMA'].iloc[-1])
            vwap = float(df['VWAP'].iloc[-1])
            
            # Conditions
            cond_rsi = 28 <= rsi <= 45
            cond_vol = vol > (vol_sma * 1.5)
            cond_dma = (latest_close >= dma20 * 0.97) and (latest_close >= dma50 * 0.97)
            cond_vwap = (latest_close >= vwap * 0.98)
            
            if cond_rsi and cond_vol and cond_dma and cond_vwap:
                selected_stocks.append({
                    "Stock": ticker.replace(".NS", ""),
                    "Price (₹)": round(latest_close, 2),
                    "RSI": round(rsi, 2)
                })
        except Exception as e:
            pass
            
    progress_text.text("Scanning Complete! 🎉")
    
    # Show Results
    if len(selected_stocks) > 0:
        st.success(f"✅ {len(selected_stocks)} Perfect Matches Found!")
        st.table(pd.DataFrame(selected_stocks))
    else:
        st.warning("⚠️ Aaj kisi bhi stock me ye saari conditions match nahi ho rahi hain.")
        
