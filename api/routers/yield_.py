from fastapi import APIRouter, HTTPException
from api.schemas.yield_ import YieldInput
from api.core.logging import logger

router = APIRouter(prefix="/predict", tags=["Yield"])

try:
    from src.yield_pred.predict import predict_single, load_model
    _model = load_model()
except Exception:
    _model = None

@router.post("/yield")
def predict_yield(data: YieldInput):
    if _model is None:
        raise HTTPException(503, "Yield predictor unavailable")
    try:
        return {"predicted_yield": predict_single(data.dict(), model=_model)}
    except Exception:
        logger.exception("Yield prediction error")
        raise HTTPException(500, "Internal server error")
