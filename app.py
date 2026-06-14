import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import io

st.set_page_config(page_title="Pro Scanner", layout="wide")
st.title("🎯 Pro Hybrid Scanner")

# URL Fix: NSE list links
index_urls = {
    "Nifty 500": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
    "Nifty Midcap 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "Nifty Smallcap 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
}

mode = st.radio("Mode:", ("Technical (Online)", "Breakout (Offline)"), horizontal=True)
category = st.selectbox("Select Index:", list(index_urls.keys()))

if st.button("🚀 Scan"):
    try:
        # Index download
        df_list = pd.read_csv(index_urls[category])
        symbols = [s + ".NS" for s in df_list['Symbol'].tolist()[:50]]
        
        if mode == "Technical (Online)":
            results = []
            progress_bar = st.progress(0)
            
            for i, sym in enumerate(symbols):
                progress_bar.progress((i+1)/len(symbols))
                try:
                    # Single stock download is safer than bulk for cloud hosting
                    df = yf.download(sym, period="1y", progress=False)
                    if len(df) < 60: continue
                    
                    latest = df.iloc[-1]
                    sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                    
                    if abs((latest['Close'] - sma_50)/sma_50) < 0.05:
                        results.append({'Symbol': sym.replace('.NS',''), 'Price': round(latest['Close'], 2)})
                except: continue
            
            st.dataframe(pd.DataFrame(results))
        
        else: # Offline Mode
            date = pd.Timestamp.now().strftime("%d%b%Y").upper()
            url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date}.csv"
            # NSE Bhavcopy URL ka structure din ke hisab se badalta hai, ye check karein
            st.write("Fetching Bhavcopy from:", url)
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                bhav = pd.read_csv(io.StringIO(r.text))
                st.dataframe(bhav.head())
            else:
                st.error("Bhavcopy file nahi mili. Aaj holiday ho sakta hai ya file link galat hai.")

    except Exception as e:
        st.error(f"Error: {e}")
        
