# src/fertilizer_recom/train.py
import os
import joblib
import argparse

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

from config import RAW_DATA_PATH, MODEL_FILENAME, RF_N_ESTIMATORS, RF_MAX_DEPTH, RANDOM_STATE
from preprocess import load_data, prepare_train_test

# Optional imports for tuning (only used if --tune specified)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

def train_and_save(target_col, model_path=MODEL_FILENAME, overwrite=True, debug=False, no_stratify=False, tune=False):
    """
    Train a pipeline and save it. Options:
      - debug: print diagnostics and save test_predictions_debug.csv
      - no_stratify: disable stratified splitting
      - tune: run a small RandomizedSearchCV to tune RF hyperparameters
    """
    df = load_data()
    df.columns = df.columns.str.strip()

    if debug:
        print("Loaded data shape:", df.shape)
        print("Columns (first 100):", df.columns.tolist()[:100])
        if target_col in df.columns:
            print("Target value counts:\n", df[target_col].value_counts(dropna=False).head(100))

    prep = prepare_train_test(df, target_col=target_col, random_state=RANDOM_STATE, stratify=not no_stratify)
    preprocessor = prep["preprocessor"]
    X_train = prep["X_train"]
    X_test = prep["X_test"]
    y_train = prep["y_train"]
    y_test = prep["y_test"]

    # Label encode target (saves mapping)
    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train.astype(str))
    y_test_enc = le.transform(y_test.astype(str))

    clf = RandomForestClassifier(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("clf", clf)
    ])

    if tune:
        # small randomized search for useful defaults
        skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE)
        param_dist = {
            "clf__n_estimators": [100, 200, 400],
            "clf__max_depth": [None, 10, 30],
            "clf__min_samples_split": [2, 5, 10],
            "clf__max_features": ["sqrt", "log2", 0.5]
        }
        rs = RandomizedSearchCV(pipeline, param_distributions=param_dist, n_iter=12, cv=skf,
                                scoring="accuracy", n_jobs=-1, random_state=RANDOM_STATE, verbose=1)
        print("Running RandomizedSearchCV (tune=True). This may take some time...")
        rs.fit(X_train, y_train_enc)
        pipeline = rs.best_estimator_
        print("Best params:", rs.best_params_)
        print("Best CV score:", rs.best_score_)
    else:
        pipeline.fit(X_train, y_train_enc)

    # Evaluate
    preds_enc = pipeline.predict(X_test)
    acc = accuracy_score(y_test_enc, preds_enc)
    print(f"Test accuracy: {acc:.4f}")
    print("Classification report (encoded labels):")
    print(classification_report(y_test_enc, preds_enc, zero_division=0))

    # Save debug predictions (decoded labels)
    preds = le.inverse_transform(np.asarray(preds_enc, dtype=int))
    out = X_test.copy()
    out["y_true"] = y_test.values
    out["y_pred"] = preds
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    if debug:
        debug_csv = os.path.join(os.path.dirname(model_path), "test_predictions_debug.csv")
        out.to_csv(debug_csv, index=False)
        print("Saved debug predictions to:", debug_csv)

    # Persist pipeline + metadata
    payload = {
        "pipeline": pipeline,
        "feature_columns": prep["feature_columns"],
        "numeric_cols": prep["numeric_cols"],
        "categorical_cols": prep["categorical_cols"],
        "label_encoder": le
    }

    if os.path.exists(model_path) and not overwrite:
        raise FileExistsError(f"Model file {model_path} exists and overwrite=False")

    joblib.dump(payload, model_path)
    print(f"Saved pipeline + label mapping to {model_path}")

    return pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train fertilizer prediction model.")
    parser.add_argument("--target", required=True, help="Name of the target column in CSV (exact).")
    parser.add_argument("--model-path", default=MODEL_FILENAME, help="Path to save the trained pipeline.")
    parser.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing model file.")
    parser.add_argument("--debug", action="store_true", help="Print debug info and save test_predictions_debug.csv.")
    parser.add_argument("--no-stratify", action="store_true", help="Do not stratify train/test split.")
    parser.add_argument("--tune", action="store_true", help="Run RandomizedSearchCV for light hyperparameter tuning.")
    args = parser.parse_args()

    train_and_save(target_col=args.target, model_path=args.model_path, overwrite=(not args.no_overwrite),
                   debug=args.debug, no_stratify=args.no_stratify, tune=args.tune)
