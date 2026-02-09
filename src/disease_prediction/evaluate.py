from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from .config import MODEL_PATH, VAL_DIR, IMG_HEIGHT, IMG_WIDTH, BATCH_SIZE


def evaluate_model():
    model = load_model(MODEL_PATH)

    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    val_gen = ImageDataGenerator(rescale=1.0 / 255).flow_from_directory(
        VAL_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False
    )

    loss, acc = model.evaluate(val_gen)
    print(f"✅ Validation Accuracy: {acc:.4f}")


if __name__ == "__main__":
    evaluate_model()
