from PyQt5.QtGui import QImage, QPixmap
import cv2

def create_combined_preview(processed_images, intensities):
    combined = np.zeros((*processed_images[0].shape, 3), dtype=np.float32)
    for i in range(3):
        combined[:, :, i] = processed_images[i].astype(np.float32) * (intensities[i] / 100)
    return combined.astype(np.uint8)

def convert_to_qimage(image):
    if len(image.shape) == 2:  # Grayscale
        return QImage(image.data, image.shape[1], image.shape[0], 
                     image.strides[0], QImage.Format_Grayscale8)
    else:  # RGB
        return QImage(image.data, image.shape[1], image.shape[0],
                     image.strides[0], QImage.Format_RGB888)
