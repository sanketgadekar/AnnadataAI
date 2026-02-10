import streamlit as st
import requests
from app.core.config import API_BASE, IRRIGATION_ENDPOINT

def render():
    st.header("🚰 Irrigation Scheduler")

    soil_moisture = st.number_input("Soil Moisture", value=30.0)
    temperature = st.number_input("Temperature", value=30.0)
    humidity = st.number_input("Humidity", value=50.0)
    rain = st.selectbox("Rain Forecast", ["no", "yes"])
    crop = st.selectbox(
        "Crop",
        ["Barley","Cotton","Ground Nuts","Maize","Millets",
         "Oil seeds","Paddy","Pulses","Sugarcane","Tobacco","Wheat"]
    )

    if st.button("Check Irrigation"):
        payload = {
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "rain_forecast": rain,
            "crop_type": crop,
        }

        resp = requests.post(API_BASE + IRRIGATION_ENDPOINT, json=payload)
        if resp.status_code == 200:
            st.success(resp.json().get("irrigation_decision"))
