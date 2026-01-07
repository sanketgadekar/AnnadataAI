import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from src.recommendation.data_preprocessing import load_data, split_data
from src.recommendation.config import DATA_PATH, MODEL_PATH


def train_model(data_path: str, model_path: str):
    """Train a RandomForest model and save it."""
    df = load_data(data_path)
    X_train, X_test, y_train, y_test = split_data(df)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42
    )

    # Cross-validation
    scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"Cross-validation scores: {scores}")
    print(f"Average CV score: {scores.mean():.4f}")

    # Train final model
    model.fit(X_train, y_train)
    joblib.dump(model, model_path)
    print(f"✅ Model saved to {model_path}")

    return model, X_test, y_test


if __name__ == "__main__":
    model, X_test, y_test = train_model(
        data_path=DATA_PATH,
        model_path=MODEL_PATH
    )
