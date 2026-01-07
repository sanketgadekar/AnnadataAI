# src/fertilizer_recom/config.py
import os

# Project root (two levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Data path
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "fertilizer_recom")
RAW_DATA_PATH = os.path.join(DATA_DIR, "Fertilizer Prediction.csv")

# Models path
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODELS_DIR, exist_ok=True)
MODEL_FILENAME = os.path.join(MODELS_DIR, "fertilizer_model.pkl")


# Training defaults
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Model defaults
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = None
