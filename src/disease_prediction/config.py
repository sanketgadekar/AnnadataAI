import os

# Image parameters
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32
EPOCHS = 10

# Project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# ===== DATASET PATHS (MATCH YOUR STRUCTURE EXACTLY) =====
TRAIN_DIR = os.path.join(
    BASE_DIR,
    "data",
    "disease",
    "New Plant Diseases Dataset",
    "New Plant Diseases Dataset",
    "train"
)

VAL_DIR = os.path.join(
    BASE_DIR,
    "data",
    "disease",
    "New Plant Diseases Dataset",
    "New Plant Diseases Dataset",
    "valid"
)

TEST_DIR = os.path.join(
    BASE_DIR,
    "data",
    "disease",
    "test",
    "test"
)

# ===== MODEL PATHS =====
MODEL_PATH = os.path.join(BASE_DIR, "models", "disease_model.h5")
CLASS_PATH = os.path.join(BASE_DIR, "models", "disease_classes.json")
