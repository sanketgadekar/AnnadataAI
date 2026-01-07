# train.py
# Train Random Forest model with preprocessing pipeline

import joblib
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from .import config
from .preprocess import load_data, build_preprocessing_pipeline, train_test_split_df


def train_and_save(model_path=None):
    model_path = model_path or config.MODEL_PATH

    df = load_data()
    preprocessor, feature_info = build_preprocessing_pipeline(df)

    X_train, X_test, y_train, y_test = train_test_split_df(df)

    model = RandomForestRegressor(random_state=config.RANDOM_STATE)

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    param_grid = {
        "model__n_estimators": [100, 200],
        "model__max_depth": [8, 16, None],
        "model__min_samples_leaf": [1, 2, 4],
    }

    print("Running GridSearch...")
    grid = GridSearchCV(
        pipeline, param_grid,
        cv=config.CV_FOLDS,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
        verbose=1
    )

    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    print("Best Params:", grid.best_params_)

    y_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\nTest MSE: {mse:.4f}")
    print(f"Test R² : {r2:.4f}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(best_model, model_path)
    print("Model saved at:", model_path)

    return best_model


if __name__ == "__main__":
    train_and_save()
