import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

API_BASE = "http://127.0.0.1:8000"

APPLIANCES = [
    "Aggregate",
    "Washing Machine",
    "Dishwasher",
    "TV",
    "Kettle",
    "Fridge",
    "Microwave",
]

st.title("📈 Usage Analytics")
st.markdown("---")

selected = st.selectbox("Select Appliance", APPLIANCES)

st.markdown("---")

# --- Hourly Pattern ---
st.subheader("Average Power by Hour of Day")

try:
    response = requests.get(f"{API_BASE}/analytics/hourly-pattern/{selected}")
    hourly = response.json()

    df_hourly = pd.DataFrame(hourly)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_hourly["hour"], df_hourly["avg_power_watts"],
            marker="o", linewidth=2, color="steelblue")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Avg Power (Watts)")
    ax.set_title(f"{selected} — Hourly Usage Pattern")
    ax.set_xticks(range(0, 24, 1))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Could not fetch hourly pattern: {e}")

st.markdown("---")

# --- Weekday vs Weekend ---
st.subheader("Weekday vs Weekend Comparison")

try:
    response = requests.get(f"{API_BASE}/analytics/weekday-vs-weekend/{selected}")
    ww = response.json()

    df_weekday = pd.DataFrame(ww["weekday"])
    df_weekend = pd.DataFrame(ww["weekend"])

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_weekday["hour"], df_weekday["avg_power_watts"],
            linewidth=2, color="steelblue", label="Weekday")
    ax.plot(df_weekend["hour"], df_weekend["avg_power_watts"],
            linewidth=2, color="tomato", linestyle="--", label="Weekend")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Avg Power (Watts)")
    ax.set_title(f"{selected} — Weekday vs Weekend")
    ax.set_xticks(range(0, 24, 1))
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Could not fetch weekday vs weekend data: {e}")

st.markdown("---")

# --- Peak Hour ---
st.subheader("Peak Usage Hour")

try:
    response = requests.get(f"{API_BASE}/analytics/peak-hour/{selected}")
    peak = response.json()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Peak Hour", f"{peak['peak_hour']}:00")
    with col2:
        st.metric("Peak Avg Power", f"{peak['peak_avg_power_watts']} W")

except Exception as e:
    st.error(f"Could not fetch peak hour: {e}")

st.markdown("---")

# --- Daily Activity Rate ---
st.subheader("Daily Activity Rate (% time ON)")

try:
    response = requests.get(f"{API_BASE}/analytics/daily-activity/{selected}")
    activity = response.json()

    df_activity = pd.DataFrame(activity)
    df_activity["date"] = pd.to_datetime(df_activity["date"])

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_activity["date"], df_activity["activity_rate_pct"],
            linewidth=0.8, color="steelblue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Activity Rate (%)")
    ax.set_title(f"{selected} — Daily Activity Rate 2013")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Could not fetch daily activity: {e}")