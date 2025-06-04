"""
Image loading utilities for RAW Sony ARW files.

This module provides functions to load and preprocess RAW images for use in the RGB Channel Processor application.

Cross-references:
    - handlers.channels: Uses load_raw_image for channel loading.
"""

import rawpy
import cv2
from PyQt5.QtWidgets import QFileDialog

def load_raw_image(parent):
    """
    Opens a file dialog for the user to select a Sony ARW RAW image,
    loads the image using rawpy, processes it to an 8-bit RGB image,
    and converts it to grayscale for further processing.

    Args:
        parent (QWidget): The parent widget for the QFileDialog (typically the main window).

    Returns:
        numpy.ndarray or None: 2D grayscale image as a NumPy array (dtype=uint8),
        or None if loading fails or is cancelled.

    Workflow:
        1. Opens a QFileDialog for ARW file selection.
        2. Loads the selected file with rawpy and applies camera white balance.
        3. Disables automatic brightness correction, outputs 8 bits per sample.
        4. Converts the resulting RGB image to grayscale using OpenCV.
        5. Handles errors gracefully, printing a message and returning None if needed.

    Example:
        gray_image = load_raw_image(self)
        if gray_image is not None:
            # Proceed with processing

    Cross-references:
        - handlers.channels.load_channel
    """
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(
        parent, "Select ARW File", "", 
        "Sony RAW Files (*.arw)", options=options)
    
    if not filename:
        return None
        
    try:
        with rawpy.imread(filename) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                no_auto_bright=True,
                output_bps=8
            )
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    except Exception as e:
        print(f"Error loading ARW file: {e}")
        return None
