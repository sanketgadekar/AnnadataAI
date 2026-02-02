import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------
# SAFE PATH HANDLING
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src/irrigation_scheduler
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "scheduler",
    "processed",
    "irrigation_clean.csv"
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "irrigation_model.pkl"
)

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(DATA_PATH)

print("✅ Processed data loaded")
print("Shape:", df.shape)

# -----------------------------
# SPLIT FEATURES / TARGET
# -----------------------------
X = df.drop("irrigation_needed", axis=1)
y = df["irrigation_needed"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# TRAIN MODEL
# -----------------------------
model = DecisionTreeClassifier(
    max_depth=5,
    min_samples_leaf=20,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# EVALUATION
# -----------------------------
y_pred = model.predict(X_test)

print("\n✅ Model Evaluation")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 3))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -----------------------------
# SAVE MODEL
# -----------------------------
joblib.dump(model, MODEL_PATH)

print("\n✅ Model saved at:")
print(MODEL_PATH)
