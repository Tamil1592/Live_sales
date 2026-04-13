import streamlit as st
import pandas as pd
import random
import sqlite3
import plotly.express as px
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pytz

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="India Mega Mall Pulse", layout="wide", page_icon="🏬")

# -----------------------------
# TIMEZONE (INDIA)
# -----------------------------
india_tz = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(india_tz).strftime("%Y-%m-%d %H:%M:%S")

st.title("🏬🇮🇳 India Mega Mall Revenue Pulse")
st.caption(f"🕒 India Time: {current_time}")

# -----------------------------
# WEATHER API KEY (PUT YOUR KEY HERE)
# -----------------------------
API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()
        if res.status_code == 200:
            return data["weather"][0]["main"] + " 🌡 " + str(data["main"]["temp"]) + "°C"
        else:
            return "Unknown"
    except:
        return "No Data"

# -----------------------------
# STATES (simplified city mapping for weather)
# -----------------------------
STATE_CITY_MAP = {
    "Tamil Nadu": "Chennai",
    "Kerala": "Kochi",
    "Karnataka": "Bengaluru",
    "Maharashtra": "Mumbai",
    "Delhi": "Delhi",
    "West Bengal": "Kolkata",
    "Gujarat": "Ahmedabad",
    "Rajasthan": "Jaipur"
}

ALL_STATES = list(STATE_CITY_MAP.keys())

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("⚙️ Settings Panel")

selected_states = st.sidebar.multiselect(
    "Select States",
    ALL_STATES,
    default=ALL_STATES
)

enable_auto_sales = st.sidebar.toggle("Enable Auto Sales", value=True)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("mall.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
id INTEGER PRIMARY KEY AUTOINCREMENT,
time TEXT,
product TEXT,
category TEXT,
price INTEGER,
state TEXT,
weather TEXT
)
""")
conn.commit()

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=20000, key="refresh")

# -----------------------------
# DATA
# -----------------------------
products = ["iPhone", "Samsung TV", "Nike Shoes", "Levi Jeans", "Rolex Watch", "MacBook"]
categories = ["Electronics", "Fashion", "Luxury", "Sports", "Food Court"]

def generate_sale():
    if not selected_states:
        return

    state = random.choice(selected_states)
    city = STATE_CITY_MAP.get(state, "Chennai")
    weather_data = get_weather(city)

    cursor.execute("""
        INSERT INTO sales(time,product,category,price,state,weather)
        VALUES (?,?,?,?,?,?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.choice(categories),
        random.randint(1000, 200000),
        state,
        weather_data
    ))
    conn.commit()

# -----------------------------
# MANUAL + AUTO SALES
# -----------------------------
colA, colB = st.columns(2)

with colA:
    if st.button("➕ Generate One Sale"):
        generate_sale()

with colB:
    if enable_auto_sales:
        generate_sale()

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_sql("SELECT * FROM sales", conn)

# -----------------------------
# KPI
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"₹{df['price'].sum():,}")
col2.metric("🛍 Total Orders", len(df))
col3.metric("🏬 States Covered", df["state"].nunique())

st.divider()

# -----------------------------
# LIVE TABLE
# -----------------------------
st.subheader("🟢 Live Sales Feed")
st.dataframe(df.tail(15), use_container_width=True)

# -----------------------------
# STATE REVENUE
# -----------------------------
st.subheader("🇮🇳 Revenue by State")
state_df = df.groupby("state")["price"].sum().reset_index()

st.plotly_chart(px.bar(state_df, x="state", y="price", color="state"), use_container_width=True)

# -----------------------------
# WEATHER IMPACT
# -----------------------------
st.subheader("🌦 Live Weather Impact on Sales")
weather_df = df.groupby("weather")["price"].sum().reset_index()

st.plotly_chart(px.bar(weather_df, x="weather", y="price", color="weather"), use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.caption(f"🏬 India Mall Analytics System | Updated: {current_time}")
