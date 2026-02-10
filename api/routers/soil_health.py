from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
import joblib, pandas as pd
from api.schemas.soil_health import SoilHealthInput
from api.core.config import BASE_DIR
from api.core.logging import logger

router = APIRouter(prefix="/predict", tags=["Soil Health"])

MODEL_PATH = BASE_DIR / "models" / "soil_health" / "soil_health_model.pkl"
soil_health_model = joblib.load(MODEL_PATH)
FEATURES = ["N", "P", "K", "ph"]

@router.post("/soil-health")
def predict_soil_health(data: SoilHealthInput):
    try:
        df = pd.DataFrame([[data.N, data.P, data.K, data.ph]], columns=FEATURES)
        prediction = soil_health_model.predict(df)[0]
        probs = soil_health_model.predict_proba(df)[0]
        return jsonable_encoder({
            "soil_health_class": prediction,
            "confidence": round(max(probs), 3),
            "class_probabilities": dict(zip(soil_health_model.classes_, probs))
        })
    except Exception:
        logger.exception("Soil health error")
        raise HTTPException(500, "Internal server error")
