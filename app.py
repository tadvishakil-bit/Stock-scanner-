import streamlit as st
import pandas as pd
import requests
import io
import datetime

st.set_page_config(page_title="Offline Bhavcopy Scanner", layout="wide")
st.title("🎯 Offline Bhavcopy Swing Scanner")

# NSE Nifty Index Links
index_urls = {
    "Nifty 500": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
    "Nifty Midcap 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "Nifty Smallcap 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"
}

category = st.radio("Select Index:", list(index_urls.keys()), horizontal=True)

if st.button("🚀 Scan Offline Data"):
    # 1. Download Index List
    try:
        index_df = pd.read_csv(index_urls[category])
        target_symbols = index_df['Symbol'].tolist()
    except:
        st.error("Index list download nahi ho paayi.")
        st.stop()
    
    # 2. Download Bhavcopy (Aaj ki date)
    date = datetime.datetime.now().strftime("%d%m%Y")
    bhav_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date}.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(bhav_url, headers=headers)
        if response.status_code == 200:
            bhav_df = pd.read_csv(io.StringIO(response.text))
            bhav_df.columns = bhav_df.columns.str.strip()
            
            # 3. Filter & Process
            final_df = bhav_df[bhav_df['SYMBOL'].isin(target_symbols)].copy()
            final_df['CLOSE'] = pd.to_numeric(final_df['CLOSE'], errors='coerce')
            final_df['DELIV_QTY'] = pd.to_numeric(final_df['DELIV_QTY'], errors='coerce')
            final_df['TRADED_QTY'] = pd.to_numeric(final_df['TRADED_QTY'], errors='coerce')
            
            # High Delivery Accumulation Logic (>50% Delivery)
            final_df['DELIV_%'] = (final_df['DELIV_QTY'] / final_df['TRADED_QTY']) * 100
            
            results = final_df[final_df['DELIV_%'] > 50][['SYMBOL', 'CLOSE', 'DELIV_%']]
            
            st.success(f"Found {len(results)} potential stocks.")
            st.dataframe(results.sort_values(by='DELIV_%', ascending=False), use_container_width=True)
        else:
            st.warning("Bhavcopy file abhi available nahi hai. Market band hone ke baad try karein.")
    except Exception as e:
        st.error(f"Error: {e}")
        
