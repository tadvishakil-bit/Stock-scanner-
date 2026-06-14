# Sirf is function ko replace karein, baki pura code wahi rahega
@st.cache_data(ttl=86400)
def get_stocks(category):
    urls = {
        "Nifty 500 (Top 50)": "https://niftyindices.com/IndexConstituent/ind_nifty500list.csv",
        "Midcap (Top 50)": "https://niftyindices.com/IndexConstituent/ind_niftymidcap100list.csv",
        "Smallcap (Top 50)": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap100list.csv"
    }
    df = pd.read_csv(urls[category])
    # Yahan .head(50) kar diya hai
    return [s + ".NS" for s in df['Symbol'].head(50).tolist()]
    
