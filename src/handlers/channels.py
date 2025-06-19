# Copyright (C) 2025 fozga
#
# This file is part of FullSpectrumProcessor.
#
# FullSpectrumProcessor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FullSpectrumProcessor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FullSpectrumProcessor.  If not, see <https://www.gnu.org/licenses/>.

"""
Handlers for loading, adjusting, and displaying individual color channels in the application.
Provides functions to load raw images, apply adjustments, update previews, and manage display modes.
"""

from __future__ import annotations

# Standard library imports
from typing import TYPE_CHECKING, List, Optional, cast

# Third-party imports
import cv2
import numpy as np

# Conditional imports for type checking
if TYPE_CHECKING:
    from ..main_window import MainWindow

# Local application imports
from ..core.align import align_images
from ..core.image_processing import apply_adjustments
from .display import update_main_display
from .image_loading import load_raw_image


def load_channel(main_window: "MainWindow", channel_idx: int) -> None:  # pylint: disable=too-many-locals
    """
    Loads a raw image file for the specified color channel, updates the application's state,
    and triggers alignment and preview updates.

    Args:
        main_window (MainWindow): Reference to the main application window containing image state and UI.
        channel_idx (int): Index of the channel to load (0=R, 1=G, 2=B).

    Returns:
        None

    Cross-references:
        - load_raw_image
        - align_images
        - adjust_channel
        - update_channel_preview
        - update_main_display
    """
    # Channel names for status messages
    channel_names = {0: "Red", 1: "Green", 2: "Blue"}
    channel_name = channel_names.get(channel_idx, "Unknown")

    # Load the RGB image
    rgb_image = load_raw_image(main_window)

    if rgb_image is not None:
        # Create a new list to avoid assignment issues
        original_rgb_images: List[Optional[np.ndarray]] = list(main_window.original_rgb_images)
        original_rgb_images[channel_idx] = rgb_image
        main_window.original_rgb_images = original_rgb_images  # type: ignore

        # Convert RGB to grayscale
        image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)  # pylint: disable=E1101

        # Create new lists with proper type annotations to avoid assignment issues
        original_images: List[Optional[np.ndarray]] = list(main_window.original_images)
        processed: List[Optional[np.ndarray]] = list(main_window.processed)

        original_images[channel_idx] = image
        processed[channel_idx] = image.copy()

        # Assign back to main_window
        main_window.original_images = original_images  # type: ignore
        main_window.processed = processed  # type: ignore

        # Display status message showing which channel was loaded
        main_window.status_handler.set_message(f"Successfully loaded image into {channel_name} channel", 3000)

        if all(img is not None for img in main_window.original_images):
            # Create arrays of ndarray images only, with explicit type casting for mypy
            gray_images: List[np.ndarray] = []
            rgb_images: List[np.ndarray] = []

            # Only include non-None images and cast them to numpy arrays
            for i in range(3):
                if main_window.original_images[i] is not None and main_window.original_rgb_images[i] is not None:
                    gray_img = cast(np.ndarray, main_window.original_images[i])
                    rgb_img = cast(np.ndarray, main_window.original_rgb_images[i])
                    gray_images.append(gray_img)
                    rgb_images.append(rgb_img)

            # Ensure we have exactly 3 images for each channel
            if len(gray_images) == 3 and len(rgb_images) == 3:
                # Align both grayscale and RGB images
                main_window.status_handler.set_message("Aligning images, please wait...")
                aligned_gray, aligned_rgb = align_images(gray_images, rgb_images)

                # Store aligned grayscale images
                main_window.aligned = aligned_gray  # type: ignore

                # Store aligned RGB images
                main_window.aligned_rgb = aligned_rgb  # type: ignore

                # Create new list with copies of aligned images
                new_processed: List[Optional[np.ndarray]] = []
                for img in aligned_gray:
                    new_processed.append(img.copy())

                main_window.processed = new_processed  # type: ignore

                for i in range(3):
                    adjust_channel(main_window, i)
                    update_channel_preview(main_window, i)
                main_window.status_handler.set_message("All channels loaded successfully - Ready for editing!", 3000)
        else:
            update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)

        # After successfully loading a channel, update save button state
        main_window.update_save_button_state()
    else:
        # Display error message if loading failed
        main_window.status_handler.set_message(f"Failed to load image for {channel_name} channel", 3000)


def adjust_channel(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Applies brightness and contrast adjustments to the specified channel and updates its preview.

    Args:
        main_window ("MainWindow"): Reference to the main application window.
        channel_idx (int): Index of the channel to adjust (0=R, 1=G, 2=B).

    Returns:
        None

    Cross-references:
        - apply_adjustments
        - update_channel_preview
        - update_main_display
    """
    if main_window.aligned[channel_idx] is not None:
        main_window.status_handler.set_message("Processing image, please wait...")
        brightness: int = main_window.controllers[channel_idx].sliders["brightness"].value()
        contrast: int = main_window.controllers[channel_idx].sliders["contrast"].value()
        result = apply_adjustments(main_window.aligned[channel_idx], brightness, contrast)
        if result is not None:
            # Create a new list to avoid assignment issues
            processed: List[Optional[np.ndarray]] = list(main_window.processed)
            processed[channel_idx] = result
            main_window.processed = processed  # type: ignore

            update_channel_preview(main_window, channel_idx)
            update_main_display(main_window)
            main_window.statusBar().clearMessage()


def update_channel_preview(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Updates the preview image for a specific channel controller.

    Args:
        main_window ("MainWindow"): Reference to the main application window.
        channel_idx (int): Index of the channel to update (0=R, 1=G, 2=B).

    Returns:
        None

    Cross-references:
        - ChannelController.update_preview
    """
    controller = main_window.controllers[channel_idx]
    controller.processed_image = main_window.processed[channel_idx]
    controller.update_preview()


def show_single_channel(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Updates the main window to display a single channel.

    This function sets the main window to show only the specified channel
    by disabling the combined view and updating the current channel index.
    It then refreshes the main display to reflect the changes.

    Args:
        main_window ("MainWindow"): Reference to the main application window.
        channel_idx (int): Index of the channel to display (0=R, 1=G, 2=B).

    Returns:
        None

    Cross-references:
        - update_main_display
    """
    main_window.show_combined = False
    main_window.current_channel = channel_idx
    update_main_display(main_window)
