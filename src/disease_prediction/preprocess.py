from tensorflow.keras.preprocessing.image import ImageDataGenerator
from .config import IMG_HEIGHT, IMG_WIDTH, BATCH_SIZE, TRAIN_DIR, VAL_DIR

def get_data_generators():
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        zoom_range=0.2,
        horizontal_flip=True
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode="categorical"
    )

    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode="categorical"
    )

    return train_generator, val_generator
