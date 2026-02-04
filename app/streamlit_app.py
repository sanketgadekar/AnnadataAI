import streamlit as st
import requests

st.set_page_config(page_title="AgroXpert", layout="wide")



API_BASE = "http://127.0.0.1:8000"  
CROP_ENDPOINT = "/predict/crop"    
SOIL_HEALTH_ENDPOINT = "/predict/soil-health" 

# --- session state for simple navigation ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- left menu visible ---
with st.sidebar:
    st.title("AgroXpert🌾")
    st.write("Your AI-Powered Farming Assistant")
    pages = ["Home", "Crop Recommendation", "Fertilizer Recommendation", "Yield Prediction",
             "Disease Detection", "Irrigation Scheduler",
             "Soil Health Check", "About"]
    for p in pages:
        if st.button(p):
            st.session_state.page = p


# --- mock fallback for when API unreachable ---
def mock_top3(ph):
    if ph < 5.8:
        top = [("Paddy", 0.62), ("Maize", 0.25), ("Millet", 0.13)]
    else:
        top = [("Maize", 0.58), ("Soybean", 0.27), ("Wheat", 0.15)]
    return {"recommended_crop": top[0][0],
            "top3": [{"crop": c, "probability": p} for c, p in top],
            "rationale": f"Mock rationale for pH={ph}"}


# --------------------------
# Crop Recommendation Page
# --------------------------
def page_crop_recommendation():
    st.header("🌱 Crop Recommendation")
    st.write("Fill soil & weather values and click **Recommend Crop**.")

    # inputs
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
        st.info(f"Calling API: {url}")
        try:
            resp = requests.post(url, json=payload, timeout=8)
        except Exception as e:
            st.error(f"Could not connect to API: {e}")
            st.warning("Showing mock recommendation")
            out = mock_top3(ph)
            display_top3(out)
            return

        st.write("Response status code:", resp.status_code)
        st.code(resp.text, language="json")

        if resp.status_code == 200:
            try:
                data = resp.json()
            except Exception:
                st.error("Invalid JSON from API")
                return

            if isinstance(data, str):
                st.success(f"Recommended Crop: **{data}**")
                return

            display_top3(data)
        else:
            st.error("API error — using mock output")
            display_top3(mock_top3(ph))


# Helper to render Top 3 crops
def display_top3(data):
    recommended = data.get("recommended_crop", "—")
    top3 = data.get("top3", [])
    rationale = data.get("rationale", "")

    st.success(f"✅ Recommended Crop: **{recommended}**")
    if top3:
        st.markdown("### Top 3 recommendations")
        for i, entry in enumerate(top3, start=1):
            crop = entry.get("crop", "—")
            prob = float(entry.get("probability", 0.0))
            st.write(f"{i}. **{crop}** — {prob*100:.1f}%")
    if rationale:
        st.info(rationale)


