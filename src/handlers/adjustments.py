import numpy as np

def apply_channel_adjustments(aligned_image, brightness, contrast):
    """
    Applies brightness and contrast adjustments to a single aligned image channel.

    Args:
        aligned_image (numpy.ndarray or None): Input 2D grayscale image (uint8) to adjust.
        brightness (float): Value to add to each pixel (can be negative or positive).
        contrast (float): Multiplicative contrast factor (e.g., 0 for no change, 0.2 for +20%, -0.2 for -20%).

    Returns:
        numpy.ndarray or None: Adjusted image as uint8 array, or None if input is None.

    Example:
        adjusted = apply_channel_adjustments(img, brightness=10, contrast=0.15)
    """
    if aligned_image is None:
        return None
        
    img = aligned_image.astype(np.float32)
    img = img * (1 + contrast) + brightness
    return np.clip(img, 0, 255).astype(np.uint8)
