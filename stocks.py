import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import base64
import os
from dotenv import load_dotenv

# === Load API key from .env file ===
load_dotenv()
API_KEY = os.getenv("COINMARKETCAP_API_KEY")

# === Streamlit Page Setup ===
st.set_page_config(layout="wide")
st.title("💹 Real-Time Cryptocurrency Prices Dashboard")

# === Sidebar Configuration ===
st.sidebar.header("⚙️ Settings")
currency = st.sidebar.selectbox("Currency", ["USD", "INR", "BTC", "ETH"])
limit = st.sidebar.slider("Top N Coins", min_value=10, max_value=100, value=50, step=10)
sort_by = st.sidebar.selectbox("Sort By", ["Price", "Market Cap", "Percent Change (24h)"])

# === CoinMarketCap API Configuration ===
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

@st.cache_data
def load_data():
    headers = {"X-CMC_PRO_API_KEY": API_KEY}
    params = {
        "start": "1",
        "limit": "100",  # Max allowed on free plan
        "convert": currency
    }

    r = requests.get(API_URL, headers=headers, params=params)
    response = r.json()

    # Error Handling
    if r.status_code != 200 or "data" not in response:
        st.error(f"API Error: {response.get('status', {}).get('error_message', 'Unknown error')}")
        st.stop()

    data = response["data"]

    coins = []
    for coin in data:
        quote = coin["quote"][currency]
        coins.append({
            "Name": coin["name"],
            "Symbol": coin["symbol"],
            "Price": quote["price"],
            "Market Cap": quote["market_cap"],
            "Percent Change (24h)": quote["percent_change_24h"],
            "Volume (24h)": quote["volume_24h"]
        })

    return pd.DataFrame(coins)

# === Load and Display Data ===
df = load_data()

# Sort according to user preference
if sort_by == "Price":
    df = df.sort_values("Price", ascending=False)
elif sort_by == "Market Cap":
    df = df.sort_values("Market Cap", ascending=False)
else:
    df = df.sort_values("Percent Change (24h)", ascending=False)

df = df.head(limit)

st.subheader("📋 Cryptocurrency Market Data")
st.dataframe(df)

# === Download CSV File ===
def download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">📥 Download CSV</a>'

st.markdown(download_link(df), unsafe_allow_html=True)

# === Bar Chart ===
st.subheader(f"📊 Bar Chart: {sort_by}")
fig, ax = plt.subplots(figsize=(10, 6))

if sort_by == "Percent Change (24h)":
    colors = ["green" if x > 0 else "red" for x in df["Percent Change (24h)"]]
    ax.barh(df["Symbol"], df["Percent Change (24h)"], color=colors)
    ax.set_xlabel("% Change")
else:
    ax.barh(df["Symbol"], df[sort_by], color="skyblue")
    ax.set_xlabel(sort_by)

ax.set_ylabel("Symbol")
ax.invert_yaxis()
st.pyplot(fig)
