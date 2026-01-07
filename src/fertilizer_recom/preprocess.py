# src/fertilizer_recom/preprocess.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from config import RAW_DATA_PATH, RANDOM_STATE, TEST_SIZE

def load_data(path=RAW_DATA_PATH):
    """Load CSV into DataFrame."""
    df = pd.read_csv(path)
    return df

def minimal_cleaning(df):
    """
    Minimal cleaning:
      - Strip column names
      - Trim whitespace in object columns
      - Normalize 'nan' strings to np.nan
      - Drop rows that are fully empty and drop duplicates
    """
    df = df.copy()
    df = df.rename(columns=lambda c: c.strip())
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for c in obj_cols:
        # preserve NaNs while trimming strings; convert 'nan' literal to np.nan
        df[c] = df[c].astype(str).str.strip().replace({"nan": np.nan})
    df = df.dropna(axis=0, how="all")
    df = df.drop_duplicates()
    return df

def coerce_numeric_like_columns(df, exclude_cols=None):
    """
    Convert object columns that are numeric-like to numeric dtype.
    exclude_cols: list of columns to skip (e.g., target)
    """
    df = df.copy()
    if exclude_cols is None:
        exclude_cols = []
    for col in df.columns:
        if col in exclude_cols:
            continue
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str)
            if sample.empty:
                continue
            # Strict numeric-like pattern: optional leading -, digits, optional decimal
            is_numeric_like = sample.str.match(r"^\s*-?\d+(\.\d+)?\s*$").all()
            if is_numeric_like:
                df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def build_preprocessing_pipeline(df, target_col):
    """
    Build a ColumnTransformer that:
      - imputes numeric with median + scales
      - imputes categorical with most frequent + one-hot (sparse_output=False)
    Returns: preprocessor, feature_columns, numeric_cols, categorical_cols
    """
    all_cols = df.columns.tolist()
    feature_columns = [c for c in all_cols if c != target_col]
    X = df[feature_columns].copy()

    # Coerce numeric-like object columns to numeric
    X = coerce_numeric_like_columns(X)

    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = [c for c in feature_columns if c not in numeric_cols]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Use sparse_output=False for sklearn >=1.4/1.6 compatibility
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols)
        ],
        remainder="drop"
    )

    return preprocessor, feature_columns, numeric_cols, categorical_cols

def prepare_train_test(df, target_col, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=True):
    """
    Minimal preprocessing + train/test split.
    Returns a dict with preprocessor, feature lists and splits.
    """
    df = minimal_cleaning(df)
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Available columns: {df.columns.tolist()}")

    # Coerce numeric-like columns globally except target
    df = coerce_numeric_like_columns(df, exclude_cols=[target_col])

    preprocessor, feature_columns, numeric_cols, categorical_cols = build_preprocessing_pipeline(df, target_col)
    X = df[feature_columns]
    y = df[target_col]

    stratify_col = y if (stratify and y.nunique() > 1) else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_col
    )

    return {
        "preprocessor": preprocessor,
        "feature_columns": feature_columns,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }
