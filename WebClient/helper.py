import os
import threading
from datetime import datetime

import numpy as np
from django.conf import settings
from PIL import Image

CLASSES = ["cercospora", "healthy", "miner", "phoma", "rust"]
IMAGE_SIZE = (224, 224)


class ModelUnavailableError(RuntimeError):
    """Raised when the classification model file is missing or cannot be loaded."""


def getImageFilenameTimestamp(image_filename):
    file_name, extension = os.path.splitext(image_filename)
    file_name = file_name + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S")) + extension
    return file_name


def preprocessImage(image_path):
    # Same as keras load_img(target_size=(224, 224)) (nearest interpolation) + img_to_array / 255
    with Image.open(image_path) as original:
        original = original.convert("RGB").resize(IMAGE_SIZE, Image.NEAREST)
        img_array = np.asarray(original, dtype=np.float32) / 255.0
    return np.expand_dims(img_array, axis=0)


class _Classifier:
    """Loads the model once per process and runs predictions.

    A ``.tflite`` model runs on the lightweight LiteRT runtime (used in production);
    any other extension (``.keras`` / ``.h5``) falls back to full TensorFlow.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._predict = None

    def _load(self):
        path = settings.MODEL_PATH
        if not os.path.exists(path):
            raise ModelUnavailableError(f"Model file not found: {path}")

        if path.endswith(".tflite"):
            from ai_edge_litert.interpreter import Interpreter

            interpreter = Interpreter(model_path=path, num_threads=2)
            interpreter.allocate_tensors()
            input_index = interpreter.get_input_details()[0]["index"]
            output_index = interpreter.get_output_details()[0]["index"]

            def predict(img_array):
                interpreter.set_tensor(input_index, img_array)
                interpreter.invoke()
                return interpreter.get_tensor(output_index)
        else:
            from tensorflow.keras.models import load_model

            model = load_model(path)

            def predict(img_array):
                return model.predict(img_array, verbose=0)

        return predict

    def predict(self, img_array):
        with self._lock:
            if self._predict is None:
                self._predict = self._load()
            return self._predict(img_array)


_classifier = _Classifier()


def analyzeImage(image_path):
    """Classify the leaf image stored at ``image_path`` and return the class name."""
    img_array = preprocessImage(image_path)
    predictions = _classifier.predict(img_array)
    predicted_class = int(np.argmax(predictions, axis=1)[0])
    return CLASSES[predicted_class]


def change12HourTo24HourFormat(timestamp):
    return datetime.strptime(timestamp, "%I:%M %p").strftime("%H:%M")