# --------------------------
# Fertilizer Recommendation Page (NEW)
# --------------------------
def page_fertilizer_recommendation():
    st.header("🧪 Fertilizer Recommendation")
    st.write("Fill soil & environmental details. Up to **2 missing values allowed**.")

    # Dropdown options
    soil_options = ["Black", "Clayey", "Loamy", "Red", "Sandy", None]
    crop_options = [
        "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
        "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco",
        "Wheat", None
    ]

    # Inputs
    Temparature = st.number_input("Temperature (°C)", min_value=0.0, value=26.0)
    Humidity = st.number_input("Humidity (%)", min_value=0.0, value=50.0)
    Moisture = st.number_input("Moisture (%)", min_value=0.0, value=40.0)
    Nitrogen = st.number_input("Nitrogen (N)", min_value=0.0, value=50.0)
    Potassium = st.number_input("Potassium (K)", min_value=0.0, value=30.0)
    Phosphorous = st.number_input("Phosphorous (P)", min_value=0.0, value=20.0)

    Soil_Type = st.selectbox("Soil Type (optional)", soil_options, index=3)
    Crop_Type = st.selectbox("Crop Type (optional)", crop_options, index=8)

    if st.button("Recommend Fertilizer"):
        # Payload
        payload = {
            "Temparature": Temparature,
            "Humidity": Humidity,
            "Moisture": Moisture,
            "Nitrogen": Nitrogen,
            "Potassium": Potassium,
            "Phosphorous": Phosphorous,
        }

        if Soil_Type is not None:
            payload["Soil Type"] = Soil_Type

        if Crop_Type is not None:
            payload["Crop Type"] = Crop_Type

        url = API_BASE.rstrip("/") + "/predict/fertilizer"
        st.info(f"Calling API: {url}")

        try:
            resp = requests.post(url, json=payload, timeout=8)
            st.write("Response status:", resp.status_code)
            st.code(resp.text, language="json")

            if resp.status_code == 200:
                data = resp.json()
                st.success(f"Recommended Fertilizer: **{data.get('recommended_fertilizer')}**")

                # Show probabilities if present
                if data.get("probabilities"):
                    st.markdown("### Fertilizer Probabilities")
                    classes = data.get("classes", [])
                    probs = data.get("probabilities", [])

                    for cls, prob in zip(classes, probs):
                        st.write(f"- **{cls}** → {prob*100:.2f}%")

        except Exception as e:
            st.error(f"Failed to contact API: {e}")


