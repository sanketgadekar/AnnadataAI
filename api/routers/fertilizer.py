from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from api.schemas.fertilizer import FertilizerInput
from api.core.logging import logger

router = APIRouter(prefix="/predict", tags=["Fertilizer"])

try:
    from src.fertilizer_recom.predict import predict_from_dict
    _fert_available = True
except Exception:
    predict_from_dict = None
    _fert_available = False

@router.post("/fertilizer")
def predict_fertilizer(data: FertilizerInput):
    if not _fert_available:
        raise HTTPException(503, "Fertilizer predictor unavailable")
    try:
        payload = data.dict(by_alias=True, exclude_none=True)
        if "Temparature" in payload and "Temperature" not in payload:
            payload["Temperature"] = payload.pop("Temparature")
        return jsonable_encoder(predict_from_dict(payload))
    except Exception:
        logger.exception("Fertilizer prediction error")
        raise HTTPException(500, "Internal server error")
