"""
Handlers for loading, adjusting, and displaying individual color channels in the application.
Provides functions to load raw images, apply adjustments, update previews, and manage display modes.
"""

from __future__ import annotations

# Standard library imports
from typing import TYPE_CHECKING, List

# Third-party imports
import numpy as np

# Conditional imports for type checking
if TYPE_CHECKING:
    from ..main_window import MainWindow

# Local application imports
from ..core.align import align_images
from ..core.image_processing import apply_adjustments
from .display import update_main_display
from .image_loading import load_raw_image


def load_channel(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Loads a raw image file for the specified color channel, updates the application's state,
    and triggers alignment and preview updates.

    Args:
        main_window (MainWindow): Reference to the main application window containing image state and UI.
        channel_idx (int): Index of the channel to load (0=R, 1=G, 2=B).

    Behavior:
        - Opens a file dialog for the user to select a RAW image.
        - Stores the loaded image in main_window.original_images and main_window.processed.
        - If all three channels are loaded, aligns all channels and updates previews for each.
        - Otherwise, updates the preview for the loaded channel only.
        - Updates the main display after loading.
    """
    image = load_raw_image(main_window)
    if image is not None:
        # Create new lists with proper type annotations to avoid assignment issues
        original_images: List[np.ndarray | None] = list(main_window.original_images)
        processed: List[np.ndarray | None] = list(main_window.processed)

        original_images[channel_idx] = image
        processed[channel_idx] = image.copy()

        # Assign back to main_window
        main_window.original_images = original_images  # type: ignore
        main_window.processed = processed  # type: ignore

        if all(img is not None for img in main_window.original_images):
            aligned = align_images(main_window.original_images)
            main_window.aligned = aligned  # type: ignore

            # Create new list with copies of aligned images, handling None values
            new_processed: List[np.ndarray | None] = []
            for img in aligned:
                if img is not None:
                    new_processed.append(img.copy())
                else:
                    new_processed.append(None)

            main_window.processed = new_processed  # type: ignore

            for i in range(3):
                adjust_channel(main_window, i)
                update_channel_preview(main_window, i)
        else:
            update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)


def adjust_channel(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Applies brightness and contrast adjustments to the specified channel and updates its preview.

    Args:
        main_window ("MainWindow"): Reference to the main application window.
        channel_idx (int): Index of the channel to adjust (0=R, 1=G, 2=B).

    Behavior:
        - Reads brightness and contrast values from the channel's sliders.
        - Applies adjustments to the aligned image for this channel.
        - Updates the processed image, channel preview, and main display.
    """
    if main_window.aligned[channel_idx] is not None:
        brightness: int = main_window.controllers[channel_idx].slider_brightness.value()
        contrast: int = main_window.controllers[channel_idx].slider_contrast.value()
        result = apply_adjustments(main_window.aligned[channel_idx], brightness, contrast)
        if result is not None:
            # Create a new list to avoid assignment issues
            processed: List[np.ndarray | None] = list(main_window.processed)
            processed[channel_idx] = result
            main_window.processed = processed  # type: ignore

            update_channel_preview(main_window, channel_idx)
            update_main_display(main_window)


def update_channel_preview(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Updates the preview image for a specific channel controller.

    Args:
        main_window ("MainWindow"): Reference to the main application window.
        channel_idx (int): Index of the channel to update (0=R, 1=G, 2=B).

    Behavior:
        - Sets the processed image for the channel controller.
        - Refreshes the preview display in the UI.
    """
    controller = main_window.controllers[channel_idx]
    controller.processed_image = main_window.processed[channel_idx]
    controller.update_preview()


def show_single_channel(main_window: "MainWindow", channel_idx: int) -> None:
    """
    Switches the main display to show only a single color channel.

    Args:
        main_window ("MainWindow"): Reference to the main application window.
        channel_idx (int): Index of the channel to display (0=R, 1=G, 2=B).

    Behavior:
        - Sets the display mode to single-channel.
        - Updates the main display to reflect the change.
    """
    main_window.show_combined = False
    main_window.current_channel = channel_idx
    update_main_display(main_window)
