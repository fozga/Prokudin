from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPixmap

class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1.0
        self._fit_to_view = False
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(QPixmap())
        self.setScene(self._scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def toggle_view(self):
        """Toggle between fit-to-view and original size"""
        self._fit_to_view = not self._fit_to_view
        if self._fit_to_view:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            self._zoom = 1.0
        else:
            self.resetTransform()
            self._zoom = 1.0

    def set_image(self, pixmap):
        self._photo.setPixmap(pixmap)
        self.fitInView(self._photo, Qt.KeepAspectRatio)
        self._zoom = 1.0

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            zoom_factor = 1.25
            if event.angleDelta().y() > 0:
                self.scale(zoom_factor, zoom_factor)
                self._zoom *= zoom_factor
                self._fit_to_view = False  # Exit fit-to-view on manual zoom
            else:
                self.scale(1/zoom_factor, 1/zoom_factor)
                self._zoom /= zoom_factor
                self._fit_to_view = False
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        if self._fit_to_view:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)
