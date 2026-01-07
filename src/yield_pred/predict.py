# predict.py
# Predict yield from user input with missing-value control

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any
from .import config


def load_model(path=None):
    path = path or config.MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError("Model not found. Train the model first.")
    return joblib.load(path)


def predict_single(input_dict: Dict[str, Any], model=None):
    model = model or load_model()
    preprocessor = model.named_steps["preprocessor"]

    num_cols = []
    cat_cols = []

    # retrieve original feature names
    for name, transformer, cols in preprocessor.transformers_:
        if name == "num":
            num_cols = list(cols)
        elif name == "cat":
            cat_cols = list(cols)

    expected_cols = num_cols + cat_cols

    # Missing input check
    missing = [
        c for c in expected_cols 
        if c not in input_dict or pd.isna(input_dict.get(c))
    ]

    if len(missing) > config.MAX_MISSING_ALLOWED:
        raise ValueError(
            f"Too many missing inputs ({len(missing)}). "
            f"Maximum allowed: {config.MAX_MISSING_ALLOWED}"
        )

    row = {c: input_dict.get(c, np.nan) for c in expected_cols}
    X = pd.DataFrame([row])

    pred = model.predict(X)
    return float(pred[0])


if __name__ == "__main__":
    example = {}
    try:
        m = load_model()
        print("Prediction:", predict_single(example, model=m))
    except Exception as e:
        print("Error:", e)
