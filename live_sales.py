import streamlit as st
import pandas as pd
import random
import sqlite3
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="India Mega Mall Pulse", layout="wide", page_icon="🏬")
st.title("🏬🇮🇳 India Mega Mall Revenue Pulse")

# -----------------------------
# FULL INDIA STATES + UTs
# -----------------------------
ALL_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Lakshadweep", "Delhi", "Puducherry", "Jammu and Kashmir", "Ladakh"
]

# -----------------------------
# SIDEBAR EDIT OPTION
# -----------------------------
st.sidebar.header("⚙️ Settings Panel")

selected_states = st.sidebar.multiselect(
    "Select Active States/UTs",
    ALL_STATES,
    default=ALL_STATES
)

enable_auto_sales = st.sidebar.toggle("Enable Auto Live Sales", value=True)

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

def weather():
    return random.choice(["Sunny ☀️", "Rain 🌧️", "Cloudy ☁️", "Heat 🔥"])

def generate_sale():
    if not selected_states:
        return
    cursor.execute("""
        INSERT INTO sales(time,product,category,price,state,weather)
        VALUES (?,?,?,?,?,?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        random.choice(products),
        random.choice(categories),
        random.randint(1000, 200000),
        random.choice(selected_states),
        weather()
    ))
    conn.commit()

# -----------------------------
# MANUAL CONTROL
# -----------------------------
colA, colB = st.columns(2)

with colA:
    if st.button("➕ Generate One Sale Now"):
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

st.plotly_chart(
    px.bar(state_df, x="state", y="price", color="state"),
    use_container_width=True
)

# -----------------------------
# CATEGORY + WEATHER
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛍 Category Sales")
    cat_df = df.groupby("category")["price"].sum().reset_index()
    st.plotly_chart(px.pie(cat_df, names="category", values="price"), use_container_width=True)

with col2:
    st.subheader("🌦 Weather Impact on Sales")
    weather_df = df.groupby("weather")["price"].sum().reset_index()
    st.plotly_chart(px.bar(weather_df, x="weather", y="price", color="weather"), use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.caption(f"🏬 India Mall Analytics System | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
