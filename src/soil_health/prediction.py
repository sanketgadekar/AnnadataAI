import joblib
import pandas as pd

from src.soil_health.config import MODEL_PATH


FEATURE_ORDER = ["N", "P", "K", "ph"]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("❌ Trained soil health model not found")
    return joblib.load(MODEL_PATH)


def validate_input(soil_input: dict):
    """
    Validate user-provided soil input
    """
    for feature in FEATURE_ORDER:
        if feature not in soil_input:
            raise ValueError(f"Missing required feature: {feature}")

        if not isinstance(soil_input[feature], (int, float)):
            raise ValueError(f"{feature} must be numeric")

    return True


def prepare_input(soil_input: dict):
    """
    Convert dict input into model-ready DataFrame
    """
    validate_input(soil_input)

    df = pd.DataFrame([[soil_input[f] for f in FEATURE_ORDER]],
                      columns=FEATURE_ORDER)
    return df


def predict_soil_health(soil_input: dict):
    """
    Main prediction function
    """
    model = load_model()
    X = prepare_input(soil_input)

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    class_probs = dict(zip(model.classes_, probabilities))

    return {
        "soil_health_class": prediction,
        "confidence": round(max(probabilities), 3),
        "class_probabilities": class_probs
    }


# ----------------- TEST LOCALLY ----------------- #
if __name__ == "__main__":
    sample_input = {
        "N": 35,
        "P": 25,
        "K": 30,
        "ph": 5.2
    }

    result = predict_soil_health(sample_input)
    print("\n🌱 Soil Health Prediction Result:")
    print(result)
