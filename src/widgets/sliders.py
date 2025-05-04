from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import pyqtSignal

class ResetSlider(QSlider):
    """Slider with double-click reset functionality"""
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
