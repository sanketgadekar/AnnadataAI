import os

# Get project root (two levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Data and model paths
DATA_PATH = os.path.join(BASE_DIR, "data", "recommendation", "raw", "Crop_recommendation.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "crop_model.pkl")

# Create necessary directories if they don't exist
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
