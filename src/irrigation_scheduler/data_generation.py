import pandas as pd
import numpy as np
import os

np.random.seed(42)
NUM_SAMPLES = 2000

# -----------------------------
# SAFE ABSOLUTE PATH HANDLING
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/irrigation_scheduler
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "scheduler",
    "raw",
    "irrigation_data.csv"
)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# -----------------------------
# DATA GENERATION
# -----------------------------
crop_thresholds = {
    "Barley": 30,
    "Cotton": 25,
    "Ground Nuts": 30,
    "Maize": 30,
    "Millets": 25,
    "Oil seeds": 30,
    "Paddy": 55,
    "Pulses": 25,
    "Sugarcane": 45,
    "Tobacco": 35,
    "Wheat": 30
}

records = []

for _ in range(NUM_SAMPLES):
    crop = np.random.choice(list(crop_thresholds.keys()))
    soil_moisture = round(np.random.uniform(10, 80), 2)
    temperature = round(np.random.uniform(20, 45), 2)
    humidity = round(np.random.uniform(20, 90), 2)
    rain_forecast = np.random.choice([0, 1], p=[0.7, 0.3])

    irrigation_needed = 1 if soil_moisture < crop_thresholds[crop] and rain_forecast == 0 else 0

    records.append([
        soil_moisture,
        temperature,
        humidity,
        rain_forecast,
        crop,
        irrigation_needed
    ])

df = pd.DataFrame(
    records,
    columns=[
        "soil_moisture",
        "temperature",
        "humidity",
        "rain_forecast",
        "crop_type",
        "irrigation_needed"
    ]
)

df.to_csv(OUTPUT_PATH, index=False)

print("✅ Dataset saved at:")
print(OUTPUT_PATH)
