"""
Channel controller widget for RGB channel adjustment and preview in the UI.
"""

from typing import Union

import cv2  # type: ignore
import numpy as np
from PyQt5.QtCore import Qt, QRect
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
        processed_image (Union[numpy.ndarray, None]): The current processed image for preview.
        btn_load (QPushButton): Button to load the channel image.
        preview_label (QLabel): Label showing the preview image.
        sliders (dict[str, ResetSlider]): Dictionary containing sliders for brightness, contrast, and intensity.

    Methods:
        init_ui(): Sets up the layout, widgets, and sliders for the channel controller.
        create_slider(min_val: int, max_val: int, default: int) -> ResetSlider: Creates a configured slider widget.
        update_preview(): Updates the preview label with the current processed image.

    Cross-references:
        - main_window.MainWindow: Used for each channel.
        - handlers.channels: Connected to channel logic.
    """

    def __init__(self, channel_name: str, color: Qt.GlobalColor, parent: Union[QWidget, None] = None) -> None:
        """
        Initializes the channel controller UI and its state.

        Args:
            channel_name (str): Name of the channel ('red', 'green', 'blue').
            color (Qt.GlobalColor): Qt color constant representing the channel.
            parent (QWidget, optional): Parent widget.

        Returns:
            None
        """
        super().__init__(parent)
        self.channel_name = channel_name
        self.color = color
        self.processed_image: Union[np.ndarray, None] = None
        self.init_ui()

    def init_ui(self) -> None:
        """
        Sets up the layout, widgets, and sliders for the channel controller.

        Args:
            self (ChannelController): The instance of the channel controller.

        Returns:
            None
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

        Args:
            self (ChannelController): The instance of the channel controller.

        Returns:
            None
        """
        if self.processed_image is not None:
            # Create a copy of the image to avoid potential reference issues
            preview_img = self.processed_image.copy()
            
            # Get the crop rectangle from the parent's viewer if possible
            parent = self.parent()
            while parent:
                if hasattr(parent, 'viewer') and hasattr(parent.viewer, 'get_saved_crop_rect'):
                    saved_crop_rect = parent.viewer.get_saved_crop_rect()
                    if saved_crop_rect and not getattr(parent, 'crop_mode', False):
                        # Apply crop on-the-fly for previews too
                        h, w = preview_img.shape[:2]
                        valid_rect = QRect(0, 0, w, h).intersected(saved_crop_rect)
                        if valid_rect.isValid() and valid_rect.width() > 0 and valid_rect.height() > 0:
                            preview_img = preview_img[
                                valid_rect.top():valid_rect.bottom()+1,
                                valid_rect.left():valid_rect.right()+1
                            ].copy()
                    break
                parent = parent.parent()
                
            # Resize while preserving aspect ratio
            h, w = preview_img.shape[:2]
            aspect = w / h
            
            if aspect > 160/120:  # Width-constrained
                new_w = 160
                new_h = int(new_w / aspect)
            else:  # Height-constrained
                new_h = 120
                new_w = int(new_h * aspect)
                
            preview = cv2.resize(preview_img, (new_w, new_h))  # pylint: disable=E1101
            
            # Create QImage directly from the numpy array
            q_img = QImage(
                preview.data, preview.shape[1], preview.shape[0], preview.strides[0], QImage.Format_Grayscale8
            )
            self.preview_label.setPixmap(QPixmap.fromImage(q_img))
