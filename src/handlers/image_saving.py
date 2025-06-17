"""
Handlers for saving processed images to files.
Provides functions to save images in various formats and handle file dialogs.
"""

import os
import re
from typing import Optional, Tuple, List

import cv2
import numpy as np
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QFileDialog, QMainWindow


def apply_crop(image: np.ndarray, crop_rect: QRect) -> np.ndarray:
    """
    Apply crop rectangle to an image.
    
    Args:
        image: NumPy array containing the image data
        crop_rect: QRect defining the crop region
        
    Returns:
        Cropped image as NumPy array
    """
    if image is None or crop_rect is None or not crop_rect.isValid():
        return image
        
    x, y, w, h = crop_rect.x(), crop_rect.y(), crop_rect.width(), crop_rect.height()
    
    # Ensure crop rectangle is within image bounds
    img_h, img_w = image.shape[:2]
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    w = max(1, min(w, img_w - x))
    h = max(1, min(h, img_h - y))
    
    # Apply crop
    return image[y:y+h, x:x+w].copy()


def _extract_extension_from_filter(filter_str: str) -> Optional[str]:
    """
    Extract the first file extension from a filter string.
    
    Args:
        filter_str: Filter string from QFileDialog (e.g., "JPEG (*.jpg *.jpeg)")
        
    Returns:
        The first extension found (e.g., "jpg") or None if no extension found
    """
    # Look for the pattern *.ext
    match = re.search(r'\*\.([a-zA-Z0-9]+)', filter_str)
    if match:
        return match.group(1).lower()
    return None


def save_image_with_dialog(
    main_window,  # MainWindow instance
) -> Tuple[bool, str]:
    """
    Open a file dialog to get a base filepath and then save all channel images and combined image.
    
    Saves images from main_window.aligned with appropriate suffixes:
    - base_name_r.ext for red channel
    - base_name_g.ext for green channel
    - base_name_b.ext for blue channel
    - base_name.ext for combined RGB image
    
    Args:
        main_window: MainWindow instance containing aligned and processed images
        
    Returns:
        Tuple containing:
            - Boolean indicating success or failure
            - String with status message
    """
    # Check if there are any images to save
    if not any(img is not None for img in main_window.aligned):
        return False, "No images to save"
        
    file_filters = "Images (*.png *.jpg *.jpeg *.tif *.tiff);;PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;All Files (*)"
    filepath, selected_filter = QFileDialog.getSaveFileName(
        main_window, "Save Images", "", file_filters
    )

    if not filepath:
        return False, "Save operation cancelled"
    
    # Parse the filepath to get base name and extension
    base_path, extension = os.path.splitext(filepath)
    
    # If no extension provided, get it from the selected filter
    if not extension:
        default_ext = _extract_extension_from_filter(selected_filter)
        if default_ext:
            extension = f".{default_ext}"
            # Update filepath with the extension
            filepath = f"{base_path}{extension}"
        else:
            return False, "No file extension provided or determined from filter"
    
    file_format = extension[1:].lower()  # Remove the dot and convert to lowercase
    
    # Get crop rectangle if available
    crop_rect = main_window.viewer.get_saved_crop_rect() if main_window.viewer else None
    
    # List to store results
    results = []
    success_count = 0
    channel_names = ['r', 'g', 'b']
    
    # Save individual channel images with suffixes
    for idx, img in enumerate(main_window.aligned):
        if img is not None:
            # Apply crop if needed
            if crop_rect and crop_rect.isValid():
                img_to_save = apply_crop(img, crop_rect)
            else:
                img_to_save = img
                
            # Create filename with channel suffix
            channel_path = f"{base_path}_{channel_names[idx]}{extension}"
            success, message = save_image(img_to_save, channel_path, file_format)
            results.append((success, message))
            if success:
                success_count += 1
    
    # Create and save combined RGB image if at least one channel is available
    available_channels = [img is not None for img in main_window.aligned]
    if any(available_channels):
        # Initialize empty channels (all zeros)
        img_shape = None
        for img in main_window.aligned:
            if img is not None:
                img_shape = img.shape
                break
                
        if img_shape is not None:
            r_channel = np.zeros(img_shape, dtype=np.uint8)
            g_channel = np.zeros(img_shape, dtype=np.uint8)
            b_channel = np.zeros(img_shape, dtype=np.uint8)
            
            # Fill in available channels
            if main_window.aligned[0] is not None:  # Red
                if crop_rect and crop_rect.isValid():
                    r_channel = apply_crop(main_window.aligned[0], crop_rect)
                else:
                    r_channel = main_window.aligned[0]
                    
            if main_window.aligned[1] is not None:  # Green
                if crop_rect and crop_rect.isValid():
                    g_channel = apply_crop(main_window.aligned[1], crop_rect)
                else:
                    g_channel = main_window.aligned[1]
                    
            if main_window.aligned[2] is not None:  # Blue
                if crop_rect and crop_rect.isValid():
                    b_channel = apply_crop(main_window.aligned[2], crop_rect)
                else:
                    b_channel = main_window.aligned[2]
            
            # Combine RGB channels
            combined = cv2.merge([b_channel, g_channel, r_channel])  # BGR for OpenCV
            
            success, message = save_image(combined, filepath, file_format)
            results.append((success, message))
            if success:
                success_count += 1
    
    # Create a summary message
    if success_count == 0:
        return False, "Failed to save any images"
    elif success_count < len(results):
        return True, f"Saved {success_count} out of {len(results)} images"
    else:
        return True, f"Successfully saved all images to {os.path.dirname(filepath)}"


def save_image(
    image: np.ndarray,
    filepath: Optional[str] = None,
    file_format: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Save a NumPy array image to a file.

    Args:
        image: NumPy array containing the image data to save
        filepath: Path to save the file to. Required.
        file_format: Optional format override (e.g., 'jpg', 'png', 'tiff')

    Returns:
        Tuple containing:
            - Boolean indicating success or failure
            - String with filepath if successful, error message if failed
    """
    if image is None or image.size == 0:
        return False, "No image data to save"

    # Check if filepath is provided
    if filepath is None:
        return False, "No filepath provided"

    # Determine format from extension if not explicitly provided
    if file_format is None:
        _, extension = os.path.splitext(filepath)
        if not extension:
            return False, "No file extension provided and no format specified"
        file_format = extension[1:].lower()  # Remove the dot and convert to lowercase

    try:
        # Handle image format based on extension
        if file_format in ['jpg', 'jpeg']:
            success = cv2.imwrite(filepath, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        elif file_format == 'png':
            success = cv2.imwrite(filepath, image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        elif file_format in ['tif', 'tiff']:
            success = cv2.imwrite(filepath, image)
        else:
            # Default case - try to save with the given extension
            success = cv2.imwrite(filepath, image)

        if success:
            return True, filepath
        else:
            return False, f"Failed to save image to {filepath}"

    except Exception as e:
        return False, f"Error saving image: {str(e)}"
