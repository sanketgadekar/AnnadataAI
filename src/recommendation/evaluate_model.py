import joblib
from sklearn.metrics import classification_report, accuracy_score
from src.recommendation.data_preprocessing import load_data, split_data
from src.recommendation.config import DATA_PATH, MODEL_PATH


def evaluate_model(model_path: str, data_path: str):
    """Evaluate saved model."""
    model = joblib.load(model_path)
    df = load_data(data_path)
    _, X_test, _, y_test = split_data(df)

    y_pred = model.predict(X_test)

    print("✅ Evaluation Report:")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")


if __name__ == "__main__":
    evaluate_model(
        model_path=MODEL_PATH,
        data_path=DATA_PATH
    )
