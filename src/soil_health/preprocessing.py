import pandas as pd
import numpy as np

from src.soil_health.config import RAW_DATA_PATH, PROCESSED_DATA_PATH
from src.soil_health.thresholds import THRESHOLDS, WEIGHTS


def load_data():
    return pd.read_csv(RAW_DATA_PATH)


def clean_data(df):
    # Keep only soil parameters
    df = df[["N", "P", "K", "ph"]].copy()

    # Remove impossible values
    df = df[
        (df["ph"] >= 3.5) & (df["ph"] <= 9.0) &
        (df["N"] >= 0) & (df["P"] >= 0) & (df["K"] >= 0)
    ]

    return df


# ---------------- SCORING LOGIC (FIXED) ---------------- #

def feature_score(value, low, high):
    """
    Returns score multiplier for a feature:
    - Optimal range        -> 1.0
    - Slight deviation     -> 0.6
    - Severe deviation     -> 0.2
    """
    if low <= value <= high:
        return 1.0
    elif (low * 0.8) <= value <= (high * 1.2):
        return 0.6
    else:
        return 0.2


def calculate_soil_health_score(row):
    score = 0

    for feature, weight in WEIGHTS.items():
        low = THRESHOLDS[feature]["low"]
        high = THRESHOLDS[feature]["high"]

        multiplier = feature_score(row[feature], low, high)
        score += multiplier * weight * 100

    return round(score, 2)


def deficiency_report(row):
    issues = []

    for feature, limits in THRESHOLDS.items():
        if row[feature] < limits["low"]:
            issues.append(f"{feature} deficient")
        elif row[feature] > limits["high"]:
            issues.append(f"{feature} excess")

    return "No major deficiency" if not issues else ", ".join(issues)


def assign_health_class(df):
    """
    Percentile-based classification to remove dataset bias
    """
    p30 = np.percentile(df["soil_health_score"], 30)
    p70 = np.percentile(df["soil_health_score"], 70)

    def classify(score):
        if score >= p70:
            return "Healthy"
        elif score >= p30:
            return "Moderate"
        else:
            return "Poor"

    df["soil_health_class"] = df["soil_health_score"].apply(classify)
    return df


def preprocess_pipeline():
    df = load_data()
    df = clean_data(df)

    df["soil_health_score"] = df.apply(calculate_soil_health_score, axis=1)
    df["deficiency_report"] = df.apply(deficiency_report, axis=1)
    df = assign_health_class(df)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print("✅ Soil health dataset reprocessed with bias-aware scoring")


if __name__ == "__main__":
    preprocess_pipeline()
