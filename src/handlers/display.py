"""
Display handlers for updating the main image view and channel previews in the application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, cast

import numpy as np
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap

if TYPE_CHECKING:
    from ..main_window import MainWindow

from ..core.image_processing import combine_channels, convert_to_qimage


def update_main_display(main_window: "MainWindow") -> None:
    """
    Updates the main display of the application based on the current state of the main window.

    Args:
        main_window (QMainWindow): The main window object containing the display settings and viewer.

    Returns:
        None
    """
    if main_window.show_combined:
        show_combined_image(main_window)
    else:
        show_single_channel_image(main_window)

    # Add null check before accessing pixmap()
    if main_window.viewer.photo is not None and main_window.viewer.photo.pixmap():
        pixmap = main_window.viewer.photo.pixmap()
        main_window.viewer.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))


def show_combined_image(main_window: "MainWindow") -> None:
    """
    Displays the combined RGB image in the main viewer.

    Args:
        main_window (QMainWindow): Reference to the main application window.

    Returns:
        None
    """
    if any(img is None for img in main_window.processed):
        return

    # If not in crop mode and a crop rectangle is set, crop the processed images on-the-fly
    crop_rect = getattr(main_window.viewer, "_saved_crop_rect", None)
    if not main_window.crop_mode and crop_rect is not None:
        cropped_channels: List[np.ndarray | None] = []
        for img in main_window.processed:
            if img is not None:
                cropped = img[crop_rect.top(): crop_rect.bottom() + 1, crop_rect.left(): crop_rect.right() + 1]
                cropped_channels.append(cropped)
            else:
                cropped_channels.append(None)
        intensities = [ctrl.sliders["intensity"].value() for ctrl in main_window.controllers]
        combined = combine_channels(cropped_channels, intensities)
        q_img = convert_to_qimage(combined)
        main_window.viewer.set_image(QPixmap.fromImage(q_img))
        return

    # Otherwise use full images
    channels = cast(List[np.ndarray | None], main_window.processed)
    intensities = [ctrl.sliders["intensity"].value() for ctrl in main_window.controllers]
    combined = combine_channels(channels, intensities)
    q_img = convert_to_qimage(combined)
    main_window.viewer.set_image(QPixmap.fromImage(q_img))


def show_single_channel_image(main_window: "MainWindow") -> None:
    """
    Displays a single selected channel as a grayscale image in the main viewer.

    Args:
        main_window (QMainWindow): Reference to the main application window.

    Returns:
        None
    """
    img = main_window.processed[main_window.current_channel]
    if img is not None:
        # If not in crop mode and a crop rectangle is set, crop the processed image on-the-fly
        crop_rect = getattr(main_window.viewer, "_saved_crop_rect", None)
        if not main_window.crop_mode and crop_rect is not None:
            cropped = img[crop_rect.top(): crop_rect.bottom() + 1, crop_rect.left(): crop_rect.right() + 1]
            img = cropped
        rgb_img = np.stack([img] * 3, axis=-1)
        q_img = convert_to_qimage(rgb_img)
        main_window.viewer.set_image(QPixmap.fromImage(q_img))
