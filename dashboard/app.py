import streamlit as st

st.set_page_config(
    page_title="Energy Sentinel",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ Energy Sentinel")
st.subheader("Household Energy Monitoring & Appliance Anomaly Detection")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Energy (2013)", value="3,206 kWh")

with col2:
    st.metric(label="Daily Average", value="8.79 kWh")

with col3:
    st.metric(label="Peak Power", value="6,138 W")

with col4:
    st.metric(label="Appliances Monitored", value="7")

st.markdown("---")

st.markdown("""
### Navigation
Use the sidebar to navigate between sections:

- **Monitoring** — Total energy consumption and trends
- **Appliance Health** — Anomaly detection and risk levels
- **Analytics** — Usage patterns and peak hours
- **Recommendations** — Actionable insights
""")