"""
Channel controller widget for RGB channel adjustment and preview in the UI.
"""

from typing import Union

import cv2  # type: ignore
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget

from .sliders import ResetSlider


class ChannelController(QGroupBox):
    """
    UI component for controlling a single RGB channel.

    This widget provides controls for loading an image channel, adjusting its
    brightness, contrast, and intensity, and displaying a live preview of the
    processed channel.

    Attributes:
        channel_name (str): Name of the channel ('red', 'green', or 'blue').
        color (Qt.GlobalColor): Qt color constant for the channel.
        processed_image (numpy.ndarray or None): The current processed image for preview.
        btn_load (QPushButton): Button to load the channel image.
        preview_label (QLabel): Label showing the preview image.
        slider_brightness (ResetSlider): Slider for brightness adjustment.
        slider_contrast (ResetSlider): Slider for contrast adjustment.
        slider_intensity (ResetSlider): Slider for intensity adjustment.
    """

    def __init__(self, channel_name: str, color: Qt.GlobalColor, parent: Union[QWidget, None] = None) -> None:
        """
        Initializes the channel controller UI and its state.

        Args:
            channel_name (str): Name of the channel ('red', 'green', 'blue').
            color (Qt.GlobalColor): Qt color constant representing the channel.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self.channel_name = channel_name
        self.color = color
        self.processed_image: Union[np.ndarray, None] = None
        self.init_ui()

    def init_ui(self) -> None:
        """
        Sets up the layout, widgets, and sliders for the channel controller.
        """
        self.setTitle(self.channel_name.capitalize())
        layout = QVBoxLayout()

        # Button to load the channel image
        self.btn_load = QPushButton(f"Load {self.channel_name}")
        self.btn_load.setFixedSize(160, 30)

        # Preview area for the processed image
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(160, 120)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray;")

        # Sliders for brightness, contrast, and intensity stored in a dictionary
        self.sliders = {
            "brightness": self.create_slider(-100, 100, 0),
            "contrast": self.create_slider(-50, 50, 0),
            "intensity": self.create_slider(0, 200, 100),
        }

        layout.addWidget(self.btn_load)
        layout.addWidget(self.preview_label)
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.sliders["brightness"])
        layout.addWidget(QLabel("Contrast:"))
        layout.addWidget(self.sliders["contrast"])
        layout.addWidget(QLabel("Intensity:"))
        layout.addWidget(self.sliders["intensity"])

        self.setFixedWidth(200)
        self.setLayout(layout)

    def create_slider(self, min_val: int, max_val: int, default: int) -> ResetSlider:
        """
        Creates a horizontal slider with the specified range and default value.
        The slider resets to the default value on double-click.

        Args:
            min_val (int): Minimum slider value.
            max_val (int): Maximum slider value.
            default (int): Default value for the slider.

        Returns:
            ResetSlider: Configured slider widget.
        """
        slider = ResetSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setFixedWidth(180)
        # Reset slider to default value on double-click
        slider.doubleClicked.connect(lambda: slider.setValue(default))
        return slider

    def update_preview(self) -> None:
        """
        Updates the preview label with the current processed image.

        The image is resized to fit the preview area (160x120) and converted to a QPixmap.
        """
        if self.processed_image is not None:
            preview = cv2.resize(self.processed_image, (160, 120))  # pylint: disable=E1101
            q_img = QImage(
                preview.data, preview.shape[1], preview.shape[0], preview.strides[0], QImage.Format_Grayscale8
            )
            self.preview_label.setPixmap(QPixmap.fromImage(q_img))
