import numpy as np

def apply_channel_adjustments(aligned_image, brightness, contrast):
    if aligned_image is None:
        return None
        
    img = aligned_image.astype(np.float32)
    img = img * (1 + contrast) + brightness
    return np.clip(img, 0, 255).astype(np.uint8)
