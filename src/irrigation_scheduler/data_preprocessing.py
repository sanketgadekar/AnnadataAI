import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder

# -----------------------------
# SAFE PATH HANDLING
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src/irrigation_scheduler
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

INPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "scheduler",
    "raw",
    "irrigation_data.csv"
)

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "scheduler",
    "processed",
    "irrigation_clean.csv"
)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(INPUT_PATH)

print("✅ Raw data loaded")
print("Shape:", df.shape)

# -----------------------------
# ENCODE CROP TYPE
# -----------------------------
label_encoder = LabelEncoder()
df["crop_type_encoded"] = label_encoder.fit_transform(df["crop_type"])

# Drop original categorical column
df.drop("crop_type", axis=1, inplace=True)

# -----------------------------
# SAVE CLEAN DATA
# -----------------------------
df.to_csv(OUTPUT_PATH, index=False)

print("✅ Preprocessed data saved at:")
print(OUTPUT_PATH)
print("Final shape:", df.shape)
