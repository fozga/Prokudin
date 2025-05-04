import cv2
import rawpy
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QSlider, QLabel
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPixmap

from widgets.image_viewer import ImageViewer
from widgets.channel_controller import ChannelController
from core.align import align_images

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
        self.red_controller = ChannelController("red", Qt.red)
        self.green_controller = ChannelController("green", Qt.green)
        self.blue_controller = ChannelController("blue", Qt.blue)

        controllers = [self.red_controller, self.green_controller, self.blue_controller]
        for idx, controller in enumerate(controllers):
            controller.btn_load.clicked.connect(lambda _, i=idx: self.load_raw_image(i))
            controller.slider_brightness.valueChanged.connect(
                lambda v, i=idx: self.adjust_channel(i))
            controller.slider_contrast.valueChanged.connect(
                lambda v, i=idx: self.adjust_channel(i))
            controller.slider_intensity.valueChanged.connect(
                lambda v, i=idx: self.adjust_channel(i))
            controller.preview_label.mousePressEvent = (
                lambda event, i=idx: self.show_single_channel(i))

        right_panel.addWidget(self.red_controller)
        right_panel.addWidget(self.green_controller)
        right_panel.addWidget(self.blue_controller)
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

    def load_raw_image(self, channel_idx):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select ARW File", "", 
            "Sony RAW Files (*.arw)", options=options)

        if filename:
            try:
                with rawpy.imread(filename) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=True,
                        output_bps=8
                    )
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                self.original_images[channel_idx] = gray.copy()
                self.processed[channel_idx] = gray.copy()

                # Check if all channels are loaded
                if all(img is not None for img in self.original_images):
                    self.aligned = align_images(self.original_images)
                    self.processed = [img.copy() for img in self.aligned]
                    for i in range(3):
                        self.update_channel_preview(i)
                else:
                    self.update_channel_preview(channel_idx)

                self.update_main_display()
            except Exception as e:
                print(f"Error loading ARW file: {e}")

    def adjust_channel(self, channel_idx):
        self.apply_adjustments(channel_idx)
        self.update_channel_preview(channel_idx)
        self.update_main_display()

    def apply_adjustments(self, channel_idx):
        if self.aligned[channel_idx] is None:
            return

        brightness = self.get_controller(channel_idx).slider_brightness.value()
        contrast = self.get_controller(channel_idx).slider_contrast.value() / 100

        img = self.aligned[channel_idx].astype(np.float32)
        img = img * (1 + contrast) + brightness
        self.processed[channel_idx] = np.clip(img, 0, 255).astype(np.uint8)

    def update_channel_preview(self, channel_idx):
        controller = self.get_controller(channel_idx)
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

        combined = np.zeros((*self.processed[0].shape, 3), dtype=np.float32)
        for i in range(3):
            intensity = self.get_controller(i).slider_intensity.value() / 100
            combined[:, :, i] = self.processed[i].astype(np.float32) * intensity

        combined = np.clip(combined, 0, 255).astype(np.uint8)
        q_img = QImage(combined.data, combined.shape[1], combined.shape[0],
                       combined.strides[0], QImage.Format_RGB888)
        self.viewer.set_image(QPixmap.fromImage(q_img))

    def show_single_channel_image(self):
        if self.processed[self.current_channel] is not None:
            img = cv2.cvtColor(self.processed[self.current_channel], cv2.COLOR_GRAY2RGB)
            q_img = QImage(img.data, img.shape[1], img.shape[0],
                           img.strides[0], QImage.Format_RGB888)
            self.viewer.set_image(QPixmap.fromImage(q_img))

    def get_controller(self, index):
        return [self.red_controller, self.green_controller, self.blue_controller][index]
