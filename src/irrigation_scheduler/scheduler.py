import os
import joblib
import pandas as pd

# -----------------------------
# SAFE PATH HANDLING
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src/irrigation_scheduler
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "irrigation_model.pkl"
)

# -----------------------------
# LOAD TRAINED MODEL
# -----------------------------
model = joblib.load(MODEL_PATH)
print("✅ Irrigation model loaded successfully")

# -----------------------------
# IRRIGATION SCHEDULER FUNCTION
# -----------------------------
def irrigation_scheduler(
    soil_moisture: float,
    temperature: float,
    humidity: float,
    rain_forecast: int,
    crop_type_encoded: int
) -> str:
    """
    Returns irrigation decision based on sensor & crop inputs.
    """

    input_df = pd.DataFrame([[
        soil_moisture,
        temperature,
        humidity,
        rain_forecast,
        crop_type_encoded
    ]], columns=[
        "soil_moisture",
        "temperature",
        "humidity",
        "rain_forecast",
        "crop_type_encoded"
    ])

    prediction = model.predict(input_df)[0]

    return "Irrigate" if prediction == 1 else "Do Not Irrigate"


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":
    decision = irrigation_scheduler(
        soil_moisture=28,
        temperature=36,
        humidity=40,
        rain_forecast=0,
        crop_type_encoded=3   # Example encoded crop
    )

    print("🌱 Irrigation Decision:", decision)
