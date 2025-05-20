"""
Custom slider widget for the RGB Channel Processor application.

This module defines the ResetSlider class, a QSlider subclass that emits a signal on double-click for quick reset functionality.
"""
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import pyqtSignal

class ResetSlider(QSlider):
    """
    A QSlider subclass that emits a custom signal on double-click.

    This slider is intended for use in UI scenarios where the user may want to
    quickly reset the slider to a default value by double-clicking it.

    Signals:
        doubleClicked: Emitted when the slider is double-clicked with the mouse.
    """
    doubleClicked = pyqtSignal()
    """
    Signal emitted when the slider is double-clicked.
    Can be connected to a slot to reset the slider or perform other actions.
    """

    def mouseDoubleClickEvent(self, event):
        """
        Handles the mouse double-click event.

        Emits the doubleClicked signal and then calls the base class implementation.

        Args:
            event (QMouseEvent): The mouse double-click event.
        """
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
