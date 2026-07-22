import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Appliance Health", page_icon="🚨", layout="wide")

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

st.title("🚨 Appliance Health")
st.markdown("---")

# --- All Appliances Health Summary ---
st.subheader("Health Summary — All Appliances")

try:
    response = requests.get(f"{API_BASE}/health/summary")
    summary = response.json()

    df_summary = pd.DataFrame(summary)

    def color_status(val):
        if val == "Critical":
            return "background-color: #ff4b4b; color: white"
        elif val == "Warning":
            return "background-color: #ffa500; color: white"
        else:
            return "background-color: #21c354; color: white"

    styled = df_summary.style.applymap(color_status, subset=["overall_status"])
    st.dataframe(styled, use_container_width=True)

except Exception as e:
    st.error(f"Could not fetch health summary: {e}")

st.markdown("---")

# --- Per Appliance Detail ---
st.subheader("Appliance Detail")

selected = st.selectbox("Select Appliance", APPLIANCES)

try:
    response = requests.get(f"{API_BASE}/health/{selected}")
    health = response.json()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", f"{health['total_records']:,}")
    with col2:
        st.metric("Anomalies Detected", f"{health['anomaly_count']:,}")
    with col3:
        st.metric("Anomaly Rate", f"{health['anomaly_pct']}%")

    st.markdown("#### Risk Distribution")
    risk = health["risk_distribution"]
    df_risk = pd.DataFrame(
        list(risk.items()), columns=["Risk Level", "Count"]
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {"Low": "steelblue", "Medium": "orange", "High": "red"}
    bar_colors = [colors.get(r, "gray") for r in df_risk["Risk Level"]]
    ax.bar(df_risk["Risk Level"], df_risk["Count"], color=bar_colors)
    ax.set_title(f"{selected} — Risk Distribution")
    ax.set_ylabel("Count")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("#### Recent Anomalies")
    if health["recent_anomalies"]:
        df_recent = pd.DataFrame(health["recent_anomalies"])
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("No recent anomalies found.")

except Exception as e:
    st.error(f"Could not fetch appliance health: {e}")