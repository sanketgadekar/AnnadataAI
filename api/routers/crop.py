from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from api.schemas.crop import CropInput
from api.core.logging import logger

router = APIRouter(prefix="/predict", tags=["Crop"])

try:
    from src.recommendation.predict import predict as legacy_crop_predict
except Exception:
    legacy_crop_predict = None

@router.post("/crop")
def predict_crop(data: CropInput):
    if legacy_crop_predict is None:
        raise HTTPException(503, "Crop predictor unavailable")
    try:
        result = legacy_crop_predict(data.dict())
        return jsonable_encoder({"recommended_crop": result})
    except Exception:
        logger.exception("Crop prediction error")
        raise HTTPException(500, "Internal server error")
