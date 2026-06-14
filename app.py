import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Nifty 500 Split Scanner", layout="centered")
st.title("⚡ Smart Scanner (Batch-Wise)")
st.write("Server speed badhane ke liye stocks ko 2 hisso me baant diya gaya hai.")

# Batch 1: Pehle Top 100 Stocks
batch_1 = [
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
    "APOLLOTYRE.NS", "MRF.NS", "ASHOKLEY.NS", "TATACHEM.NS", "COROMANDEL.NS"
]

# Batch 2: Baaki ke 100 Stocks
batch_2 = [
    "IGL.NS", "MGL.NS", "GUJGASLTD.NS", "PETRONET.NS", "CONCOR.NS", "MFSL.NS",
    "MAXHEALTH.NS", "SYNGENE.NS", "LAURUSLABS.NS", "IPCALAB.NS", "ALKEM.NS",
    "ASTRAL.NS", "SUPREMEIND.NS", "PAGEIND.NS", "BATAINDIA.NS", "VOLTAS.NS",
    "HAVELLS.NS", "CROMPTON.NS", "WHIRLPOOL.NS", "JUBLFOOD.NS", "DEVYANI.NS",
    "NAUKRI.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "TATAELXSI.NS",
    "RECLTD.NS", "PFC.NS", "IDBI.NS", "YESBANK.NS", "UNIONBANK.NS", "CANBK.NS",
    "INDIANB.NS", "UCOBANK.NS", "CENTRALBK.NS", "MAHABANK.NS", "SUZLON.NS",
    "IREDA.NS", "NHPC.NS", "SJVN.NS", "HUDCO.NS", "NBCC.NS", "ENGINERSIN.NS",
    "COCHINSHIP.NS", "MAZDOCK.NS", "GRSE.NS", "BDL.NS", "BEML.NS", "CGPOWER.NS",
    "KAYNES.NS", "IDEA.NS", "INDHOTEL.NS", "OBEROIRLTY.NS", "GODREJPROP.NS",
    "PRESTIGE.NS", "BRIGADE.NS", "SOBHA.NS", "LODHA.NS", "MCX.NS", "CDSL.NS",
    "BSE.NS", "ANGELONE.NS", "MOTILALOFS.NS", "IEX.NS", "TATACOMM.NS", "BHARATFORG.NS",
    "SONACOMS.NS", "MOTHERSON.NS", "BALKRISIND.NS", "GLENMARK.NS", "BIOCON.NS",
    "GRANULES.NS", "ZYDUSLIFE.NS", "TORNTPHARM.NS", "FORTIS.NS", "MEDANTA.NS",
    "AWL.NS", "PATANJALI.NS", "RADICO.NS", "UBL.NS", "ABFRL.NS", "MANYAVAR.NS",
    "METROBRAND.NS", "CAMPUS.NS", "RELAXO.NS", "VBL.NS", "DEEPAKNTR.NS", "NAVINFLUOR.NS",
    "AARTIIND.NS", "ATUL.NS", "TATAINVEST.NS", "BAJAJHLDNG.NS"
]

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_fundamentals(ticker):
    try:
        info = yf.Ticker(ticker).info
        roe = info.get('returnOnEquity', 0) or 0
        debt_eq = info.get('debtToEquity', 100) or 100
        if roe >= 0.10 and debt_eq <= 150:
            return True
        return False
    except:
        return False

st.markdown("---")

# 🗂 BATCH SELECT KARNE KA OPTION
batch_choice = st.selectbox(
    "📂 Kaunsa Batch Scan Karna Hai?",
    ["Batch 1 (Top 100 Stocks)", "Batch 2 (Next 100 Midcaps)"]
)

if batch_choice == "Batch 1 (Top 100 Stocks)":
    current_watchlist = batch_1
else:
    current_watchlist = batch_2

# 🔘 STRATEGY OPTION
strategy = st.radio(
    "⚙️ Aapko kaunsa Scanner use karna hai?",
    ["📉 1. Only RSI Reversal Scanner", "🚀 2. Only Breakout Scanner"]
)
st.markdown("---")

if st.button("🔍 Start Scanning"):
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    selected_stocks = []
    total_stocks = len(current_watchlist)
    
    for i, ticker in enumerate(current_watchlist):
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
            # SCANNER 1: RSI REVERSAL
            # ==========================================
            if strategy == "📉 1. Only RSI Reversal Scanner":
                df['DMA_20'] = df['Close'].rolling(window=20).mean()
                dma20 = float(df['DMA_20'].iloc[-1])
                
                cond_rsi = 28 <= rsi <= 45
                cond_vol = latest_vol > (vol_sma * 1.5)
                cond_dma = latest_close >= (dma20 * 0.97)
                
                if cond_rsi and cond_vol and cond_dma:
                    if check_fundamentals(ticker):
                        selected_stocks.append({
                            "Stock": ticker.replace(".NS", ""),
                            "Price (₹)": round(latest_close, 2),
                            "RSI": round(rsi, 2),
                            "Type": "RSI Reversal"
                        })
            
            # ==========================================
            # SCANNER 2: BREAKOUT
            # ==========================================
            elif strategy == "🚀 2. Only Breakout Scanner":
                df['20_Day_High'] = df['High'].shift(1).rolling(window=20).max()
                prev_20_high = float(df['20_Day_High'].iloc[-1])
                
                cond_price_breakout = latest_close > prev_20_high
                cond_high_volume = latest_vol > (vol_sma * 1.5)
                cond_rsi_strong = rsi > 60
                
                if cond_price_breakout and cond_high_volume and cond_rsi_strong:
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
    
    if len(selected_stocks) > 0:
        st.success(f"🎉 Perfect Matches Found in {batch_choice}:")
        st.table(pd.DataFrame(selected_stocks))
    else:
        st.warning("⚠️ Is batch me kisi strong fundamental stock me ye setup nahi mila.")
        
