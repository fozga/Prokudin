import cv2
import numpy as np
from PyQt5.QtGui import QImage

# TODO  Implement async processing

def apply_adjustments(image, brightness=0, contrast=0):
    """
    Applies brightness and contrast adjustments to a grayscale image.

    Args:
        image (numpy.ndarray | None): Input 8-bit grayscale image (shape: HxW)
        brightness (int): [-100, 100] - additive brightness adjustment
        contrast (int): [-100, 100] - multiplicative contrast adjustment (percentage)

    Returns:
        numpy.ndarray: Adjusted 8-bit image (uint8) or None if input is invalid

    Example:
        >>> adjusted = apply_adjustments(img, brightness=20, contrast=10)
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
        channels (list): [R, G, B] 8-bit grayscale images (uint8, shape: HxW)
        intensities (list): [R%, G%, B%] intensity multipliers (0-200%)

    Returns:
        numpy.ndarray | None: Combined 8-bit RGB image (uint8, shape: HxWx3) 
                    or None if any channel missing

    Note:
        Output image uses float32 calculations for precision before conversion
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
        image (numpy.ndarray | None): 
            - Grayscale: HxW (uint8)
            - RGB: HxWx3 (uint8)

    Returns:
        QImage: Empty QImage if input invalid, otherwise formatted image

    Note:
        Uses image buffer directly (no copy) - original must persist while in use
    """
    if image is None:
        return QImage()
    
    if len(image.shape) == 2:  # Grayscale
        return QImage(image.data, image.shape[1], image.shape[0], 
                     image.strides[0], QImage.Format_Grayscale8)
    else:  # RGB
        return QImage(image.data, image.shape[1], image.shape[0],
                     image.strides[0], QImage.Format_RGB888)
