"""
Display handler utilities for updating the main image viewer in the application.

This module provides functions to update the main display area, showing either the combined RGB image or a single channel, with support for cropping and intensity adjustments.
"""
import numpy as np
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap
from core.image_processing import combine_channels, convert_to_qimage

def update_main_display(main_window):
    """
    Updates the main display of the application based on the current state of the main window.

    This function determines whether to display a combined image or a single channel image
    depending on the `show_combined` attribute of the `main_window`. It also adjusts the
    scene rectangle of the viewer to match the dimensions of the displayed pixmap, if available.

    Args:
        main_window: The main window object containing the display settings and viewer.
    """
    if main_window.show_combined:
        show_combined_image(main_window)
    else:
        show_single_channel_image(main_window)

    if main_window.viewer._photo.pixmap():
        pixmap = main_window.viewer._photo.pixmap()
        main_window.viewer.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))

def show_combined_image(main_window):
    """
    Displays the combined RGB image in the main viewer.

    Combines the three processed channels using their respective intensity slider values,
    converts the result to a QImage, and sets it in the viewer.

    Args:
        main_window: Reference to the main application window.
    """
    if any(img is None for img in main_window.processed):
        return

    # If not in crop mode and a crop rectangle is set, crop the processed images on-the-fly
    crop_rect = getattr(main_window.viewer, '_saved_crop_rect', None)
    if not main_window.crop_mode and crop_rect is not None:
        cropped_channels = []
        for img in main_window.processed:
            if img is not None:
                cropped = img[crop_rect.top():crop_rect.bottom()+1, crop_rect.left():crop_rect.right()+1]
                cropped_channels.append(cropped)
            else:
                cropped_channels.append(None)
        intensities = [ctrl.slider_intensity.value() for ctrl in main_window.controllers]
        combined = combine_channels(cropped_channels, intensities)
        q_img = convert_to_qimage(combined)
        main_window.viewer.set_image(QPixmap.fromImage(q_img))
        return

    # Otherwise use full images
    intensities = [ctrl.slider_intensity.value() for ctrl in main_window.controllers]
    combined = combine_channels(main_window.processed, intensities)
    q_img = convert_to_qimage(combined)
    main_window.viewer.set_image(QPixmap.fromImage(q_img))

def show_single_channel_image(main_window):
    """
    Displays a single selected channel as a grayscale image in the main viewer.

    The selected channel is duplicated across RGB for display purposes, converted to QImage,
    and shown in the viewer.

    Args:
        main_window: Reference to the main application window.
    """
    img = main_window.processed[main_window.current_channel]
    if img is not None:
        # If not in crop mode and a crop rectangle is set, crop the processed image on-the-fly
        crop_rect = getattr(main_window.viewer, '_saved_crop_rect', None)
        if not main_window.crop_mode and crop_rect is not None:
            cropped = img[crop_rect.top():crop_rect.bottom()+1, crop_rect.left():crop_rect.right()+1]
            img = cropped
        rgb_img = np.stack([img]*3, axis=-1)
        q_img = convert_to_qimage(rgb_img)
        main_window.viewer.set_image(QPixmap.fromImage(q_img))
