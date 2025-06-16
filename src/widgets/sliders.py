# pylint: disable=too-few-public-methods

"""
Custom slider widgets for the application's UI.
Provides a ResetSlider that emits a signal on double-click for quick reset functionality.
"""

from typing import Union

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent  # add this import
from PyQt5.QtWidgets import QSlider


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

    def mouseDoubleClickEvent(self, event: Union[QMouseEvent, None]) -> None:  # pylint: disable=C0103
        """
        Handles the mouse double-click event.

        Args:
            self (ResetSlider): The instance of the slider.
            event (QMouseEvent): The mouse double-click event.

        Returns:
            None

        Emits the doubleClicked signal and then calls the base class implementation.

        Args:
            event (QMouseEvent | None): The mouse double-click event.
        """
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
