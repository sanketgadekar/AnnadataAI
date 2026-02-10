import streamlit as st
import requests
from app.core.config import API_BASE, CROP_ENDPOINT
from app.utils.helpers import mock_top3


def render():
    st.header("🌱 Crop Recommendation")
    st.write("Fill soil & weather values and click **Recommend Crop**.")

    # --------------------------
    # Inputs
    # --------------------------
    N = st.number_input("Nitrogen (N)", min_value=0.0, value=20.0)
    P = st.number_input("Phosphorus (P)", min_value=0.0, value=15.0)
    K = st.number_input("Potassium (K)", min_value=0.0, value=100.0)
    temperature = st.number_input("Temperature (°C)", value=25.0)
    humidity = st.number_input("Humidity (%)", value=60.0)
    ph = st.number_input("pH", value=6.5, step=0.1)
    rainfall = st.number_input("Rainfall (mm)", value=50.0)

    # --------------------------
    # Action
    # --------------------------
    if st.button("Recommend Crop"):
        payload = {
            "N": float(N),
            "P": float(P),
            "K": float(K),
            "temperature": float(temperature),
            "humidity": float(humidity),
            "ph": float(ph),
            "rainfall": float(rainfall),
        }

        url = API_BASE.rstrip("/") + CROP_ENDPOINT

        try:
            resp = requests.post(url, json=payload, timeout=8)

            if resp.status_code == 200:
                data = resp.json()
            else:
                data = mock_top3(ph)

        except Exception:
            data = mock_top3(ph)

        # --------------------------
        # Clean UI Output
        # --------------------------
        recommended = data.get("recommended_crop", "—")
        top3 = data.get("top3", [])
        rationale = data.get("rationale", "")

        # Main recommendation
        st.markdown("## 🌾 Recommended Crop")
        st.success(f"**{recommended.capitalize()}**")

        # Other suitable crops (no percentages)
        if top3:
            st.markdown("### 🌱 Other Suitable Crops")

            for item in top3:
                crop = item.get("crop", "—")
                prob = float(item.get("probability", 0))

                col1, col2 = st.columns([2, 5])
                with col1:
                    st.write(f"**{crop.capitalize()}**")
                with col2:
                    st.progress(min(prob, 1.0))

        # Explanation
        if rationale:
            st.info(f"ℹ️ {rationale}")
