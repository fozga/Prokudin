"""
Custom slider widget for the RGB Channel Processor application.

This module defines the ResetSlider class, a QSlider subclass that emits a signal on double-click for quick reset functionality.

Cross-references:
    - widgets.channel_controller.ChannelController: Uses ResetSlider for channel adjustments.
"""

from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import pyqtSignal

class ResetSlider(QSlider):
    """
    QSlider subclass with double-click reset functionality.

    Cross-references:
        - ChannelController: Used for brightness, contrast, intensity sliders.
    """
    doubleClicked = pyqtSignal()
    """
    Signal emitted when the slider is double-clicked.
    Can be connected to a slot to reset the slider or perform other actions.
    """

    def mouseDoubleClickEvent(self, event):
        """
        Handles the mouse double-click event.

        Args:
            self (ResetSlider): The instance of the slider.
            event (QMouseEvent): The mouse double-click event.

        Returns:
            None

        Emits the doubleClicked signal and then calls the base class implementation.

        Args:
            event (QMouseEvent): The mouse double-click event.
        """
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
