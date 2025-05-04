from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import pyqtSignal

class ResetSlider(QSlider):
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
