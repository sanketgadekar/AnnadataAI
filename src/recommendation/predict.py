# src/recommendation/predict.py
import joblib
import pandas as pd
from typing import Dict, Any, List
from src.recommendation.config import MODEL_PATH

def format_topk(classes, probs, k=3):
    pairs = list(zip(list(classes), list(probs)))
    pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)
    topk = [{"crop": str(c), "probability": float(round(p, 4))} for c, p in pairs_sorted[:k]]
    return topk

def predict(input_data: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
    """
    Return structured prediction with top-K crops and probabilities.

    Returns:
      {
        "recommended_crop": <top1_crop>,
        "top3": [{"crop": "Maize", "probability": 0.72}, ...],
        "rationale": "Model probabilities from RandomForestClassifier"
      }
    """
    # load model (should be a pipeline if you used preprocessing)
    model = joblib.load(MODEL_PATH)

    # Build DataFrame same shape as training features
    df = pd.DataFrame([input_data])

    # If model is a sklearn Pipeline that ends with classifier, it still supports predict_proba.
    # If the model does not support predict_proba, fall back to predict.
    try:
        probs = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(df)[0]        # shape (n_classes,)
            classes = model.classes_ if hasattr(model, "classes_") else model.named_steps[list(model.named_steps)[-1]].classes_
        else:
            # fallback: model doesn't support predict_proba (unlikely for RandomForest)
            pred = model.predict(df)[0]
            return {
                "recommended_crop": str(pred),
                "top3": [{"crop": str(pred), "probability": 1.0}],
                "rationale": "Model does not support probabilities; returned single prediction"
            }

        # format top-k
        topk = format_topk(classes, probs, k=top_k)
        recommended = topk[0]["crop"] if len(topk) > 0 else None

        return {
            "recommended_crop": recommended,
            "top3": topk,
            "rationale": f"Top {top_k} crops by predicted probability"
        }

    except Exception as e:
        # bubble up or handle as you prefer
        raise RuntimeError(f"Prediction failed: {e}")

# quick CLI test if run directly
if __name__ == "__main__":
    sample = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.0
    }
    print(predict(sample))
