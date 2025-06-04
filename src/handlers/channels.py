"""
Handlers for loading, adjusting, and displaying individual color channels in the application.
Provides functions to load raw images, apply adjustments, update previews, and manage display modes.
"""

from core.align import align_images
from core.image_processing import apply_adjustments
from handlers.display import update_main_display
from handlers.image_loading import load_raw_image


def load_channel(main_window, channel_idx):
    """
    Loads a raw image file for the specified color channel, updates the application's state,
    and triggers alignment and preview updates.

    Args:
        main_window: Reference to the main application window containing image state and UI.
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
        main_window.original_images[channel_idx] = image
        main_window.processed[channel_idx] = image.copy()
        if all(img is not None for img in main_window.original_images):
            main_window.aligned = align_images(main_window.original_images)
            main_window.processed = [img.copy() for img in main_window.aligned]
            for i in range(3):
                adjust_channel(main_window, i)
                update_channel_preview(main_window, i)
        else:
            update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)


def adjust_channel(main_window, channel_idx):
    """
    Applies brightness and contrast adjustments to the specified channel and updates its preview.

    Args:
        main_window: Reference to the main application window.
        channel_idx (int): Index of the channel to adjust (0=R, 1=G, 2=B).

    Behavior:
        - Reads brightness and contrast values from the channel's sliders.
        - Applies adjustments to the aligned image for this channel.
        - Updates the processed image, channel preview, and main display.
    """
    if main_window.aligned[channel_idx] is not None:
        brightness = main_window.controllers[channel_idx].slider_brightness.value()
        contrast = main_window.controllers[channel_idx].slider_contrast.value()
        main_window.processed[channel_idx] = apply_adjustments(main_window.aligned[channel_idx], brightness, contrast)
        update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)


def update_channel_preview(main_window, channel_idx):
    """
    Updates the preview image for a specific channel controller.

    Args:
        main_window: Reference to the main application window.
        channel_idx (int): Index of the channel to update (0=R, 1=G, 2=B).

    Behavior:
        - Sets the processed image for the channel controller.
        - Refreshes the preview display in the UI.
    """
    controller = main_window.controllers[channel_idx]
    controller.processed_image = main_window.processed[channel_idx]
    controller.update_preview()


def show_single_channel(main_window, channel_idx):
    """
    Switches the main display to show only a single color channel.

    Args:
        main_window: Reference to the main application window.
        channel_idx (int): Index of the channel to display (0=R, 1=G, 2=B).

    Behavior:
        - Sets the display mode to single-channel.
        - Updates the main display to reflect the change.
    """
    main_window.show_combined = False
    main_window.current_channel = channel_idx
    update_main_display(main_window)
