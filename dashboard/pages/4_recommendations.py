import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Recommendations", page_icon="💡", layout="wide")

API_BASE = "http://127.0.0.1:8000"

st.title("💡 Smart Recommendations")
st.markdown("---")

st.subheader("Actionable Insights Based on Anomaly Detection")

try:
    response = requests.get(f"{API_BASE}/recommendations/")
    recommendations = response.json()

    if not recommendations:
        st.success("All appliances are operating normally. No recommendations at this time.")
    else:
        for rec in recommendations:
            appliance = rec["appliance"]
            anomaly_pct = rec["anomaly_pct"]
            high_risk = rec["high_risk_count"]
            message = rec["recommendation"]

            if anomaly_pct > 10:
                box_type = st.error
                icon = "🔴"
            elif high_risk > 500:
                box_type = st.warning
                icon = "🟠"
            else:
                box_type = st.info
                icon = "🔵"

            with st.container():
                st.markdown(f"### {icon} {appliance}")
                box_type(message)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Anomaly Rate", f"{anomaly_pct}%")
                with col2:
                    st.metric("High Risk Count", f"{high_risk:,}")
                st.markdown("---")

except Exception as e:
    st.error(f"Could not fetch recommendations: {e}")