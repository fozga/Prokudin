import numpy as np

def apply_brightness_contrast(image, brightness=0, contrast=0):
    """
    Apply brightness and contrast adjustment to a grayscale image.
    :param image: numpy array (grayscale)
    :param brightness: int, -100 to 100
    :param contrast: float, -0.5 to 0.5 (np. -50 do 50 podzielone przez 100)
    :return: adjusted image (uint8)
    """
    img = image.astype(np.float32)
    img = img * (1 + contrast) + brightness
    img = np.clip(img, 0, 255)
    return img.astype(np.uint8)
