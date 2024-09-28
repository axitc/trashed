#!/usr/bin/env python

# NOTE : experiment with epochs. results will probably differ
IMG_WIDTH, IMG_HEIGHT = 224, 224
BATCH_SIZE = 32
EPOCHS = 5

import os
import cv2
import numpy as np
def load_data(data_dir):
    images = []
    labels = []
    for file in os.listdir(data_dir):
        img = cv2.imread(os.path.join(data_dir, file))
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        # scale image between 0 and 1
        if 'trash' in file:
            label = 1
        else:
            label = 0
        images.append(img)
        labels.append(label)
    return np.array(images), np.array(labels)

train_dir = '../data/ready/batchx'

train_images, train_labels = load_data(train_dir)

from sklearn.model_selection import train_test_split
train_images, val_images, train_labels, val_labels = train_test_split(train_images, train_labels, test_size=0.2, random_state=42)

from tensorflow.keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(
        rotation_range = 30,
        width_shift_range = 0.2,
        height_shift_range = 0.2,
        shear_range = 30,
        zoom_range = 0.2,
        horizontal_flip = True,
        fill_mode = 'nearest'
        )
val_datagen = ImageDataGenerator()

train_generator = train_datagen.flow(train_images, train_labels, batch_size = BATCH_SIZE)
val_generator = val_datagen.flow(val_images, val_labels, batch_size = BATCH_SIZE)

from tensorflow.keras.models import load_model
cnn = load_model('cnn.keras')

cnn.fit(train_generator, epochs=EPOCHS, validation_data=val_generator)

cnn.save('cnn.keras')
