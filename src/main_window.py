from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap
import numpy as np

from widgets.image_viewer import ImageViewer
from widgets.channel_controller import ChannelController
from handlers.image_loading import load_raw_image
from core.align import align_images
from core.image_processing import apply_adjustments, combine_channels, convert_to_qimage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RGB Channel Processor")
        self.setGeometry(100, 100, 1200, 800)

        self.original_images = [None, None, None]
        self.aligned = [None, None, None]
        self.processed = [None, None, None]
        self.show_combined = True
        self.current_channel = 0

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.viewer = ImageViewer()
        main_layout.addWidget(self.viewer, 70)

        right_panel = QVBoxLayout()
        self.controllers = [
            ChannelController("red", Qt.red),
            ChannelController("green", Qt.green),
            ChannelController("blue", Qt.blue)
        ]

        for idx, controller in enumerate(self.controllers):
            controller.btn_load.clicked.connect(lambda _, i=idx: self.load_channel(i))
            controller.slider_brightness.valueChanged.connect(lambda v, i=idx: self.adjust_channel(i))
            controller.slider_contrast.valueChanged.connect(lambda v, i=idx: self.adjust_channel(i))
            controller.slider_intensity.valueChanged.connect(lambda v, i=idx: self.update_main_display())
            controller.preview_label.mousePressEvent = (lambda event, i=idx: self.show_single_channel(i))

            right_panel.addWidget(controller)
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 30)

        self.setCentralWidget(main_widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.show_combined = False
            self.current_channel = 0
            self.update_main_display()
            event.accept()
            return
        elif event.key() == Qt.Key_2:
            self.show_combined = False
            self.current_channel = 1
            self.update_main_display()
            event.accept()
            return
        elif event.key() == Qt.Key_3:
            self.show_combined = False
            self.current_channel = 2
            self.update_main_display()
            event.accept()
            return
        elif event.key() == Qt.Key_A:
            self.show_combined = True
            self.update_main_display()
            event.accept()
            return
        super().keyPressEvent(event)

    def load_channel(self, channel_idx):
        image = load_raw_image(self)
        if image is not None:
            self.original_images[channel_idx] = image
            self.processed[channel_idx] = image.copy()
            if all(img is not None for img in self.original_images):
                self.aligned = align_images(self.original_images)
                self.processed = [img.copy() for img in self.aligned]
                for i in range(3):
                    self.update_channel_preview(i)
            else:
                self.update_channel_preview(channel_idx)
            self.update_main_display()

    def adjust_channel(self, channel_idx):
        if self.aligned[channel_idx] is not None:
            brightness = self.controllers[channel_idx].slider_brightness.value()
            contrast = self.controllers[channel_idx].slider_contrast.value()
            self.processed[channel_idx] = apply_adjustments(self.aligned[channel_idx], brightness, contrast)
            self.update_channel_preview(channel_idx)
            self.update_main_display()

    def update_channel_preview(self, channel_idx):
        controller = self.controllers[channel_idx]
        controller.processed_image = self.processed[channel_idx]
        controller.update_preview()

    def show_single_channel(self, channel_idx):
        self.show_combined = False
        self.current_channel = channel_idx
        self.update_main_display()

    def update_main_display(self):
        if self.show_combined:
            self.show_combined_image()
        else:
            self.show_single_channel_image()

        if self.viewer._photo.pixmap():
            pixmap = self.viewer._photo.pixmap()
            self.viewer.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))

    def show_combined_image(self):
        if any(img is None for img in self.processed):
            return
        intensities = [ctrl.slider_intensity.value() for ctrl in self.controllers]
        combined = combine_channels(self.processed, intensities)
        q_img = convert_to_qimage(combined)
        self.viewer.set_image(QPixmap.fromImage(q_img))

    def show_single_channel_image(self):
        img = self.processed[self.current_channel]
        if img is not None:
            rgb_img = np.stack([img]*3, axis=-1)
            q_img = convert_to_qimage(rgb_img)
            self.viewer.set_image(QPixmap.fromImage(q_img))