# --------------------------
# Yield Prediction Page (NEW)
# --------------------------
def page_yield_prediction():
    st.header("📈 Yield Prediction")
    st.write("Predict crop yield. You may skip up to **2** features (choose 'none').")

    # Provided Area options + 'none'
    area_options = [
        'Albania', 'Algeria', 'Angola', 'Argentina', 'Armenia',
        'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain',
        'Bangladesh', 'Belarus', 'Belgium', 'Botswana', 'Brazil',
        'Bulgaria', 'Burkina Faso', 'Burundi', 'Cameroon', 'Canada',
        'Central African Republic', 'Chile', 'Colombia', 'Croatia',
        'Denmark', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador',
        'Eritrea', 'Estonia', 'Finland', 'France', 'Germany', 'Ghana',
        'Greece', 'Guatemala', 'Guinea', 'Guyana', 'Haiti', 'Honduras',
        'Hungary', 'India', 'Indonesia', 'Iraq', 'Ireland', 'Italy',
        'Jamaica', 'Japan', 'Kazakhstan', 'Kenya', 'Latvia', 'Lebanon',
        'Lesotho', 'Libya', 'Lithuania', 'Madagascar', 'Malawi',
        'Malaysia', 'Mali', 'Mauritania', 'Mauritius', 'Mexico',
        'Montenegro', 'Morocco', 'Mozambique', 'Namibia', 'Nepal',
        'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Norway',
        'Pakistan', 'Papua New Guinea', 'Peru', 'Poland', 'Portugal',
        'Qatar', 'Romania', 'Rwanda', 'Saudi Arabia', 'Senegal',
        'Slovenia', 'South Africa', 'Spain', 'Sri Lanka', 'Sudan',
        'Suriname', 'Sweden', 'Switzerland', 'Tajikistan', 'Thailand',
        'Tunisia', 'Turkey', 'Uganda', 'Ukraine', 'United Kingdom',
        'Uruguay', 'Zambia', 'Zimbabwe', "none"
    ]

    # Provided Item options + 'none'
    item_options = [
        'Maize', 'Potatoes', 'Rice, paddy', 'Sorghum', 'Soybeans', 'Wheat',
        'Cassava', 'Sweet potatoes', 'Plantains and others', 'Yams', "none"
    ]

    # Inputs
    Area = st.selectbox("Area (select or choose 'none')", area_options, index=area_options.index("India") if "India" in area_options else 0)
    Item = st.selectbox("Item / Crop (select or choose 'none')", item_options, index=0)
    Year = st.number_input("Year", min_value=1900, max_value=2100, value=2018, step=1)
    average_rain_fall_mm_per_year = st.number_input("Average Rainfall (mm per year)", value=1000.0, step=1.0)
    pesticides_tonnes = st.number_input("Pesticides (tonnes)", value=1.0, step=0.1)
    avg_temp = st.number_input("Average Temperature (°C)", value=22.0, step=0.1)

    if st.button("Predict Yield"):
        # Build payload using only provided values (skip 'none' or blank)
        payload = {}
        if Area is not None and Area != "none":
            payload["Area"] = Area
        if Item is not None and Item != "none":
            payload["Item"] = Item
        # numeric fields - allow user to skip by setting a toggle? we include them by default
        payload["Year"] = int(Year) if Year else None
        payload["average_rain_fall_mm_per_year"] = float(average_rain_fall_mm_per_year) if average_rain_fall_mm_per_year != "" else None
        payload["pesticides_tonnes"] = float(pesticides_tonnes) if pesticides_tonnes != "" else None
        payload["avg_temp"] = float(avg_temp) if avg_temp != "" else None

        # Remove None values so API receives only provided features
        payload = {k: v for k, v in payload.items() if v is not None}

        st.info("Sending payload (only non-empty fields)")
        st.code(payload, language="json")

        url = API_BASE.rstrip("/") + "/predict/yield"
        st.info(f"Calling API: {url}")

        # Try first the direct-field API (top-level fields). If that fails (non-200), try nested {"data": {...}}
        try:
            resp = requests.post(url, json=payload, timeout=8)
        except Exception as e:
            st.error(f"Could not connect to API: {e}")
            return

        st.write("Attempt 1 - status code:", resp.status_code)
        st.code(resp.text, language="json")

        if resp.status_code == 200:
            try:
                data = resp.json()
                st.success(f"Predicted yield: **{data.get('predicted_yield', data)}**")
            except Exception:
                st.error("Invalid JSON from API")
            return

        # Attempt 2: nested payload under "data"
        try:
            resp2 = requests.post(url, json={"data": payload}, timeout=8)
            st.write("Attempt 2 (nested) - status code:", resp2.status_code)
            st.code(resp2.text, language="json")
            if resp2.status_code == 200:
                try:
                    data = resp2.json()
                    st.success(f"Predicted yield: **{data.get('predicted_yield', data)}**")
                except Exception:
                    st.error("Invalid JSON from API (attempt 2)")
                return
            else:
                st.error("API returned non-200 status for both attempts.")
        except Exception as e:
            st.error(f"Second attempt failed: {e}")

# --------------------------
# Irrigation Scheduler Page (NEW)
# --------------------------
def page_irrigation_scheduler():
    st.header("🚰 Irrigation Scheduler")
    st.write("Get a smart recommendation on whether irrigation is needed.")

    # Crop options (EXACT as requested)
    crop_options = [
        "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
        "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco",
        "Wheat"
    ]

    # Inputs
    soil_moisture = st.number_input(
        "Soil Moisture (%)", min_value=0.0, max_value=100.0, value=30.0
    )
    temperature = st.number_input(
        "Temperature (°C)", min_value=0.0, value=30.0
    )
    humidity = st.number_input(
        "Humidity (%)", min_value=0.0, max_value=100.0, value=50.0
    )

    rain_forecast = st.selectbox(
        "Rain Forecast",
        options=["no", "yes"],
        help="Select 'yes' if rain is expected soon"
    )

    crop_type = st.selectbox(
        "Crop Type",
        options=crop_options
    )

    if st.button("Check Irrigation Requirement"):
        payload = {
            "soil_moisture": float(soil_moisture),
            "temperature": float(temperature),
            "humidity": float(humidity),
            "rain_forecast": rain_forecast,
            "crop_type": crop_type,
        }

        url = API_BASE.rstrip("/") + "/predict/irrigation"
        st.info(f"Calling API: {url}")
        st.code(payload, language="json")

        try:
            resp = requests.post(url, json=payload, timeout=8)
            st.write("Response status code:", resp.status_code)
            st.code(resp.text, language="json")

            if resp.status_code == 200:
                data = resp.json()
                decision = data.get("irrigation_decision", "—")

                if decision.lower() == "irrigate":
                    st.success("✅ Irrigation is REQUIRED for this crop.")
                else:
                    st.info("💧 Irrigation is NOT required at this time.")

            else:
                st.error("API returned an error.")

        except Exception as e:
            st.error(f"Could not connect to API: {e}")
