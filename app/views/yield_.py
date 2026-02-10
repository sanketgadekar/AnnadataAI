import streamlit as st
import requests
from app.core.config import API_BASE, YIELD_ENDPOINT


def render():
    st.header("📈 Yield Prediction")
    st.write("Estimate crop yield based on climate and farming inputs.")

    # --------------------------
    # Inputs
    # --------------------------
    Area = st.text_input("Area / Country", value="India")
    Item = st.text_input("Crop", value="Wheat")
    Year = st.number_input("Year", min_value=1900, max_value=2100, value=2018)
    rainfall = st.number_input(
        "Average Rainfall (mm/year)", min_value=0.0, value=1000.0
    )
    pesticides = st.number_input(
        "Pesticides Used (tonnes)", min_value=0.0, value=1.0
    )
    temp = st.number_input(
        "Average Temperature (°C)", min_value=-10.0, value=22.0
    )

    # --------------------------
    # Action
    # --------------------------
    if st.button("Predict Yield"):
        payload = {
            "Area": Area,
            "Item": Item,
            "Year": int(Year),
            "average_rain_fall_mm_per_year": float(rainfall),
            "pesticides_tonnes": float(pesticides),
            "avg_temp": float(temp),
        }

        url = API_BASE.rstrip("/") + YIELD_ENDPOINT

        try:
            resp = requests.post(url, json=payload, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                raw_yield = data.get("predicted_yield", 0)

                # ----------------------------------------
                # Unit conversion
                # Model output: hectograms per hectare (hg/ha)
                # 1 tonne = 10,000 hg
                # ----------------------------------------
                tonnes_per_hectare = raw_yield / 10000

                st.markdown("## 🌾 Predicted Yield")
                st.success(
                    f"**{tonnes_per_hectare:.2f} tonnes per hectare**"
                )

                # Optional transparency (can remove if you want)
                st.caption(f"(Model output: {raw_yield:.1f} hg/ha)")

            else:
                st.error("❌ Failed to get prediction from API")

        except Exception as e:
            st.error(f"❌ Could not connect to API: {e}")
