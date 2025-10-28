import cv2
import os
import numpy as np

def preprocess_image(img_path, augment=False):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (128, 128))
    img = img / 255.0
    # Optional: CLAHE for contrast enhancement
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # img = clahe.apply((img*255).astype(np.uint8)) / 255.0
    if augment:
        if np.random.rand() > 0.5:
            img = np.fliplr(img)
        if np.random.rand() > 0.5:
            img = np.flipud(img)
        angle = np.random.uniform(-15, 15)
        M = cv2.getRotationMatrix2D((64, 64), angle, 1)
        img = cv2.warpAffine(img, M, (128, 128), borderMode=cv2.BORDER_REFLECT)
    return img


