# config.py
# Configuration for Yield Prediction Project

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DATA_PATH = os.path.join(ROOT_DIR, "data", "yield_pred", "yield_df.csv")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "yield_model.pkl")

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 3

# Maximum missing allowed during prediction
MAX_MISSING_ALLOWED = 2
