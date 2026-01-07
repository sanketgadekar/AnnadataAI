import os
import traceback
import joblib
import pickle
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder

# ----------------------------
# Logging setup
# ----------------------------
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
#  EXISTING CODE (NOT TOUCHED / IMPROVED)
# ============================================================

# ----------------------------
# MODEL PATHS
# ----------------------------
FERTILIZER_MODEL_PATHS = [
    os.path.join("models", "fertilizer_model.pkl"),
    os.path.join("models", "fertilizer_pipeline.joblib"),
    os.path.join("models", "fertilizer_model.joblib"),
    os.path.join("models", "fertilizer_pipeline.pkl"),
]


def _find_fertilizer_model():
    for p in FERTILIZER_MODEL_PATHS:
        if os.path.exists(p):
            return p
    return None


# ----------------------------
# TRY TO IMPORT CROP PREDICTOR
# ----------------------------
try:
    from src.recommendation.predict import predict as legacy_crop_predict
    logger.info("Imported legacy crop predictor.")
except Exception as e:
    legacy_crop_predict = None
    logger.warning("Could not import crop predictor: %s", e, exc_info=True)


# ----------------------------
# IMPORT FERTILIZER PREDICTOR (NEW SIMPLIFIED VERSION)
# ----------------------------
try:
    from src.fertilizer_recom.predict import predict_from_dict
    _fert_available = True
    logger.info("Imported fertilizer predictor (predict_from_dict).")
except Exception as e:
    logger.warning("Could not import predict_from_dict: %s", e, exc_info=True)
    predict_from_dict = None
    _fert_available = False


# ============================================================
#   >>> YIELD MODEL IMPORTS (LAZY) <<<
# ============================================================
# We avoid heavy eager loading at import time. Use lazy loader.
_yield_model = None
_yield_available = False
_load_yield_error = None

try:
    # attempt shallow import of functions; actual model loaded lazily
    from src.yield_pred.predict import predict_single, load_model  # type: ignore
    _yield_imported = True
    logger.info("Yield prediction module import OK (model will be lazy-loaded).")
except Exception as e:
    predict_single = None
    load_model = None
    _yield_imported = False
    _load_yield_error = e
    logger.warning("Could not import yield prediction module: %s", e, exc_info=True)


def get_yield_model():
    """Lazy load yield model and cache it. Returns model or raises exception."""
    global _yield_model, _yield_available, _load_yield_error
    if _yield_model is not None:
        return _yield_model
    if not _yield_imported:
        raise RuntimeError("yield module not available") from _load_yield_error
    try:
        _yield_model = load_model()
        _yield_available = True
        logger.info("Yield model loaded successfully.")
        return _yield_model
    except Exception as e:
        _yield_available = False
        _load_yield_error = e
        logger.exception("Failed to load yield model:")
        raise


# ============================================================
#   >>> SOIL HEALTH SERVICE IMPORT ADDED HERE <<<
# ============================================================
try:
    from soil_health.service import assess_soil
    _soil_available = True
    logger.info("Imported soil_health.service.assess_soil")
except Exception as e:
    assess_soil = None
    _soil_available = False
    logger.warning("Could not import soil health service: %s", e, exc_info=True)


# ============================================================
#  SCHEMAS
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
    # Note: original code had "Temparature" (misspelling). We'll accept both keys
    # by reading model input with by_alias and falling back to raw dict keys.
    Temparature: Optional[float] = Field(None, alias="Temparature")
    Temperature: Optional[float] = Field(None, alias="Temperature")
    Humidity: Optional[float] = Field(None, alias="Humidity")
    Moisture: Optional[float] = Field(None, alias="Moisture")
    Nitrogen: Optional[float] = Field(None, alias="Nitrogen")
    Potassium: Optional[float] = Field(None, alias="Potassium")
    Phosphorous: Optional[float] = Field(None, alias="Phosphorous")
    Soil_Type: Optional[str] = Field(None, alias="Soil Type")
    Crop_Type: Optional[str] = Field(None, alias="Crop Type")

    class Config:
        allow_population_by_field_name = True


# ============================================================
#   >>> YIELD MODEL SCHEMA ADDED HERE <<<
# ============================================================

class YieldInput(BaseModel):
    Area: Optional[str] = "India"
    Item: Optional[str] = "Wheat"
    Year: Optional[int] = 2013
    average_rain_fall_mm_per_year: Optional[float] = 1100
    pesticides_tonnes: Optional[float] = 5.4
    avg_temp: Optional[float] = 24.5

    class Config:
        schema_extra = {
            "example": {
                "Area": "India",
                "Item": "Wheat",
                "Year": 2013,
                "average_rain_fall_mm_per_year": 1100,
                "pesticides_tonnes": 5.4,
                "avg_temp": 24.5,
            }
        }


# ============================================================
#   >>> SOIL HEALTH SCHEMAS ADDED HERE (Pydantic IN API FILE) <<<
# ============================================================
# Pydantic models for the soil-health endpoint are defined here,
# as requested (keeps API self-contained).

