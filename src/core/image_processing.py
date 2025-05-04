import cv2
import numpy as np
from PyQt5.QtGui import QImage

def apply_adjustments(image, brightness=0, contrast=0):
    if image is None:
        return None
    
    img = image.astype(np.float32)
    img = img * (1 + contrast/100) + brightness
    return np.clip(img, 0, 255).astype(np.uint8)

def combine_channels(channels, intensities):
    if any(channel is None for channel in channels):
        return None
    
    combined = np.zeros((*channels[0].shape, 3), dtype=np.float32)
    for i in range(3):
        combined[:, :, i] = channels[i].astype(np.float32) * (intensities[i]/100)
    
    return np.clip(combined, 0, 255).astype(np.uint8)

def convert_to_qimage(image):
    if image is None:
        return QImage()
    
    if len(image.shape) == 2:  # Grayscale
        return QImage(image.data, image.shape[1], image.shape[0], 
                     image.strides[0], QImage.Format_Grayscale8)
    else:  # RGB
        return QImage(image.data, image.shape[1], image.shape[0],
                     image.strides[0], QImage.Format_RGB888)
