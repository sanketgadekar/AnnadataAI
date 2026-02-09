import json
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam

from .preprocess import get_data_generators
from .config import MODEL_PATH, CLASS_PATH, EPOCHS


def train_model():
    train_gen, val_gen = get_data_generators()
    num_classes = train_gen.num_classes

    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )
    base_model.trainable = False

    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(128, activation="relu"),
        Dense(num_classes, activation="softmax")
    ])

    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS
    )

    model.save(MODEL_PATH, include_optimizer=False)

    # Save class index mapping
    with open(CLASS_PATH, "w") as f:
        json.dump(train_gen.class_indices, f)

    print("✅ Disease model and class labels saved")


if __name__ == "__main__":
    train_model()
