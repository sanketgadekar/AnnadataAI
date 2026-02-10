from fastapi import APIRouter, HTTPException
from api.schemas.irrigation import IrrigationInput
from api.core.config import CROP_ENCODING_MAP
from api.core.logging import logger

router = APIRouter(prefix="/predict", tags=["Irrigation"])

try:
    from src.irrigation_scheduler.scheduler import irrigation_scheduler
    _available = True
except Exception:
    irrigation_scheduler = None
    _available = False

@router.post("/irrigation")
def predict_irrigation(data: IrrigationInput):
    if not _available:
        raise HTTPException(503, "Irrigation scheduler unavailable")

    crop = data.crop_type.strip()
    rain = data.rain_forecast.lower()

    if crop not in CROP_ENCODING_MAP:
        raise HTTPException(400, f"Unsupported crop type: {crop}")

    rain_encoded = 1 if rain == "yes" else 0

    try:
        decision = irrigation_scheduler(
            soil_moisture=data.soil_moisture,
            temperature=data.temperature,
            humidity=data.humidity,
            rain_forecast=rain_encoded,
            crop_type_encoded=CROP_ENCODING_MAP[crop],
        )
        return {"irrigation_decision": decision}
    except Exception:
        logger.exception("Irrigation error")
        raise HTTPException(500, "Internal server error")
