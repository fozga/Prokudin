"""
Image processing utilities for channel adjustment and combination.

This module provides functions for brightness/contrast adjustment, channel combination, and conversion to QImage for display in PyQt5 GUIs.

Cross-references:
    - handlers.channels: Uses apply_adjustments and combine_channels.
    - handlers.display: Uses combine_channels and convert_to_qimage.
"""

import cv2
import numpy as np
from PyQt5.QtGui import QImage

def apply_adjustments(image, brightness=0, contrast=0):
    """
    Applies brightness and contrast adjustments to a grayscale image.

    Args:
        image (numpy.ndarray or None): Input 8-bit grayscale image (shape: HxW).
        brightness (int): [-100, 100] - additive brightness adjustment.
        contrast (int): [-100, 100] - multiplicative contrast adjustment (percentage).

    Returns:
        numpy.ndarray: Adjusted 8-bit image (uint8) or None if input is invalid.

    Example:
        >>> adjusted = apply_adjustments(img, brightness=20, contrast=10)

    Cross-references:
        - handlers.channels.adjust_channel
    """
    if image is None:
        return None
    
    img = image.astype(np.float32)
    img = img * (1 + contrast/100) + brightness
    return np.clip(img, 0, 255).astype(np.uint8)

def combine_channels(channels, intensities):
    """
    Combines three grayscale channels into RGB image with intensity adjustments.

    Args:
        channels (list of numpy.ndarray): [R, G, B] 8-bit grayscale images (uint8, shape: HxW).
        intensities (list of int): [R%, G%, B%] intensity multipliers (0-200%).

    Returns:
        numpy.ndarray or None: Combined 8-bit RGB image (uint8, shape: HxWx3) or None if any channel missing.

    Cross-references:
        - handlers.display.show_combined_image
    """
    if any(channel is None for channel in channels):
        return None
    
    combined = np.zeros((*channels[0].shape, 3), dtype=np.float32)
    for i in range(3):
        combined[:, :, i] = channels[i].astype(np.float32) * (intensities[i]/100)
    
    return np.clip(combined, 0, 255).astype(np.uint8)

def convert_to_qimage(image):
    """
    Converts numpy image to QImage for PyQt5 display.

    Args:
        image (numpy.ndarray or None): 
            - Grayscale: HxW (uint8)
            - RGB: HxWx3 (uint8)

    Returns:
        QImage: Empty QImage if input invalid, otherwise formatted image.

    Cross-references:
        - handlers.display.show_combined_image
        - handlers.display.show_single_channel_image
    """
    if image is None:
        return QImage()
    
    if len(image.shape) == 2:  # Grayscale
        return QImage(image.data, image.shape[1], image.shape[0], 
                     image.strides[0], QImage.Format_Grayscale8)
    else:  # RGB
        return QImage(image.data, image.shape[1], image.shape[0],
                     image.strides[0], QImage.Format_RGB888)
