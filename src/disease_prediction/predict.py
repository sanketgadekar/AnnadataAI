import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from .config import MODEL_PATH, CLASS_PATH, IMG_HEIGHT, IMG_WIDTH


def predict_disease(image_path):
    model = load_model(MODEL_PATH)

    with open(CLASS_PATH, "r") as f:
        class_map = json.load(f)

    idx_to_class = {v: k for k, v in class_map.items()}

    img = image.load_img(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)
    idx = int(np.argmax(preds))
    confidence = float(preds[0][idx])

    return {
        "disease": idx_to_class[idx],
        "confidence": confidence
    }


if __name__ == "__main__":
    # ⚠️ CHANGE THIS PATH TO A REAL IMAGE
    result = predict_disease("sample_leaf.jpg")
    print(result)
