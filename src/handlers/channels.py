"""
Channel handling utilities for the RGB Channel Processor.

Cross-references:
    - handlers.image_loading: RAW image loading.
    - core.align: Channel alignment.
    - core.image_processing: Channel adjustments.
    - handlers.display: Main display update.
    - widgets.channel_controller.ChannelController: Per-channel UI.
"""

from handlers.image_loading import load_raw_image
from core.align import align_images
from core.image_processing import apply_adjustments
from handlers.display import update_main_display

def load_channel(main_window, channel_idx):
    """
    Loads a raw image file for the specified color channel, updates the application's state,
    and triggers alignment and preview updates.

    Args:
        main_window (QMainWindow): Reference to the main application window containing image state and UI.
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
        main_window (QMainWindow): Reference to the main application window.
        channel_idx (int): Index of the channel to adjust (0=R, 1=G, 2=B).

    Returns:
        None

    Cross-references:
        - apply_adjustments
        - update_channel_preview
        - update_main_display
    """
    if main_window.aligned[channel_idx] is not None:
        brightness = main_window.controllers[channel_idx].slider_brightness.value()
        contrast = main_window.controllers[channel_idx].slider_contrast.value()
        main_window.processed[channel_idx] = apply_adjustments(
            main_window.aligned[channel_idx], brightness, contrast
        )
        update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)

def update_channel_preview(main_window, channel_idx):
    """
    Updates the preview image for a specific channel controller.

    Args:
        main_window (QMainWindow): Reference to the main application window.
        channel_idx (int): Index of the channel to update (0=R, 1=G, 2=B).

    Returns:
        None

    Cross-references:
        - ChannelController.update_preview
    """
    controller = main_window.controllers[channel_idx]
    controller.processed_image = main_window.processed[channel_idx]
    controller.update_preview()

def show_single_channel(main_window, channel_idx):
    """
    Updates the main window to display a single channel.

    This function sets the main window to show only the specified channel
    by disabling the combined view and updating the current channel index.
    It then refreshes the main display to reflect the changes.

    Args:
        main_window (QMainWindow): The main application window object that contains the display and state information.
        channel_idx (int): The index of the channel to be displayed.

    Returns:
        None

    Cross-references:
        - update_main_display
    """
    main_window.show_combined = False
    main_window.current_channel = channel_idx
    update_main_display(main_window)
