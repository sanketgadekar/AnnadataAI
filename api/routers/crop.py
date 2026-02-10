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

        # --------------------------------------------------
        # Normalize legacy model output (IMPORTANT)
        # --------------------------------------------------

        # Case 1: legacy returns string
        if isinstance(result, str):
            return jsonable_encoder({
                "recommended_crop": result,
                "top3": [{"crop": result}],
                "rationale": "Crop recommended based on soil and weather conditions"
            })

        # Case 2: legacy returns dict with top3
        if isinstance(result, dict):
            recommended = result.get("recommended_crop", "—")

            # If recommended is dict, extract crop name
            if isinstance(recommended, dict):
                recommended = recommended.get("crop", "—")

            top3_raw = result.get("top3", [])
            top3 = []

            for item in top3_raw:
                if isinstance(item, dict) and "crop" in item:
                    top3.append({"crop": item["crop"]})
                elif isinstance(item, str):
                    top3.append({"crop": item})

            if not top3 and recommended != "—":
                top3 = [{"crop": recommended}]

            return jsonable_encoder({
                "recommended_crop": recommended,
                "top3": top3,
                "rationale": result.get(
                    "rationale",
                    "Top crops selected based on predicted suitability"
                )
            })

        # Fallback (should not happen)
        return jsonable_encoder({
            "recommended_crop": "Unknown",
            "top3": [],
            "rationale": "Unable to determine crop"
        })

    except Exception:
        logger.exception("Crop prediction error")
        raise HTTPException(500, "Internal server error")
