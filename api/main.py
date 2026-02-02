import os
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder

# ============================================================
# LOGGING SETUP
# ============================================================
logger = logging.getLogger("annadata.api")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ============================================================
# CROP ENCODING MAP (FOR IRRIGATION ONLY)
# Must match LabelEncoder order used during training
# ============================================================
CROP_ENCODING_MAP = {
    "Barley": 0,
    "Cotton": 1,
    "Ground Nuts": 2,
    "Maize": 3,
    "Millets": 4,
    "Oil seeds": 5,
    "Paddy": 6,
    "Pulses": 7,
    "Sugarcane": 8,
    "Tobacco": 9,
    "Wheat": 10
}

# ============================================================
# CROP PREDICTOR (LEGACY – UNCHANGED)
# ============================================================
try:
    from src.recommendation.predict import predict as legacy_crop_predict
    logger.info("Imported legacy crop predictor.")
except Exception:
    legacy_crop_predict = None
    logger.warning("Could not import crop predictor", exc_info=True)

# ============================================================
# FERTILIZER PREDICTOR (UNCHANGED)
# ============================================================
try:
    from src.fertilizer_recom.predict import predict_from_dict
    _fert_available = True
    logger.info("Imported fertilizer predictor.")
except Exception:
    predict_from_dict = None
    _fert_available = False
    logger.warning("Fertilizer predictor not available", exc_info=True)

# ============================================================
# YIELD MODEL (LAZY LOAD – UNCHANGED)
# ============================================================
_yield_model = None
_yield_available = False

try:
    from src.yield_pred.predict import predict_single, load_model
    _yield_imported = True
    logger.info("Yield module imported (lazy loading enabled).")
except Exception:
    predict_single = None
    load_model = None
    _yield_imported = False
    logger.warning("Yield module import failed", exc_info=True)

def get_yield_model():
    global _yield_model, _yield_available
    if _yield_model is not None:
        return _yield_model
    try:
        _yield_model = load_model()
        _yield_available = True
        return _yield_model
    except Exception as e:
        _yield_available = False
        raise RuntimeError("Yield model load failed") from e

# ============================================================
# IRRIGATION SCHEDULER (NEW MODEL)
# ============================================================
try:
    from src.irrigation_scheduler.scheduler import irrigation_scheduler
    _irrigation_available = True
    logger.info("Irrigation scheduler imported.")
except Exception:
    irrigation_scheduler = None
    _irrigation_available = False
    logger.warning("Irrigation scheduler not available", exc_info=True)

# ============================================================
# SCHEMAS
# ============================================================
class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class FertilizerInput(BaseModel):
    Temparature: Optional[float] = Field(None, alias="Temparature")
    Temperature: Optional[float] = Field(None, alias="Temperature")
    Humidity: Optional[float] = None
    Moisture: Optional[float] = None
    Nitrogen: Optional[float] = None
    Potassium: Optional[float] = None
    Phosphorous: Optional[float] = None
    Soil_Type: Optional[str] = Field(None, alias="Soil Type")
    Crop_Type: Optional[str] = Field(None, alias="Crop Type")

    class Config:
        allow_population_by_field_name = True

class YieldInput(BaseModel):
    Area: Optional[str] = "India"
    Item: Optional[str] = "Wheat"
    Year: Optional[int] = 2013
    average_rain_fall_mm_per_year: Optional[float] = 1100
    pesticides_tonnes: Optional[float] = 5.4
    avg_temp: Optional[float] = 24.5

# 🔹 IRRIGATION INPUT (HUMAN-FRIENDLY)
class IrrigationInput(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    rain_forecast: str = Field(..., example="no", description="yes or no")
    crop_type: str = Field(..., example="Maize")

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(title="AnnadataAI API")

@app.get("/")
def home():
    return {
        "message": "API Running",
        "endpoints": [
            "/predict/crop",
            "/predict/fertilizer",
            "/predict/yield",
            "/predict/irrigation",
            "/health",
        ],
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "services": {
            "crop": legacy_crop_predict is not None,
            "fertilizer": _fert_available,
            "yield_imported": _yield_imported,
            "yield_loaded": _yield_available,
            "irrigation": _irrigation_available,
        },
    }

# ============================================================
# CROP PREDICTION (UNCHANGED)
# ============================================================
@app.post("/predict/crop")
def predict_crop(data: CropInput):
    if legacy_crop_predict is None:
        raise HTTPException(503, "Crop predictor unavailable")
    try:
        result = legacy_crop_predict(data.dict())
        return jsonable_encoder({"recommended_crop": result})
    except Exception:
        logger.exception("Crop prediction error")
        raise HTTPException(500, "Internal server error")

# ============================================================
# FERTILIZER PREDICTION (UNCHANGED)
# ============================================================
@app.post("/predict/fertilizer")
def predict_fertilizer(data: FertilizerInput):
    if not _fert_available:
        raise HTTPException(503, "Fertilizer predictor unavailable")
    try:
        payload = data.dict(by_alias=True, exclude_none=True)
        if "Temparature" in payload and "Temperature" not in payload:
            payload["Temperature"] = payload.pop("Temparature")
        result = predict_from_dict(payload)
        return jsonable_encoder(result)
    except Exception:
        logger.exception("Fertilizer prediction error")
        raise HTTPException(500, "Internal server error")

# ============================================================
# YIELD PREDICTION (UNCHANGED)
# ============================================================
@app.post("/predict/yield")
def predict_yield(data: YieldInput):
    if not _yield_imported:
        raise HTTPException(503, "Yield predictor unavailable")
    try:
        model = get_yield_model()
        result = predict_single(data.dict(), model=model)
        return {"predicted_yield": result}
    except Exception:
        logger.exception("Yield prediction error")
        raise HTTPException(500, "Internal server error")

# ============================================================
# IRRIGATION SCHEDULER (NEW, SIMPLE, CLEAN)
# ============================================================
@app.post("/predict/irrigation")
def predict_irrigation(data: IrrigationInput):
    if not _irrigation_available:
        raise HTTPException(503, "Irrigation scheduler unavailable")

    crop = data.crop_type.strip()
    rain_value = data.rain_forecast.strip().lower()

    if crop not in CROP_ENCODING_MAP:
        raise HTTPException(400, f"Unsupported crop type: {crop}")

    if rain_value not in ["yes", "no"]:
        raise HTTPException(400, "rain_forecast must be 'yes' or 'no'")

    crop_encoded = CROP_ENCODING_MAP[crop]
    rain_encoded = 1 if rain_value == "yes" else 0

    try:
        decision = irrigation_scheduler(
            soil_moisture=data.soil_moisture,
            temperature=data.temperature,
            humidity=data.humidity,
            rain_forecast=rain_encoded,
            crop_type_encoded=crop_encoded,
        )

        return {
            "crop": crop,
            "rain_forecast": rain_value,
            "irrigation_decision": decision
        }

    except Exception:
        logger.exception("Irrigation prediction error")
        raise HTTPException(500, "Internal server error")
