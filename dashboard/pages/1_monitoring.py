import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Monitoring", page_icon="📊", layout="wide")

API_BASE = "http://127.0.0.1:8000"

st.title("📊 Energy Monitoring")
st.markdown("---")

# --- Summary Section ---
st.subheader("Energy Summary")

try:
    response = requests.get(f"{API_BASE}/monitoring/summary")
    summary = response.json()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Energy (kWh)", f"{summary['total_energy_kwh']:,.2f}")
    with col2:
        st.metric("Daily Average (kWh)", f"{summary['avg_daily_kwh']:,.2f}")
    with col3:
        st.metric("Peak Power (W)", f"{summary['peak_power_watts']:,.2f}")
    with col4:
        st.metric("Avg Power (W)", f"{summary['avg_power_watts']:,.2f}")

except Exception as e:
    st.error(f"Could not fetch summary: {e}")

st.markdown("---")

# --- Monthly Trend ---
st.subheader("Monthly Average Power Consumption")

try:
    response = requests.get(f"{API_BASE}/monitoring/monthly-trend")
    monthly = response.json()

    df_monthly = pd.DataFrame(monthly)
    df_monthly["month"] = pd.to_datetime(df_monthly["month"])
    df_monthly = df_monthly.sort_values("month")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_monthly["month"], df_monthly["avg_power_watts"],
            marker="o", linewidth=2, color="steelblue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg Power (Watts)")
    ax.set_title("Monthly Average Power Consumption — 2013")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Could not fetch monthly trend: {e}")

st.markdown("---")

# --- Appliance Energy Breakdown ---
st.subheader("Appliance Energy Breakdown (kWh)")

try:
    response = requests.get(f"{API_BASE}/monitoring/appliance-breakdown")
    breakdown = response.json()

    df_breakdown = pd.DataFrame(breakdown)
    df_breakdown = df_breakdown.sort_values("total_energy_kwh", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(df_breakdown["appliance"], df_breakdown["total_energy_kwh"],
            color="steelblue")
    ax.set_xlabel("Total Energy (kWh)")
    ax.set_title("Total Energy Consumed per Appliance — 2013")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Could not fetch appliance breakdown: {e}")