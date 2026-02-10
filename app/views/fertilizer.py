import streamlit as st
import requests
from app.core.config import API_BASE, FERTILIZER_ENDPOINT

def render():
    st.header("🧪 Fertilizer Recommendation")

    Temparature = st.number_input("Temperature (°C)", value=26.0)
    Humidity = st.number_input("Humidity (%)", value=50.0)
    Moisture = st.number_input("Moisture (%)", value=40.0)
    Nitrogen = st.number_input("Nitrogen (N)", value=50.0)
    Potassium = st.number_input("Potassium (K)", value=30.0)
    Phosphorous = st.number_input("Phosphorous (P)", value=20.0)

    Soil_Type = st.selectbox(
        "Soil Type (optional)",
        ["Black", "Clayey", "Loamy", "Red", "Sandy", None],
        index=3,
    )
    Crop_Type = st.selectbox(
        "Crop Type (optional)",
        [
            "Barley","Cotton","Ground Nuts","Maize","Millets",
            "Oil seeds","Paddy","Pulses","Sugarcane","Tobacco","Wheat",None
        ],
        index=8,
    )

    if st.button("Recommend Fertilizer"):
        payload = {
            "Temparature": Temparature,
            "Humidity": Humidity,
            "Moisture": Moisture,
            "Nitrogen": Nitrogen,
            "Potassium": Potassium,
            "Phosphorous": Phosphorous,
        }

        if Soil_Type:
            payload["Soil Type"] = Soil_Type
        if Crop_Type:
            payload["Crop Type"] = Crop_Type

        resp = requests.post(API_BASE + FERTILIZER_ENDPOINT, json=payload)
        if resp.status_code == 200:
            st.success(resp.json().get("recommended_fertilizer"))
