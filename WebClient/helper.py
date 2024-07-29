from django.core.files.storage import default_storage
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.utils import load_img
from tensorflow.keras.models import load_model
from datetime import datetime
import os
from django.conf import settings

def getImageFilenameTimestamp(image_filename):
    file_name, extension = os.path.splitext(image_filename)
    file_name = file_name + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S")) + extension
    return file_name

def preprocessImage(image):
    file_name = getImageFilenameTimestamp(image.name)
    file_name_2 = settings.MEDIA_ROOT + "/images/" + file_name
    file_url = file_name_2
    original = load_img(file_url, target_size=(224, 224))
    img_array = img_to_array(original)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array, file_name

def analyzeImage(image):
    img_array, file_name = preprocessImage(image)
    model = load_model('/Users/lazaaq/Documents/tugas akhir/5. multiclass classification BRACOL/notebooks/20240721 ResNet50 - 100epoch, 0.92 on test/best_weights_resnet.keras')
    
    # Predict class probabilities
    predictions = model.predict(img_array)
    
    # Convert predictions to class indices
    predicted_class = np.argmax(predictions, axis=1)
    predicted_class = predicted_class[0]
    
    classes = ["cercospora", "healthy", "miner", "phoma", "rust"]

    return classes[predicted_class], file_name

    