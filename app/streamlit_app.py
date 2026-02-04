import streamlit as st
import requests

st.set_page_config(page_title="AgroXpert", layout="wide")

API_BASE = "http://127.0.0.1:8000"
CROP_ENDPOINT = "/predict/crop"
SOIL_HEALTH_ENDPOINT = "/predict/soil-health"  # 🔹 NEW

# --- session state for simple navigation ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- left menu visible ---
with st.sidebar:
    st.title("AgroXpert🌾")
    st.write("Your AI-Powered Farming Assistant")
    pages = [
        "Home",
        "Crop Recommendation",
        "Fertilizer Recommendation",
        "Yield Prediction",
        "Disease Detection",
        "Irrigation Scheduler",
        "Soil Health Check",   # 🔹 ALREADY PRESENT
        "About",
    ]
    for p in pages:
        if st.button(p):
            st.session_state.page = p


# --- mock fallback for when API unreachable ---
def mock_top3(ph):
    if ph < 5.8:
        top = [("Paddy", 0.62), ("Maize", 0.25), ("Millet", 0.13)]
    else:
        top = [("Maize", 0.58), ("Soybean", 0.27), ("Wheat", 0.15)]
    return {
        "recommended_crop": top[0][0],
        "top3": [{"crop": c, "probability": p} for c, p in top],
        "rationale": f"Mock rationale for pH={ph}",
    }


# --------------------------
# Crop Recommendation Page
# --------------------------
def page_crop_recommendation():
    st.header("🌱 Crop Recommendation")
    st.write("Fill soil & weather values and click **Recommend Crop**.")

    N = st.number_input("Nitrogen (N)", min_value=0.0, value=20.0)
    P = st.number_input("Phosphorus (P)", min_value=0.0, value=15.0)
    K = st.number_input("Potassium (K)", min_value=0.0, value=100.0)
    temperature = st.number_input("Temperature (°C)", value=25.0)
    humidity = st.number_input("Humidity (%)", value=60.0)
    ph = st.number_input("pH", value=6.5, step=0.1)
    rainfall = st.number_input("Rainfall (mm)", value=50.0)

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
        except Exception:
            st.warning("API unreachable, using mock result")
            display_top3(mock_top3(ph))
            return

        if resp.status_code == 200:
            display_top3(resp.json())
        else:
            display_top3(mock_top3(ph))


def display_top3(data):
    st.success(f"✅ Recommended Crop: **{data.get('recommended_crop')}**")
    for i, entry in enumerate(data.get("top3", []), start=1):
        st.write(f"{i}. {entry['crop']} — {entry['probability']*100:.1f}%")


# --------------------------
# 🔹 SOIL HEALTH CHECK (NEW PAGE – ADD ONLY)
# --------------------------
def page_soil_health_check():
    st.header("🧪 Soil Health Check")
    st.write("Evaluate overall soil health using NPK and pH values.")

    N = st.number_input("Nitrogen (N)", min_value=0.0, value=40.0)
    P = st.number_input("Phosphorus (P)", min_value=0.0, value=30.0)
    K = st.number_input("Potassium (K)", min_value=0.0, value=35.0)
    ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.5, step=0.1)

    if st.button("Check Soil Health"):
        payload = {
            "N": float(N),
            "P": float(P),
            "K": float(K),
            "ph": float(ph),
        }

        url = API_BASE.rstrip("/") + SOIL_HEALTH_ENDPOINT
        st.info(f"Calling API: {url}")
        st.code(payload, language="json")

        try:
            resp = requests.post(url, json=payload, timeout=8)
            st.write("Response status:", resp.status_code)
            st.code(resp.text, language="json")

            if resp.status_code == 200:
                data = resp.json()

                st.success(f"🌱 Soil Health: **{data['soil_health_class']}**")
                st.metric("Confidence", f"{data['confidence']*100:.1f}%")

                st.markdown("### 📊 Class Probabilities")
                for cls, prob in data["class_probabilities"].items():
                    st.write(f"- **{cls}** → {prob*100:.2f}%")

            else:
                st.error("API returned an error.")

        except Exception as e:
            st.error(f"Could not connect to API: {e}")


# --------------------------
# Existing Pages (UNCHANGED)
# --------------------------
def page_home():
    st.title("Welcome to AgroXpert 🌾")
    st.write("Use the left menu to open features.")


def page_about():
    st.header("About AgroXpert")
    st.write("AgroXpert is part of AnnadataAI initiative.")


def blank_sanker(name):
    st.header(name)
    st.error("Feature coming soon")


# --------------------------
# Routing (ADD ONE CONDITION ONLY)
# --------------------------
page = st.session_state.page

if page == "Home":
    page_home()
elif page == "Crop Recommendation":
    page_crop_recommendation()
elif page == "Soil Health Check":      # 🔹 NEW
    page_soil_health_check()
elif page == "About":
    page_about()
else:
    blank_sanker(page)
