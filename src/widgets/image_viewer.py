"""
Custom QGraphicsView widget for displaying and interacting with images,
including zoom, fit-to-view, and drag-to-pan functionality.
"""

from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QPainter, QPixmap, QResizeEvent, QWheelEvent
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget


class ImageViewer(QGraphicsView):
    """
    A custom graphics view for displaying and interacting with images.

    This widget provides features such as:
      - Displaying images with zoom and fit-to-view capabilities.
      - Smooth rendering and antialiasing.
      - Drag-to-pan functionality.
      - Mouse wheel zoom with Ctrl modifier.
      - Automatic scene rect and transformation management.

    Attributes:
        _zoom (float): Current zoom factor.
        _fit_to_view (bool): Whether the image is fit to the view.
        _scene (QGraphicsScene): The graphics scene containing the image.
        photo (QGraphicsPixmapItem): The pixmap item displaying the image.
    """

    def __init__(self, parent: Union[QWidget, None] = None) -> None:
        """
        Initializes the ImageViewer with default settings.

        Args:
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self._zoom = 1.0
        self._fit_to_view = False
        self._scene = QGraphicsScene(self)
        self.photo: Union[QGraphicsPixmapItem, None] = self._scene.addPixmap(QPixmap())
        self.setScene(self._scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def toggle_view(self) -> None:
        """
        Toggles between fit-to-view and manual zoom modes.

        - If toggled on, fits the image to the view while preserving aspect ratio.
        - If toggled off, resets any zoom or transformation.
        """
        self._fit_to_view = not self._fit_to_view
        if self._fit_to_view:
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = 1.0
        else:
            self.resetTransform()
            self._zoom = 1.0

    def set_image(self, pixmap: QPixmap) -> None:
        """
        Sets the displayed image.

        Args:
            pixmap (QPixmap): The image to display.

        Behavior:
            - Sets the pixmap in the scene.
            - Fits the image to the view.
            - Resets the zoom factor.
        """
        if self.photo is not None:
            self.photo.setPixmap(pixmap)
            self.fitInView(self.photo, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = 1.0

    def wheelEvent(self, event: Union[QWheelEvent, None]) -> None:  # pylint: disable=C0103
        """
        Handles mouse wheel events for zooming.

        - Holding Ctrl and using the wheel zooms in/out.
        - Exits fit-to-view mode on manual zoom.
        - Otherwise, passes the event to the base class.

        Args:
            event (QWheelEvent): The wheel event.
        """
        if event is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                zoom_factor = 1.25
                if event.angleDelta().y() > 0:
                    self.scale(zoom_factor, zoom_factor)
                    self._zoom *= zoom_factor
                    self._fit_to_view = False  # Exit fit-to-view on manual zoom
                else:
                    self.scale(1 / zoom_factor, 1 / zoom_factor)
                    self._zoom /= zoom_factor
                    self._fit_to_view = False
                event.accept()
            else:
                super().wheelEvent(event)
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event: Union[QResizeEvent, None]) -> None:  # pylint: disable=C0103
        """
        Handles widget resize events.

        - If in fit-to-view mode, refits the image to the new view size.

        Args:
            event (QResizeEvent): The resize event.
        """
        if self._fit_to_view:
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def mousePressEvent(self, event: Union[QMouseEvent, None]) -> None:  # pylint: disable=C0103
        """
        Handles mouse press events.

        - Enables scroll-hand drag mode on left mouse button press.

        Args:
            event (QMouseEvent): The mouse press event.
        """

        if event is not None:
            if event.button() == Qt.MouseButton.LeftButton:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: Union[QMouseEvent, None]) -> None:  # pylint: disable=C0103
        """
        Handles mouse release events.

        - Disables drag mode when the mouse is released.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)
