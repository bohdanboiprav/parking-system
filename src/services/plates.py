import numpy as np
import pytesseract
import tensorflow as tf
from keras.src.utils import load_img, img_to_array
import keras
from tensorflow.keras.losses import MSE

model = keras.models.load_model('src/services/model_last3.keras')


async def plates_recognition(image_path, model):
    print(image_path)
    image = load_img(image_path)
    image_resized = load_img(image_path, target_size=(224, 224))
    image_arr_224 = img_to_array(image_resized) / 255.0
    h, w, d = np.array(image, dtype=np.uint8).shape
    image_arr_224 = image_arr_224.reshape(1, 224, 224, 3)
    coordinates = model.predict(image_arr_224)
    denorm = np.array([w, w, h, h])
    coordinates = coordinates * denorm
    img = np.array(load_img(image_path))
    xmin, xmax, ymin, ymax = int(coordinates[0, 0]), int(coordinates[0, 1]), int(coordinates[0, 2]), int(
        coordinates[0, 3])
    roi = img[ymin:ymax, xmin:xmax]
    text = pytesseract.image_to_string(roi, lang='eng')
    return text
