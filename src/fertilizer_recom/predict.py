# src/fertilizer_recom/predict.py
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import joblib

from .config import MODEL_FILENAME

ALLOWED_MISSING = 2  # up to 2 missing allowed


# -------------------------------------------------------
# Load Model
# -------------------------------------------------------
def load_pipeline(model_path=MODEL_FILENAME):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model file found at: {model_path}. Train model first.")

    data = joblib.load(model_path)

    pipeline = data.get("pipeline")
    feature_columns = data.get("feature_columns")
    label_encoder = data.get("label_encoder", None)

    if pipeline is None or feature_columns is None:
        raise ValueError("Model file is missing required keys ('pipeline' or 'feature_columns').")

    return pipeline, feature_columns, label_encoder


# -------------------------------------------------------
# Input Validation
# -------------------------------------------------------
def validate_input_dict(input_dict, feature_columns):
    """
    Build a single-row DataFrame from input_dict using feature_columns order.
    Allow up to ALLOWED_MISSING NaN values.
    """
    missing_keys = []
    row = {}

    for feat in feature_columns:
        if feat not in input_dict or input_dict[feat] is None or (isinstance(input_dict[feat], str) and input_dict[feat].strip() == ""):
            row[feat] = np.nan
            missing_keys.append(feat)
        else:
            row[feat] = input_dict[feat]

    if len(missing_keys) > ALLOWED_MISSING:
        raise ValueError(
            f"Too many missing inputs: {len(missing_keys)} missing. "
            f"Maximum allowed is {ALLOWED_MISSING}. Missing features: {missing_keys}"
        )

    df = pd.DataFrame([row], columns=feature_columns)
    return df


# -------------------------------------------------------
# Prediction (FINAL CLEAN VERSION)
# -------------------------------------------------------
def predict_from_dict(input_dict, model_path=MODEL_FILENAME):
    pipeline, feature_columns, label_encoder = load_pipeline(model_path)
    X_df = validate_input_dict(input_dict, feature_columns)

    pred_enc = pipeline.predict(X_df)

    # Decode label if encoder is present
    if label_encoder is not None:
        try:
            pred_label = label_encoder.inverse_transform(np.asarray(pred_enc, dtype=int))
            final = pred_label[0]
        except Exception:
            final = str(pred_enc[0])
    else:
        final = str(pred_enc[0])

    # 🚨 ONLY ONE VALUE RETURNED
    return {"recommended_fertilizer": final}


# -------------------------------------------------------
# CLI Input Parsing
# -------------------------------------------------------
def parse_kv_list(kv_list):
    res = {}
    for kv in kv_list:
        if "=" not in kv:
            raise ValueError(f"Invalid key-value pair '{kv}'. Use KEY=VALUE.")
        k, v = kv.split("=", 1)
        k = k.strip()
        v = v.strip()

        if v.lower() in {"null", "none", ""}:
            res[k] = None
            continue

        try:
            if "." in v:
                res[k] = float(v)
            else:
                res[k] = int(v)
        except Exception:
            res[k] = v

    return res


# -------------------------------------------------------
# CLI Execution
# -------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make prediction using saved fertilizer model.")
    parser.add_argument("--model-path", default=MODEL_FILENAME, help="Path to the saved pipeline joblib.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", help="JSON string with feature_name: value pairs.")
    group.add_argument("--json-file", help="Path to JSON file containing a JSON object.")
    group.add_argument("--kv", nargs="+", help="Example: --kv N=90 P=41 K=40 Crop=Sugarcane")

    args = parser.parse_args()

    # Choose input method
    if args.json:
        input_data = json.loads(args.json)
    elif args.json_file:
        with open(args.json_file, "r") as f:
            input_data = json.load(f)
    else:
        input_data = parse_kv_list(args.kv)

    # Run prediction
    try:
        out = predict_from_dict(input_data, model_path=args.model_path)
        print(json.dumps(out, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