# --------------------------
# 🧪 SOIL HEALTH CHECK (ONLY NEW CODE)
# --------------------------
def page_soil_health_check():
    st.header("🧪 Soil Health Check")
    st.write("Check overall soil condition using NPK and pH values.")

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

                st.success(f"🌱 Soil Health Status: **{data['soil_health_class']}**")
                st.metric("Confidence", f"{data['confidence']*100:.1f}%")

                st.markdown("### 📊 Class Probabilities")
                for cls, prob in data["class_probabilities"].items():
                    st.write(f"- **{cls}** → {prob*100:.2f}%")
            else:
                st.error("API error while checking soil health")

        except Exception as e:
            st.error(f"Could not connect to API: {e}")
# --------------------------
# Blank pages
# --------------------------
def blank_sanker(name):
    st.header(name)
    st.markdown("<div style='color:#b00020;font-weight:700;font-size:20px'>sanket error</div>", unsafe_allow_html=True)


def page_home():
    st.title("Welcome to AgroXpert 🌾")
    st.write("Use the left menu to open features.")
    st.image(
        "https://agroxpert.in/wp-content/uploads/2020/12/Untitled-design-4.png",
        use_container_width=True,
        caption="Sanket_Gadekar 🌾"
    )

def page_about():
    st.header("About AgroXpert")
    st.markdown("""
    **AgroXpert** is a smart farming platform built to guide farmers using simple,  
    **AI-powered tools** that make agriculture easier, smarter, and more efficient.
    """)
    st.image(
        "https://eos.com/wp-content/uploads/2020/02/drone-technology-for-agriculture.jpg.webp",
        use_container_width=True,
        caption="Empowering farmers with AI-driven insights 🌾"
    )
    st.markdown("""
        ### 🌾 What AgroXpert Does
        AgroXpert helps farmers in every stage of farming:

        - **Crop Recommendation** – get the best crop suggestion based on soil & weather  
        - **Fertilizer Recommendation** – know exactly what nutrients your soil needs  
        - **Disease Detection** *(coming soon)* – upload leaf photos to find plant diseases  
        - **Irrigation Scheduler** *(coming soon)* – tells when and how much to water  
        - **Pest & Disease Risk Alerts** *(coming soon)* – stay prepared for threats  
        - **Soil Health Check** *(coming soon)* – quick evaluation of soil condition  
        - **Yield Prediction** *(coming soon)* – early yield estimation for better planning  

        ---

        ### 🤖 Powered by AI, Designed for Farmers  
        AgroXpert uses:
        - Machine Learning  
        - Weather + soil data  
        - Image analysis  
        - Practical agricultural knowledge  

        All combined to give farmers **simple, clear, and reliable guidance**.

        ---

        ### 🎯 Our Vision  
        To empower every farmer with AI tools that improve productivity, reduce risk,  
        and make farming more successful and sustainable.

        ---

        *AgroXpert is part of the AnnadataAI initiative — advancing agriculture with technology.*
        """)


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
    blank_sanker("Disease Detection")
elif page == "Irrigation Scheduler":
    page_irrigation_scheduler()
elif page == "About":
    page_about()
else:
    st.write("Unknown page")
