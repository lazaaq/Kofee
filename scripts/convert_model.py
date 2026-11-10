"""Convert the trained Keras ResNet model to TFLite for the production runtime.

Usage (needs requirements-dev.txt, i.e. full TensorFlow):
    python scripts/convert_model.py path/to/best_weights_resnet.keras model/kofee_resnet.tflite

The output is float16-quantised (about half the size, same predictions in practice).
The script prints a comparison between Keras and TFLite on the sample images.
"""
import os
import sys

import numpy as np
import tensorflow as tf
from PIL import Image

CLASSES = ["cercospora", "healthy", "miner", "phoma", "rust"]
SAMPLES = os.path.join(os.path.dirname(__file__), "..", "media", "sample_image")


def load(path):
    with Image.open(path) as img:
        img = img.convert("RGB").resize((224, 224), Image.NEAREST)
        return np.expand_dims(np.asarray(img, dtype=np.float32) / 255.0, 0)


def main(src, dst):
    model = tf.keras.models.load_model(src)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()

    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "wb") as f:
        f.write(tflite_model)
    print(f"Wrote {dst} ({len(tflite_model) / 1e6:.1f} MB)")

    interpreter = tf.lite.Interpreter(model_path=dst)
    interpreter.allocate_tensors()
    inp = interpreter.get_input_details()[0]["index"]
    out = interpreter.get_output_details()[0]["index"]
    for name in sorted(os.listdir(SAMPLES)):
        x = load(os.path.join(SAMPLES, name))
        keras_cls = CLASSES[int(np.argmax(model.predict(x, verbose=0)))]
        interpreter.set_tensor(inp, x)
        interpreter.invoke()
        lite_cls = CLASSES[int(np.argmax(interpreter.get_tensor(out)))]
        print(f"{name:28s} keras={keras_cls:11s} tflite={lite_cls}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
