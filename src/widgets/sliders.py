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

    def mouseDoubleClickEvent(self, event: Union[QMouseEvent, None]) -> None:  # pylint: disable=C0103
        """
        Handles the mouse double-click event.

        Emits the doubleClicked signal and then calls the base class implementation.

        Args:
            event (QMouseEvent | None): The mouse double-click event.
        """
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
