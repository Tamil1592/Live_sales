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
# WEATHER API KEY
# -----------------------------
API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=5)
        data = res.json()

        if res.status_code == 200:
            condition = data["weather"][0]["main"]
            temp = data["main"]["temp"]
            return f"{condition} 🌡 {temp}°C"
        else:
            return "No Data"
    except:
        return "API Error"

# -----------------------------
# ALL INDIA STATES -> CITIES
# -----------------------------
STATE_CITY_MAP = {
    "Tamil Nadu": "Chennai",
    "Kerala": "Thiruvananthapuram",
    "Karnataka": "Bengaluru",
    "Maharashtra": "Mumbai",
    "Delhi": "Delhi",
    "West Bengal": "Kolkata",
    "Gujarat": "Ahmedabad",
    "Rajasthan": "Jaipur",
    "Uttar Pradesh": "Lucknow",
    "Bihar": "Patna",
    "Punjab": "Chandigarh",
    "Haryana": "Gurgaon",
    "Telangana": "Hyderabad",
    "Andhra Pradesh": "Amaravati",
    "Madhya Pradesh": "Bhopal",
    "Odisha": "Bhubaneswar",
    "Assam": "Guwahati",
    "Jharkhand": "Ranchi",
    "Uttarakhand": "Dehradun",
    "Himachal Pradesh": "Shimla"
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
# LIVE WEATHER TABLE
# -----------------------------
st.subheader("🌦 Live Indian Weather Dashboard")

weather_rows = []

for state in selected_states:
    city = STATE_CITY_MAP.get(state)
    if city:
        weather_rows.append({
            "State": state,
            "City": city,
            "Weather": get_weather(city)
        })

st.dataframe(pd.DataFrame(weather_rows), use_container_width=True)

# -----------------------------
# LIVE SALES TABLE
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
st.subheader("🌦 Weather Impact on Sales")
weather_df = df.groupby("weather")["price"].sum().reset_index()

st.plotly_chart(px.bar(weather_df, x="weather", y="price", color="weather"), use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.caption(f"🏬 India Mall Analytics System | Updated: {current_time}")
