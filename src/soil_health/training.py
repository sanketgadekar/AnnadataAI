import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

from src.soil_health.config import PROCESSED_DATA_PATH, MODEL_PATH


def load_processed_data():
    return pd.read_csv(PROCESSED_DATA_PATH)


def prepare_data(df):
    X = df[["N", "P", "K", "ph"]]
    y = df["soil_health_class"]
    return X, y


def train_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    print("\n📊 Classification Report:\n")
    print(classification_report(y_test, y_pred))

    print("🧮 Confusion Matrix:\n")
    print(confusion_matrix(y_test, y_pred))


def save_model(model):
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved at: {MODEL_PATH}")


def training_pipeline():
    df = load_processed_data()
    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    save_model(model)


if __name__ == "__main__":
    training_pipeline()
