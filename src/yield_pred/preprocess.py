# preprocess.py
# Preprocessing utilities for Yield Prediction

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from .import config


def load_data(path: str = None):
    path = path or config.DATA_PATH
    df = pd.read_csv(path)
    return df


def build_preprocessing_pipeline(df: pd.DataFrame):
    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    # auto-detect target column
    possible_targets = [
        c for c in numeric_cols 
        if "yield" in c.lower() or c.lower() == "target"
    ]
    target_col = possible_targets[0] if possible_targets else None

    if target_col:
        numeric_cols = [c for c in numeric_cols if c != target_col]

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # numeric transformer
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ])

    # categorical transformer
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ],
        remainder="drop"
    )

    feature_info = {
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "target_col": target_col
    }

    return preprocessor, feature_info


def train_test_split_df(df: pd.DataFrame, test_size=None, random_state=None):
    test_size = test_size or config.TEST_SIZE
    random_state = random_state or config.RANDOM_STATE

    possible_targets = [
        c for c in df.columns 
        if "yield" in c.lower() or c.lower() == "target"
    ]

    if not possible_targets:
        raise ValueError("Target column not found. Expected column containing 'yield' or named 'target'.")

    target = possible_targets[0]

    X = df.drop(columns=[target])
    y = df[target]

    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def save_preprocessor(preprocessor, path):
    joblib.dump(preprocessor, path)
