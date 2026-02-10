import streamlit as st
import requests

st.set_page_config(page_title="AgroXpert", layout="wide")

API_BASE = "http://127.0.0.1:8000"
CROP_ENDPOINT = "/predict/crop"
SOIL_HEALTH_ENDPOINT = "/predict/soil-health"

# 🔹 NEW (DISEASE ENDPOINT – ADDED ONLY)
DISEASE_ENDPOINT = "/predict/disease"

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
        "Soil Health Check",
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
            display_top3(mock_top3(ph))
            return

        if resp.status_code == 200:
            data = resp.json()
            display_top3(data)
        else:
            display_top3(mock_top3(ph))


def display_top3(data):
    recommended = data.get("recommended_crop", "—")
    top3 = data.get("top3", [])
    rationale = data.get("rationale", "")

    st.success(f"✅ Recommended Crop: **{recommended}**")
    if top3:
        for i, entry in enumerate(top3, start=1):
            st.write(
                f"{i}. **{entry.get('crop')}** — {entry.get('probability',0)*100:.1f}%"
            )
    if rationale:
        st.info(rationale)


# --------------------------
# Fertilizer Recommendation
# --------------------------
def page_fertilizer_recommendation():
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
            "Barley",
            "Cotton",
            "Ground Nuts",
            "Maize",
            "Millets",
            "Oil seeds",
            "Paddy",
            "Pulses",
            "Sugarcane",
            "Tobacco",
            "Wheat",
            None,
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

        url = API_BASE.rstrip("/") + "/predict/fertilizer"
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            st.success(resp.json().get("recommended_fertilizer"))


# --------------------------
# Yield Prediction
# --------------------------
def page_yield_prediction():
    st.header("📈 Yield Prediction")

    Area = st.text_input("Area", value="India")
    Item = st.text_input("Crop", value="Wheat")
    Year = st.number_input("Year", value=2018)
    rainfall = st.number_input("Rainfall", value=1000.0)
    pesticides = st.number_input("Pesticides", value=1.0)
    temp = st.number_input("Avg Temp", value=22.0)

    if st.button("Predict Yield"):
        payload = {
            "Area": Area,
            "Item": Item,
            "Year": Year,
            "average_rain_fall_mm_per_year": rainfall,
            "pesticides_tonnes": pesticides,
            "avg_temp": temp,
        }

        url = API_BASE.rstrip("/") + "/predict/yield"
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            st.success(resp.json().get("predicted_yield"))


# --------------------------
# Irrigation Scheduler
# --------------------------
def page_irrigation_scheduler():
    st.header("🚰 Irrigation Scheduler")

    soil_moisture = st.number_input("Soil Moisture", value=30.0)
    temperature = st.number_input("Temperature", value=30.0)
    humidity = st.number_input("Humidity", value=50.0)
    rain = st.selectbox("Rain Forecast", ["no", "yes"])
    crop = st.selectbox(
        "Crop",
        [
            "Barley",
            "Cotton",
            "Ground Nuts",
            "Maize",
            "Millets",
            "Oil seeds",
            "Paddy",
            "Pulses",
            "Sugarcane",
            "Tobacco",
            "Wheat",
        ],
    )

    if st.button("Check Irrigation"):
        payload = {
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "rain_forecast": rain,
            "crop_type": crop,
        }

        url = API_BASE.rstrip("/") + "/predict/irrigation"
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            st.success(resp.json().get("irrigation_decision"))


# --------------------------
# Soil Health Check
# --------------------------
def page_soil_health_check():
    st.header("🧪 Soil Health Check")

    N = st.number_input("Nitrogen (N)", value=40.0)
    P = st.number_input("Phosphorus (P)", value=30.0)
    K = st.number_input("Potassium (K)", value=35.0)
    ph = st.number_input("pH", value=6.5)

    if st.button("Check Soil Health"):
        payload = {"N": N, "P": P, "K": K, "ph": ph}
        url = API_BASE.rstrip("/") + SOIL_HEALTH_ENDPOINT
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            st.success(data["soil_health_class"])
            st.metric("Confidence", f"{data['confidence']*100:.1f}%")


# --------------------------
# 🦠 Disease Prediction (NEW – ADDED ONLY)
# --------------------------
def page_disease_prediction():
    st.header("🦠 Plant Disease Detection")
    uploaded_file = st.file_uploader(
        "Upload leaf image", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file and st.button("Predict Disease"):
        url = API_BASE.rstrip("/") + DISEASE_ENDPOINT
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }
        resp = requests.post(url, files=files)
        if resp.status_code == 200:
            data = resp.json()
            st.success(f"Disease: {data['disease']}")
            st.metric("Confidence", f"{data['confidence']*100:.2f}%")


def page_home():
    st.title("Welcome to AgroXpert 🌾")


def page_about():
    st.header("About AgroXpert")


# --------------------------
# Routing
# --------------------------
page = st.session_state.page

if page == "Home":
    page_home()
elif page == "Crop Recommendation":
    page_crop_recommendation()
elif page == "Fertilizer Recommendation":
    page_fertilizer_recommendation()
elif page == "Yield Prediction":
    page_yield_prediction()
elif page == "Disease Detection":
    page_disease_prediction()
elif page == "Irrigation Scheduler":
    page_irrigation_scheduler()
elif page == "Soil Health Check":
    page_soil_health_check()
elif page == "About":
    page_about()
else:
    st.write("Unknown page")
