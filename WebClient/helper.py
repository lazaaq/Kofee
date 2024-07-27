from django.core.files.storage import default_storage
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.utils import load_img
from tensorflow.keras.models import load_model
import time


def preprocessImage(image):
    file_name = "temp.jpg"
    file_name_2 = default_storage.save(file_name, image)
    file_url = default_storage.url(file_name_2)
    file_url = '/Users/lazaaq/Documents/tugas akhir/6. Web/GIthub Repo/Kofee' + file_url
    original = load_img(file_url, target_size=(224, 224))
    img_array = img_to_array(original)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def analyzeImage(image):
    img_array = preprocessImage(image)
    model = load_model('/Users/lazaaq/Documents/tugas akhir/5. multiclass classification BRACOL/notebooks/20240721 ResNet50 - 100epoch, 0.92 on test/best_weights_resnet.keras')
    
    # Predict class probabilities
    predictions = model.predict(img_array)
    
    # Convert predictions to class indices
    predicted_class = np.argmax(predictions, axis=1)
    predicted_class = predicted_class[0]
    
    classes = ["cercospora", "healthy", "miner", "phoma", "rust"]

    return classes[predicted_class]

    