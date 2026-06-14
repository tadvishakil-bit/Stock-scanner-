import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import time
import datetime
import pytz

# --- 1. Stocks List Fetch Karne Ka Function ---
@st.cache_data(ttl=86400) # Din mein sirf ek baar net se download karega taaki fast rahe
def get_nifty_500_symbols():
    url = "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv"
    try:
        df = pd.read_csv(url)
        symbols = [symbol + ".NS" for symbol in df['Symbol'].tolist()]
        return symbols
    except Exception as e:
        st.error("Nifty 500 ki list load nahi ho payi. Puraani list use karein.")
        return []

# --- 2. Technical Indicators & Setup Logic ---
def check_stock_setup(df, strategy_selected):
    # 200 DMA nikalne ke liye kam se kam 200 din ka data chahiye
    if len(df) < 200:
        return False
        
    # Indicators Calculate Karna
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    df['SMA_200'] = ta.sma(df['Close'], length=200)
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    df['Vol_SMA_20'] = ta.sma(df['Volume'], length=20)
    
    # Latest aur ek din pehle ka data
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Breakout Logic
    if strategy_selected == "Breakout":
        # Kal 50 SMA ke niche tha, Aaj upar aa gaya
        price_breakout = (prev['Close'] < prev['SMA_50']) and (latest['Close'] > latest['SMA_50'])
        # Volume 2x average se zyada hai
        volume_spike = latest['Volume'] > (2 * latest['Vol_SMA_20'])
        
        if price_breakout and volume_spike:
            return True
            
    # Reversal Logic
    elif strategy_selected == "Reversal":
        # RSI 30 ke niche se ghoom kar upar aaya
        rsi_reversal = (prev['RSI_14'] < 30) and (latest['RSI_14'] > 30)
        # Price 200 SMA (long term support) ke upar ho
        above_support = latest['Close'] > latest['SMA_200']
        
        if rsi_reversal and above_support:
            return True

    return False

# --- 3. Streamlit UI (Frontend) ---
st.set_page_config(page_title="Live Stock Scanner", layout="centered")
st.title("📈 Nifty 500 Scanner")

stocks_list = get_nifty_500_symbols()

# Radio Button Strategy Select karne ke liye
strategy_ui = st.radio(
    "Aapko konsa setup scan karna hai?",
    ("Breakout (50 DMA Crossover + Volume)", "Reversal (RSI < 30 Bounce + 200 DMA Support)")
)

# Backend ke liye Strategy ka naam chota kar liya
if "Breakout" in strategy_ui:
    strategy = "Breakout"
else:
    strategy = "Reversal"

# --- 4. Main Scanning Engine ---
if st.button("🚀 Scan Shuru Karein"):
    if len(stocks_list) == 0:
        st.warning("Stocks list khali hai. Internet connection check karein.")
    else:
        with st.spinner(f"Nifty 500 ke saare stocks scan ho rahe hain. Thoda intezaar karein..."):
            
            # 1 saal ka data ek sath download taaki 200 DMA ban sake
            data = yf.download(stocks_list, period="1y", interval="1d", group_by="ticker", threads=True, show_errors=False)
            
            scanned_stocks = []
            
            # Har stock ka loop chalayenge
            for symbol in stocks_list:
                try:
                    # Agar yfinance ne data return kiya hai
                    if symbol in data.columns.levels[0]:
                        df = data[symbol].dropna()
                        if check_stock_setup(df, strategy):
                            # '.NS' hata kar sirf stock ka naam dikhayenge
                            clean_symbol = symbol.replace('.NS', '')
                            scanned_stocks.append(clean_symbol)
                except Exception as e:
                    pass # Kuch stocks delist ho jate hain, unko ignore karega
            
            # Result Print Karna
            if len(scanned_stocks) > 0:
                st.success(f"🎉 Total {len(scanned_stocks)} stocks mile hain ({strategy} setup ke liye):")
                st.write(scanned_stocks)
            else:
                st.info(f"Abhi kisi bhi stock mein {strategy} ka setup nahi ban raha hai.")

# --- 5. Auto-Refresh Logic (Live Market Hours) ---
def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    
    # Monday = 0 se Friday = 4
    if now.weekday() > 4:
        return False
        
    # 9:15 AM se 3:30 PM (15:30)
    market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_start <= now <= market_end

st.markdown("---")
if is_market_open():
    st.info("🟢 Live Market On: Scanner har 5 minute mein apne aap refresh hoga.")
    time.sleep(300) 
    st.rerun() 
else:
    st.warning("🔴 Market abhi closed hai. Auto-refresh off hai.")
        
