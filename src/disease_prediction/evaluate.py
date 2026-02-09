from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from .config import MODEL_PATH, TEST_DIR, IMG_HEIGHT, IMG_WIDTH, BATCH_SIZE


def evaluate_model():
    model = load_model(MODEL_PATH)

    test_gen = ImageDataGenerator(rescale=1.0 / 255).flow_from_directory(
        TEST_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False
    )

    loss, acc = model.evaluate(test_gen)
    print(f"✅ Test Accuracy: {acc:.4f}")


if __name__ == "__main__":
    evaluate_model()
