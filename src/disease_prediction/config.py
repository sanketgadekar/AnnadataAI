import os

# Image parameters
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32
EPOCHS = 10

# 🔒 DATASET PATHS (EXACTLY AS YOUR STRUCTURE)
TRAIN_DIR = r"D:\New Plant Diseases Dataset\New Plant Diseases Dataset\train"
VAL_DIR   = r"D:\New Plant Diseases Dataset\New Plant Diseases Dataset\valid"
TEST_DIR  = r"D:\test\test"

# Project base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Model & class mapping paths
MODEL_PATH = os.path.join(BASE_DIR, "models/disease_model.h5")
CLASS_PATH = os.path.join(BASE_DIR, "models/disease_classes.json")
