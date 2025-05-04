from handlers.image_loading import load_raw_image
from core.align import align_images
from core.image_processing import apply_adjustments
from handlers.display import update_main_display

def load_channel(main_window, channel_idx):
    image = load_raw_image(main_window)
    if image is not None:
        main_window.original_images[channel_idx] = image
        main_window.processed[channel_idx] = image.copy()
        if all(img is not None for img in main_window.original_images):
            main_window.aligned = align_images(main_window.original_images)
            main_window.processed = [img.copy() for img in main_window.aligned]
            for i in range(3):
                update_channel_preview(main_window, i)
        else:
            update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)

def adjust_channel(main_window, channel_idx):
    if main_window.aligned[channel_idx] is not None:
        brightness = main_window.controllers[channel_idx].slider_brightness.value()
        contrast = main_window.controllers[channel_idx].slider_contrast.value()
        main_window.processed[channel_idx] = apply_adjustments(
            main_window.aligned[channel_idx], brightness, contrast
        )
        update_channel_preview(main_window, channel_idx)
        update_main_display(main_window)

def update_channel_preview(main_window, channel_idx):
    controller = main_window.controllers[channel_idx]
    controller.processed_image = main_window.processed[channel_idx]
    controller.update_preview()

def show_single_channel(main_window, channel_idx):
    main_window.show_combined = False
    main_window.current_channel = channel_idx
    update_main_display(main_window)
