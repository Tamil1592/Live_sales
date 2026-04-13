import streamlit as st
import pandas as pd
import random
import sqlite3
import plotly.express as px
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="India Mall Pulse", layout="wide")
st.title("🏬🇮🇳 India Mall Revenue Dashboard")

# -----------------------------
# WEATHER API
# -----------------------------
API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()

        if res.status_code == 200:
            return f"{data['weather'][0]['main']} {data['main']['temp']}°C"
        return "No Data"
    except:
        return "Error"

# -----------------------------
# STATES → CITIES
# -----------------------------
STATE_CITY = {
    "Tamil Nadu": "Chennai",
    "Karnataka": "Bengaluru",
    "Kerala": "Kochi",
    "Maharashtra": "Mumbai",
    "Delhi": "Delhi",
    "West Bengal": "Kolkata"
}

states = list(STATE_CITY.keys())

# -----------------------------
# SIDEBAR
# -----------------------------
selected_states = st.sidebar.multiselect("Select States", states, default=states)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("mall.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS sales(
time TEXT,
product TEXT,
price INT,
state TEXT,
weather TEXT
)
""")

# -----------------------------
# DATA
# -----------------------------
products = ["iPhone", "TV", "Shoes", "Jeans", "Laptop"]

def add_sale():
    if not selected_states:
        return

    state = random.choice(selected_states)
    city = STATE_CITY[state]
    weather = get_weather(city)

    c.execute("INSERT INTO sales VALUES (?,?,?,?,?)", (
        datetime.now().strftime("%H:%M:%S"),
        random.choice(products),
        random.randint(1000, 50000),
        state,
        weather
    ))
    conn.commit()

# -----------------------------
# BUTTON
# -----------------------------
if st.button("➕ Add Sale"):
    add_sale()

# Auto sales
if st.checkbox("Auto Sales"):
    add_sale()

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_sql("SELECT * FROM sales", conn)

# -----------------------------
# KPIs
# -----------------------------
col1, col2 = st.columns(2)

col1.metric("💰 Revenue", f"₹{df['price'].sum():,}")
col2.metric("🛍 Orders", len(df))

st.divider()

# -----------------------------
# TABLE
# -----------------------------
st.dataframe(df.tail(10), use_container_width=True)

# -----------------------------
# CHART
# -----------------------------
state_df = df.groupby("state")["price"].sum().reset_index()
st.bar_chart(state_df.set_index("state"))

# -----------------------------
# WEATHER VIEW
# -----------------------------
st.subheader("🌦 Live Weather")

weather_view = []
for s in selected_states:
    weather_view.append({
        "State": s,
        "City": STATE_CITY[s],
        "Weather": get_weather(STATE_CITY[s])
    })

st.dataframe(pd.DataFrame(weather_view))
