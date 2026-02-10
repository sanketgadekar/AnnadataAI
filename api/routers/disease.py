from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.encoders import jsonable_encoder
import shutil, uuid
from api.core.config import BASE_DIR
from api.core.logging import logger

router = APIRouter(prefix="/predict", tags=["Disease"])

from src.disease_prediction.predict import predict_disease

TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

@router.post("/disease")
async def predict_disease_api(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Uploaded file must be an image")

    temp_path = TEMP_DIR / f"{uuid.uuid4().hex}_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return jsonable_encoder(predict_disease(str(temp_path)))
    except Exception:
        logger.exception("Disease prediction error")
        raise HTTPException(500, "Internal server error")
    finally:
        if temp_path.exists():
            temp_path.unlink()
