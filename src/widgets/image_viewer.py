"""
Custom QGraphicsView widget for displaying and interacting with images,
including zoom, fit-to-view, and drag-to-pan functionality.
"""

from typing import Union

from PyQt5.QtCore import QEvent, QRect, QRectF, Qt
from PyQt5.QtGui import QMouseEvent, QPainter, QPixmap, QResizeEvent, QWheelEvent
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget

from src.widgets.crop_handler import CropHandler


class ImageViewer(QGraphicsView):  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    A custom graphics view for displaying and interacting with images.

    This widget provides features such as:
      - Displaying images with zoom and fit-to-view capabilities.
      - Smooth rendering and antialiasing.
      - Drag-to-pan functionality.
      - Mouse wheel zoom with Ctrl modifier.
      - Automatic scene rect and transformation management.

    Attributes:
        zoom (float): Current zoom factor.
        fit_to_view (bool): Whether the image is fit to the view.
        scene (QGraphicsScene): The graphics scene containing the image.
        photo (QGraphicsPixmapItem): The pixmap item displaying the image.
    """

    def __init__(self, parent: Union[QWidget, None] = None) -> None:
        """
        Initializes the ImageViewer with default settings.

        Args:
            self (ImageViewer): The instance of the image viewer.
            parent (QWidget, optional): Parent widget.

        Returns:
            None
        """
        super().__init__(parent)
        self.zoom = 1.0
        self.fit_to_view = False
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

        # Initialize crop handler
        self._crop_handler = CropHandler(self)

    def toggle_view(self) -> None:
        """
        Toggles between fit-to-view and manual zoom modes.

        Args:
            self (ImageViewer): The instance of the image viewer.

        Returns:
            None
        """
        self.fit_to_view = not self.fit_to_view
        if self.fit_to_view:
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.zoom = 1.0
        else:
            self.resetTransform()
            self.zoom = 1.0

    def set_image(self, pixmap: QPixmap) -> None:
        """
        Sets the displayed image.

        Args:
            self (ImageViewer): The instance of the image viewer.
            pixmap (QPixmap): The image to display.

        Returns:
            None

        Behavior:
            - Sets the pixmap in the scene.
            - Fits the image to the view.
            - Resets the zoom factor.
        """
        if self.photo is not None:
            self.photo.setPixmap(pixmap)
            self.fitInView(self.photo, Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom = 1.0

    def wheelEvent(self, event: QWheelEvent) -> None:  # pylint: disable=C0103
        """
        Handles mouse wheel events for zooming.

        Args:
            self (ImageViewer): The instance of the image viewer.
            event (QWheelEvent): The wheel event.

        Returns:
            None

        - Holding Ctrl and using the wheel zooms in/out.
        - Exits fit-to-view mode on manual zoom.
        - Otherwise, passes the event to the base class.
        """
        if event is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                zoom_factor = 1.25
                if event.angleDelta().y() > 0:
                    self.scale(zoom_factor, zoom_factor)
                    self.zoom *= zoom_factor
                    self.fit_to_view = False  # Exit fit-to-view on manual zoom
                else:
                    self.scale(1 / zoom_factor, 1 / zoom_factor)
                    self.zoom /= zoom_factor
                    self.fit_to_view = False
                event.accept()
            else:
                super().wheelEvent(event)
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # pylint: disable=C0103
        """
        Handles widget resize events.

        Args:
            self (ImageViewer): The instance of the image viewer.
            event (QResizeEvent): The resize event.

        Returns:
            None

        - If in fit-to-view mode, refits the image to the new view size.
        """
        if self.fit_to_view:
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # pylint: disable=C0103
        """
        Handles mouse press events.

        Args:
            self (ImageViewer): The instance of the image viewer.
            event (QMouseEvent): The mouse press event.

        Returns:
            None

        - Delegates crop-related events to the crop handler.
        - Enables scroll-hand drag mode on left mouse button press.
        """
        if event is not None:
            # First check if crop handler wants to handle this event
            if self._crop_handler.handle_mouse_press(event, self.photo):
                return
            if event.button() == Qt.MouseButton.LeftButton:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # pylint: disable=C0103
        """
        Handles mouse release events.

        Args:
            self (ImageViewer): The instance of the image viewer.
            event (QMouseEvent): The mouse release event.

        Returns:
            None

        - Delegates crop-related events to the crop handler.
        - Disables drag mode when the mouse is released.
        """
        if event is not None:
            # First check if crop handler wants to handle this event
            if self._crop_handler.handle_mouse_release(event, self.photo):
                return
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # pylint: disable=C0103
        """
        Handles mouse move events.

        Args:
            self (ImageViewer): The instance of the image viewer.
            event (QMouseEvent): The mouse move event.

        Returns:
            None

        - Delegates crop-related events to the crop handler.
        """
        if self._crop_handler.handle_mouse_move(event, self.photo):
            return
        super().mouseMoveEvent(event)

    def enterEvent(self, event: QEvent) -> None:  # pylint: disable=C0103
        """Handle mouse enter events to ensure cursor is updated."""
        if self._crop_handler.is_crop_mode() and isinstance(event, QMouseEvent):
            handle = self._crop_handler.get_handle_at(event.pos(), self.photo)
            self._crop_handler.update_cursor_for_handle(handle)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # pylint: disable=C0103
        """Handle mouse leave events to reset cursor."""
        if self._crop_handler.is_crop_mode() and isinstance(event, QMouseEvent):
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def set_crop_mode(self, enabled: bool) -> None:
        """
        Enables or disables crop mode in the image viewer.

        Args:
            self (ImageViewer): The instance of the image viewer.
            enabled (bool): True to enable crop mode, False to disable it.

        Returns:
            None
        """
        self._crop_handler.set_crop_mode(enabled, self.photo)

    def confirm_crop(self) -> None:
        """
        Confirms the current crop rectangle and applies the crop to the image.
        """
        if self.photo is None or not self.photo.pixmap():
            return

        # First save the crop rectangle
        self._crop_handler.confirm_crop(self.photo)

        # Then apply the crop to the image
        saved_rect = self._crop_handler.get_saved_crop_rect()
        if saved_rect:
            # Get the cropped pixmap
            cropped_pixmap = self._crop_handler.apply_crop(self.photo)

            if not cropped_pixmap.isNull() and cropped_pixmap.width() > 0 and cropped_pixmap.height() > 0:
                # Remove old pixmap item
                self._scene.removeItem(self.photo)

                # Create new pixmap item with cropped image
                self.photo = self._scene.addPixmap(cropped_pixmap)

                # Update the scene rectangle to match the new image dimensions
                self.setSceneRect(0, 0, cropped_pixmap.width(), cropped_pixmap.height())

                # Fit the cropped image to view
                self.fitInView(self.photo, Qt.AspectRatioMode.KeepAspectRatio)
                self.zoom = 1.0

                # Force update
                self.viewport().update()

    def cancel_crop(self) -> None:
        """
        Cancels the current crop operation.
        """
        self._crop_handler.cancel_crop()

    def get_saved_crop_rect(self) -> Union[QRect, None]:
        """
        Returns the saved crop rectangle.
        """
        return self._crop_handler.get_saved_crop_rect()

    def set_saved_crop_rect(self, rect: QRect) -> None:
        """
        Sets the saved crop rectangle.
        """
        self._crop_handler.set_saved_crop_rect(rect)

    def get_crop_rect(self) -> Union[QRect, None]:
        """
        Returns the current crop rectangle.
        """
        return self._crop_handler.get_crop_rect()

    def set_crop_rect(self, rect: QRect) -> None:
        """
        Sets the crop rectangle for the image viewer and triggers a viewport update.
        """
        self._crop_handler.set_crop_rect(rect)

    def set_crop_ratio(self, ratio: Union[tuple[int, int], None]) -> None:
        """
        Sets the aspect ratio for the crop rectangle.
        """
        self._crop_handler.set_crop_ratio(ratio, self.photo)

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:  # pylint: disable=C0103, unused-argument
        """
        Draws the crop rectangle and handles when in crop mode.

        Args:
            painter (QPainter): The painter object.
            rect (QRectF): The area to be painted.

        Returns:
            None
        """
        self._crop_handler.draw_foreground(painter, rect, self.sceneRect())
