import numpy as np
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPixmap
from core.image_processing import combine_channels, convert_to_qimage

def update_main_display(main_window):
    if main_window.show_combined:
        show_combined_image(main_window)
    else:
        show_single_channel_image(main_window)

    if main_window.viewer._photo.pixmap():
        pixmap = main_window.viewer._photo.pixmap()
        main_window.viewer.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))

def show_combined_image(main_window):
    if any(img is None for img in main_window.processed):
        return
    intensities = [ctrl.slider_intensity.value() for ctrl in main_window.controllers]
    combined = combine_channels(main_window.processed, intensities)
    q_img = convert_to_qimage(combined)
    main_window.viewer.set_image(QPixmap.fromImage(q_img))

def show_single_channel_image(main_window):
    img = main_window.processed[main_window.current_channel]
    if img is not None:
        rgb_img = np.stack([img]*3, axis=-1)
        q_img = convert_to_qimage(rgb_img)
        main_window.viewer.set_image(QPixmap.fromImage(q_img))
