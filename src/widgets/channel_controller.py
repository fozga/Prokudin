from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
from .sliders import ResetSlider

class ChannelController(QGroupBox):
    def __init__(self, channel_name, color, parent=None):
        super().__init__(parent)
        self.channel_name = channel_name
        self.color = color
        self.processed_image = None
        self.init_ui()

    def init_ui(self):
        self.setTitle(self.channel_name.capitalize())
        layout = QVBoxLayout()

        self.btn_load = QPushButton(f"Load {self.channel_name}")
        self.btn_load.setFixedSize(160, 30)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(160, 120)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray;")

        self.slider_brightness = self.create_slider(-100, 100, 0)
        self.slider_contrast = self.create_slider(-50, 50, 0)
        self.slider_intensity = self.create_slider(0, 200, 100)

        layout.addWidget(self.btn_load)
        layout.addWidget(self.preview_label)
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.slider_brightness)
        layout.addWidget(QLabel("Contrast:"))
        layout.addWidget(self.slider_contrast)
        layout.addWidget(QLabel("Intensity:"))
        layout.addWidget(self.slider_intensity)

        self.setFixedWidth(200)
        self.setLayout(layout)

    def create_slider(self, min_val, max_val, default):
        slider = ResetSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setFixedWidth(180)
        # Reset slider to default value on double-click
        slider.doubleClicked.connect(lambda: slider.setValue(default))
        return slider

    def update_preview(self):
        if self.processed_image is not None:
            preview = cv2.resize(self.processed_image, (160, 120))
            q_img = QImage(preview.data, preview.shape[1], preview.shape[0],
                           preview.strides[0], QImage.Format_Grayscale8)
            self.preview_label.setPixmap(QPixmap.fromImage(q_img))
