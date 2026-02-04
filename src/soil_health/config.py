from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = BASE_DIR / "data" / "health" / "raw" / "Crop_recommendation.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "health" / "processed" / "soil_health_processed.csv"

MODEL_PATH = BASE_DIR / "models" / "soil_health" / "soil_health_model.pkl"
