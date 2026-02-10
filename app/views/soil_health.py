import streamlit as st
import requests
from app.core.config import API_BASE, SOIL_HEALTH_ENDPOINT

def render():
    st.header("🧪 Soil Health Check")

    N = st.number_input("Nitrogen (N)", value=40.0)
    P = st.number_input("Phosphorus (P)", value=30.0)
    K = st.number_input("Potassium (K)", value=35.0)
    ph = st.number_input("pH", value=6.5)

    if st.button("Check Soil Health"):
        payload = {"N": N, "P": P, "K": K, "ph": ph}
        resp = requests.post(API_BASE + SOIL_HEALTH_ENDPOINT, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            st.success(data["soil_health_class"])
            st.metric("Confidence", f"{data['confidence']*100:.1f}%")