class SoilTestInput(BaseModel):
    N: Optional[float] = Field(None, description="Available Nitrogen (kg/ha or ppm)")
    P: Optional[float] = Field(None, description="Available Phosphorus (kg/ha or ppm)")
    K: Optional[float] = Field(None, description="Available Potassium (kg/ha or ppm)")
    pH: Optional[float] = Field(None, description="Soil pH")
    OC: Optional[float] = Field(None, description="Organic Carbon (%)")
    crop: Optional[str] = Field(None, description="Optional crop name for crop-specific tuning")
    soil_type: Optional[str] = Field(None, alias="soil_type", description="Optional soil type")
    lab_method: Optional[str] = Field("default", description="Lab extractant/method")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "N": 120,
                "P": 8,
                "K": 85,
                "pH": 5.8,
                "OC": 0.45,
                "crop": "maize",
                "soil_type": "sandy_loam",
                "lab_method": "default",
            }
        }


class SoilHealthOutput(BaseModel):
    grade: str
    problems: list[str]
    improvement_plan: list[str]
    explainability: Dict[str, Any]


# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(title="AnnadataAI API")


@app.get("/")
def home():
    return {
        "message": "API Running",
        "endpoints": ["/predict/crop", "/predict/fertilizer", "/predict/yield", "/predict/soil-health", "/health"],
    }


@app.get("/health")
def health_check():
    """
    Lightweight health endpoint that indicates availability of optional services.
    """
    return {
        "status": "ok",
        "services": {
            "crop_predictor": legacy_crop_predict is not None,
            "fertilizer_predictor": _fert_available,
            "yield_model_imported": _yield_imported,
            "yield_model_loaded": _yield_available,
            "soil_service": _soil_available,
        },
    }


# ----------------------------
# CROP PREDICTION
# ----------------------------
@app.post("/predict/crop")
def predict_crop(data: CropInput):
    if legacy_crop_predict is None:
        raise HTTPException(status_code=503, detail="Crop prediction function missing")

    try:
        result = legacy_crop_predict(data.dict())

        if isinstance(result, str):
            return {"recommended_crop": result}

        if isinstance(result, dict):
            return jsonable_encoder(result)

        return {"recommended_crop": str(result)}

    except Exception as e:
        logger.exception("Error in predict_crop:")
        # avoid leaking internals
        raise HTTPException(status_code=500, detail="Internal server error")


# ----------------------------
# FERTILIZER PREDICTION
# ----------------------------
def fertilizer_payload_from_model(data: FertilizerInput) -> Dict[str, Any]:
    """
    Build payload for fertilizer predictor robustly across pydantic versions and aliases.
    Accepts both 'Temparature' and 'Temperature' (and returns the canonical key).
    """
    # pydantic v2: model_dump, v1: dict
    if hasattr(data, "model_dump"):
        raw = data.model_dump(by_alias=True)
    else:
        # for pydantic v1
        raw = data.dict(by_alias=True)

    # normalize keys: prefer correct spelling 'Temperature' if provided, else 'Temparature'
    if raw.get("Temperature") is None and raw.get("Temparature") is not None:
        raw["Temperature"] = raw.pop("Temparature")

    # also try to map "Soil Type" alias to "Soil Type" key expected by old predictor
    # (predict_from_dict expects certain keys; adjust as needed)
    payload = {k: v for k, v in raw.items() if v is not None}
    return payload


@app.post("/predict/fertilizer")
def predict_fertilizer(data: FertilizerInput):
    if not _fert_available:
        raise HTTPException(status_code=503, detail="Fertilizer predictor not available")

    try:
        payload = fertilizer_payload_from_model(data)

        result = predict_from_dict(payload)
        return jsonable_encoder(result)

    except ValueError as ve:
        logger.warning("Validation error in predict_fertilizer: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("Error in predict_fertilizer:")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
#   >>> YIELD PREDICTION ENDPOINT ADDED HERE <<<
# ============================================================
@app.post("/predict/yield")
def predict_yield(payload: YieldInput):
    if not _yield_imported:
        raise HTTPException(status_code=503, detail="Yield prediction module not available")

    try:
        model = get_yield_model()
    except Exception as e:
        # get_yield_model already logged the exception
        raise HTTPException(status_code=503, detail="Yield model not available")

    try:
        input_dict = payload.dict()
        result = predict_single(input_dict, model=model)
        return {"predicted_yield": result}
    except ValueError as ve:
        logger.warning("Validation error in predict_yield: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("Error in predict_yield:")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
#   >>> SOIL HEALTH ENDPOINT ADDED HERE <<<
# ============================================================
@app.post("/predict/soil-health", response_model=SoilHealthOutput)
def predict_soil(payload: SoilTestInput):
    """
    Rule-based soil health assessment endpoint.
    Uses src/soil_health/service.assess_soil (if available).
    """
    if not _soil_available:
        raise HTTPException(status_code=503, detail="Soil health service not available")

    try:
        # pydantic v2 uses model_dump; fall back to dict if not available
        if hasattr(payload, "model_dump"):
            data = payload.model_dump()
        else:
            data = payload.dict()

        # keep only provided keys (no Nones)
        data = {k: v for k, v in data.items() if v is not None}

        # sanity check: need at least one numeric soil parameter
        if not any(data.get(k) is not None for k in ("N", "P", "K", "pH", "OC")):
            raise HTTPException(status_code=400, detail="Provide at least one of N, P, K, pH, OC")

        result = assess_soil(data)
        # ensure JSON serializable
        return jsonable_encoder(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in predict_soil:")
        raise HTTPException(status_code=500, detail="Internal server error")
