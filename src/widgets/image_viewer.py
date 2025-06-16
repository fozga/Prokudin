"""
Custom QGraphicsView widget for displaying and interacting with images,
including zoom, fit-to-view, and drag-to-pan functionality.
"""

from typing import Union

from PyQt5.QtCore import QPointF, QRect, QRectF, QEvent, Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QPen, QPixmap, QResizeEvent, QWheelEvent, QCursor
from PyQt5.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget


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

        # Crop-related state
        self._crop_mode = False
        self._crop_rect: Union[QRect, None] = None  # Current temporary crop rectangle
        self._saved_crop_rect: Union[QRect, None]  = None  # Last confirmed crop rectangle
        self._crop_ratio: Union[tuple[int, int], None] = None
        self._crop_handle_size = 20
        self._dragging = False
        self._drag_start: Union[QPointF, None] = None
        self._drag_handle: Union[str, None] = None
        self._original_crop_rect: Union[QRect, None] = None
        self._anchor_point: Union[QPointF, None]  = None
        self._fixed_edges: Union[dict[str, int], None] = None
        self._min_crop_size = 50

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

        - Enables scroll-hand drag mode on left mouse button press.
        """
        if event is not None:
            if self._crop_mode and event.button() == Qt.MouseButton.LeftButton:
                self._drag_handle = self.get_handle_at(event.pos())
                if self._drag_handle:
                    self._dragging = True
                    self._drag_start = self.mapToScene(event.pos())
                    self._original_crop_rect = self._crop_rect  # Store original rect

                    self._anchor_point = self.get_anchor_point(self._drag_handle, self._crop_rect)
                    # Store fixed edges for corner handles
                    if (
                        self._drag_handle in ["top_left", "top_right", "bottom_left", "bottom_right"]
                        and self._crop_rect is not None
                    ):
                        rect = self._crop_rect
                        self._fixed_edges = {
                            "top": rect.top(),
                            "bottom": rect.bottom(),
                            "left": rect.left(),
                            "right": rect.right(),
                        }
                    else:
                        self._fixed_edges = None
                    if self._drag_handle == "move":
                        self.setCursor(QCursor.ClosedHandCursor)
                    event.accept()
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

        - Disables drag mode when the mouse is released.
        """
        if event is not None:
            if self._crop_mode and event.button() == Qt.MouseButton.LeftButton:
                if self._dragging:
                    self._dragging = False
                    self._drag_handle = None
                    # Update cursor based on current position

                    handle = self.get_handle_at(event.pos())
                    self.update_cursor_for_handle(handle)
                    event.accept()
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

        - Updates the cursor based on the handle under the mouse.
        - Updates the crop rectangle based on mouse movement.
        """
        if self._crop_mode:
            if self._dragging and self._crop_rect:
                current_pos = self.mapToScene(event.pos())
                if self._drag_handle == "move":
                    delta = current_pos - self._drag_start
                    self._drag_start = current_pos
                    self._crop_rect.translate(int(delta.x()), int(delta.y()))
                else:

                    self.resize_crop_rect_from_anchor(
                        self._drag_handle, self._anchor_point, current_pos, self._original_crop_rect
                    )
                self.constrain_crop_rect()
                self.viewport().update()
                event.accept()
                return
            else:
                # Update cursor based on handle under mouse

                handle = self.get_handle_at(event.pos())
                self.update_cursor_for_handle(handle)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def enterEvent(self, event: QEvent) -> None:  # pylint: disable=C0103
        """Handle mouse enter events to ensure cursor is updated."""
        if self._crop_mode and isinstance(event, QMouseEvent):
            handle = self.get_handle_at(event.pos())
            self.update_cursor_for_handle(handle)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # pylint: disable=C0103
        """Handle mouse leave events to reset cursor."""
        if self._crop_mode and isinstance(event, QMouseEvent):
            self.setCursor(QCursor.ArrowCursor)
        super().leaveEvent(event)

    def update_cursor_for_handle(self, handle: Union[str, None]) -> None:
        """Update cursor based on the handle under the mouse."""
        if self._dragging and self._drag_handle == "move":
            self.setCursor(QCursor.ClosedHandCursor)
        elif handle == "move":
            self.setCursor(QCursor.SizeAllCursor)  # Four arrows for center area
        elif handle in ["top_left", "bottom_right"]:
            self.setCursor(QCursor.SizeFDiagCursor)  # Diagonal arrow for top-left/bottom-right
        elif handle in ["top_right", "bottom_left"]:
            self.setCursor(QCursor.SizeBDiagCursor)  # Diagonal arrow for top-right/bottom-left
        elif handle in ["left", "right"]:
            self.setCursor(QCursor.SizeHorCursor)  # Horizontal arrow for left/right
        elif handle in ["top", "bottom"]:
            self.setCursor(QCursor.SizeVerCursor)  # Vertical arrow for top/bottom
        else:
            self.setCursor(QCursor.ArrowCursor)
        # Force immediate cursor update
        QApplication.processEvents()

    def set_crop_mode(self, enabled: bool) -> None:
        """
        Enables or disables crop mode in the image viewer.

        Args:
            self (ImageViewer): The instance of the image viewer.
            enabled (bool): True to enable crop mode, False to disable it.

        Returns:
            None

        Behavior:
            - Initializes the crop rectangle if enabling crop mode.
            - Discards the temporary crop rectangle when disabling crop mode.
        """
        self._crop_mode = enabled
        if enabled and self.photo is not None:
            if self.photo.pixmap():
                if self._saved_crop_rect:
                    # Use last saved crop rectangle if available
                    self._crop_rect = QRect(self._saved_crop_rect)
                else:
                    # Initialize to 80% of image size, centered

                    img_width = self.photo.pixmap().width()
                    img_height = self.photo.pixmap().height()
                    rect_width = int(img_width * 0.8)
                    rect_height = int(img_height * 0.8)
                    x = (img_width - rect_width) // 2
                    y = (img_height - rect_height) // 2
                    self._crop_rect = QRect(x, y, rect_width, rect_height)

                if self._crop_ratio:

                    self.adjust_crop_rect_to_ratio()
            self.setCursor(QCursor.ArrowCursor)
        else:
            # Discard temporary crop rectangle when exiting crop mode
            self._crop_rect = None
            self.setCursor(QCursor.ArrowCursor)
        self.viewport().update()

    def confirm_crop(self) -> None:
        """
        Confirms the current crop rectangle.

        - Saves the crop rectangle for future use.
        - Exits crop mode.
        """
        if self._crop_rect:
            self._saved_crop_rect = QRect(self._crop_rect)
        self.set_crop_mode(False)

    def cancel_crop(self) -> None:
        """
        Cancels the current crop operation.

        - Discards the temporary crop rectangle.
        - Exits crop mode.
        """
        self._crop_rect = None
        self.set_crop_mode(False)

    def set_crop_rect(self, rect: QRect) -> None:
        """
        Sets the crop rectangle for the image viewer and triggers a viewport update.

        Args:
            self (ImageViewer): The instance of the image viewer.
            rect (QRect): The rectangle defining the crop area.

        Returns:
            None
        """
        self._crop_rect = rect
        self.viewport().update()

    def set_crop_ratio(self, ratio: Union[tuple[int, int], None]) -> None:
        """
        Sets the aspect ratio for the crop rectangle.

        Args:
            self (ImageViewer): The instance of the image viewer.
            ratio (tuple or None): Aspect ratio as (width, height), or None for free aspect.

        Returns:
            None
        """
        if not self._crop_rect:
            self._crop_ratio = ratio
            return

        # Update the ratio
        self._crop_ratio = ratio

        # Adjust the current rectangle to the new ratio

        self.adjust_crop_rect_to_ratio()

    def adjust_crop_rect_to_ratio(self) -> None:
        """
        Adjusts the current crop rectangle to maintain the set aspect ratio.

        Args:
            self (ImageViewer): The instance of the image viewer.

        Returns:
            None
        """
        if self.photo is not None:
            if not self._crop_ratio or not self._crop_rect:
                return

            # Get current dimensions
            original_width = self._crop_rect.width()
            original_height = self._crop_rect.height()

            # Calculate new dimensions based on ratio
            w, h = self._crop_ratio
            target_ratio = w / h

            # First try to maintain width and adjust height
            new_width = original_width
            new_height = int(new_width / target_ratio)

            # If new height would exceed original height, maintain height instead
            if new_height > original_height:
                new_height = original_height
                new_width = int(new_height * target_ratio)

            # Create new rectangle maintaining the top-left corner position
            new_rect = QRect(self._crop_rect.left(), self._crop_rect.top(), new_width, new_height)

            # Ensure the new rectangle stays within image bounds

            bounds = self.photo.boundingRect()
            if new_rect.right() > bounds.right():
                new_rect.setRight(int(bounds.right()))
                new_rect.setWidth(int(new_rect.height() * target_ratio))
            if new_rect.bottom() > bounds.bottom():
                new_rect.setBottom(int(bounds.bottom()))
                new_rect.setHeight(int(new_rect.width() / target_ratio))

            self._crop_rect = new_rect
            self.viewport().update()

    def get_handle_at(self, pos: QPointF) -> Union[str, None]:
        """
        Determines which crop handle (if any) is under the given mouse position.

        Args:
            self (ImageViewer): The instance of the image viewer.
            pos (QPointF): Mouse position in view coordinates.

        Returns:
            str or None: Handle name ('top_left', 'move', etc.) or None if not on a handle.
        """

        if not self._crop_rect:
            return None

        # Convert view coordinates to scene coordinates
        scene_pos = self.mapToScene(pos)
        rect = self._crop_rect
        handle_size = self._crop_handle_size

        # Define handle areas with larger hit regions
        handles = {
            "top_left": QRectF(rect.left() - handle_size, rect.top() - handle_size, handle_size * 2, handle_size * 2),
            "top_right": QRectF(rect.right() - handle_size, rect.top() - handle_size, handle_size * 2, handle_size * 2),
            "bottom_left": QRectF(
                rect.left() - handle_size, rect.bottom() - handle_size, handle_size * 2, handle_size * 2
            ),
            "bottom_right": QRectF(
                rect.right() - handle_size, rect.bottom() - handle_size, handle_size * 2, handle_size * 2
            ),
            "top": QRectF(
                rect.left() + handle_size, rect.top() - handle_size, rect.width() - handle_size * 2, handle_size * 2
            ),
            "bottom": QRectF(
                rect.left() + handle_size, rect.bottom() - handle_size, rect.width() - handle_size * 2, handle_size * 2
            ),
            "left": QRectF(
                rect.left() - handle_size, rect.top() + handle_size, handle_size * 2, rect.height() - handle_size * 2
            ),
            "right": QRectF(
                rect.right() - handle_size, rect.top() + handle_size, handle_size * 2, rect.height() - handle_size * 2
            ),
        }

        # First check corners and edges
        for handle, handle_rect in handles.items():
            if handle_rect.contains(scene_pos):
                return handle

        # Then check if inside crop rect (for moving)
        if rect.contains(scene_pos.toPoint()):
            return "move"

        return None

    def get_anchor_point(self, handle: str, rect: Union[QRect, None]) -> QPointF:
        """
        Returns the fixed anchor point (QPointF) for a given handle and rectangle.

        Args:
            self (ImageViewer): The instance of the image viewer.
            handle (str): The handle being dragged.
            rect (QRect): The crop rectangle.

        Returns:
            QPointF: The anchor point.
        """
        if rect is not None:
            if handle == "top_left":
                return QPointF(rect.right(), rect.bottom())
            if handle == "top_right":
                return QPointF(rect.left(), rect.bottom())
            if handle == "bottom_left":
                return QPointF(rect.right(), rect.top())
            if handle == "bottom_right":
                return QPointF(rect.left(), rect.top())
            if handle == "left":
                return QPointF(rect.left(), rect.center().y())
            if handle == "right":
                return QPointF(rect.right(), rect.center().y())
            if handle == "top":
                return QPointF(rect.center().x(), rect.top())
            if handle == "bottom":
                return QPointF(rect.center().x(), rect.bottom())
            return QPointF(rect.center().x(), rect.center().y())
        return QPointF(0, 0)

    def resize_crop_rect_from_anchor(
        self,
        handle: Union[str, None],
        anchor: Union[QPointF, None],
        mouse_scene_pos: QPointF,
        original_rect: Union[QRect, None],
    ) -> None:
        """
        Resizes the crop rectangle based on the dragged handle and anchor.

        Args:
            self (ImageViewer): The instance of the image viewer.
            handle (str): The handle being dragged.
            anchor (QPointF): The fixed anchor point.
            mouse_scene_pos (QPointF): Current mouse position in scene coordinates.
            original_rect (QRect): The original crop rectangle before dragging.

        Returns:
            None
        """
        if self.photo is not None and anchor is not None and original_rect is not None and handle is not None:
            bounds = self.photo.boundingRect()
            anchor = QPointF(anchor)
            mouse = QPointF(mouse_scene_pos)
            # Clamp mouse to image bounds
            mouse.setX(max(int(bounds.left()), min(int(bounds.right()), int(mouse.x()))))
            mouse.setY(max(int(bounds.top()), min(int(bounds.bottom()), int(mouse.y()))))
            # For corners, fix two opposite edges
            if handle in ["top_left", "top_right", "bottom_left", "bottom_right"] and self._fixed_edges:
                fe = self._fixed_edges
                if handle == "top_left":
                    fixed_right = int(fe["right"])
                    fixed_bottom = int(fe["bottom"])
                    moving_x = int(mouse.x())
                    moving_y = int(mouse.y())
                    moving_x = min(moving_x, fixed_right - 10)
                    moving_y = min(moving_y, fixed_bottom - 10)
                    width = fixed_right - moving_x
                    height = fixed_bottom - moving_y
                    if self._crop_ratio:
                        w, h = self._crop_ratio
                        target_ratio = w / h
                        if width / target_ratio > height:
                            width = int(height * target_ratio)
                        else:
                            height = int(width / target_ratio)
                        moving_x = fixed_right - width
                        moving_y = fixed_bottom - height
                    new_rect = QRect(
                        moving_x, moving_y, fixed_right - moving_x, fixed_bottom - moving_y
                    )
                elif handle == "top_right":
                    fixed_left = int(fe["left"])
                    fixed_bottom = int(fe["bottom"])
                    moving_x = int(mouse.x())
                    moving_y = int(mouse.y())
                    moving_x = max(moving_x, fixed_left + 10)
                    moving_y = min(moving_y, fixed_bottom - 10)
                    width = moving_x - fixed_left
                    height = fixed_bottom - moving_y
                    if self._crop_ratio:
                        w, h = self._crop_ratio
                        target_ratio = w / h
                        if width / target_ratio > height:
                            width = int(height * target_ratio)
                            moving_x = fixed_left + width
                        else:
                            height = int(width / target_ratio)
                            moving_y = fixed_bottom - height
                    new_rect = QRect(
                        fixed_left, moving_y, moving_x - fixed_left, fixed_bottom - moving_y
                    )
                elif handle == "bottom_left":
                    fixed_right = int(fe["right"])
                    fixed_top = int(fe["top"])
                    moving_x = int(mouse.x())
                    moving_y = int(mouse.y())
                    moving_x = min(moving_x, fixed_right - 10)
                    moving_y = max(moving_y, fixed_top + 10)
                    width = fixed_right - moving_x
                    height = moving_y - fixed_top
                    if self._crop_ratio:
                        w, h = self._crop_ratio
                        target_ratio = w / h
                        if width / target_ratio > height:
                            width = int(height * target_ratio)
                            moving_x = fixed_right - width
                        else:
                            height = int(width / target_ratio)
                            moving_y = fixed_top + height
                    new_rect = QRect(moving_x, fixed_top, fixed_right - moving_x, moving_y - fixed_top)
                elif handle == "bottom_right":
                    fixed_left = int(fe["left"])
                    fixed_top = int(fe["top"])
                    moving_x = int(mouse.x())
                    moving_y = int(mouse.y())
                    moving_x = max(moving_x, fixed_left + 10)
                    moving_y = max(moving_y, fixed_top + 10)
                    width = moving_x - fixed_left
                    height = moving_y - fixed_top
                    if self._crop_ratio:
                        w, h = self._crop_ratio
                        target_ratio = w / h
                        if width / target_ratio > height:
                            width = int(height * target_ratio)
                            moving_x = fixed_left + width
                        else:
                            height = int(width / target_ratio)
                            moving_y = fixed_top + height
                    new_rect = QRect(fixed_left, fixed_top, moving_x - fixed_left, moving_y - fixed_top)
                # Clamp new_rect to image bounds
                new_rect = new_rect.intersected(
                    QRect(int(bounds.left()), int(bounds.top()), int(bounds.width()), int(bounds.height()))
                )

                if new_rect.width() < self._min_crop_size or new_rect.height() < self._min_crop_size:
                    return  # Maintain minimum size
                self._crop_rect = new_rect
            elif handle in ["left", "right", "top", "bottom"]:
                rect = QRectF(original_rect)
                if self._crop_ratio:
                    w, h = self._crop_ratio
                    target_ratio = w / h
                    if handle in ["left", "right"]:
                        if handle == "left":
                            fixed_right = int(rect.right())
                            new_left = min(int(mouse.x()), fixed_right - 10)
                            width = fixed_right - new_left
                            height = int(round(width / target_ratio))
                            center_y = int(rect.center().y())
                            new_top = int(round(center_y - height / 2))
                            new_bottom = new_top + height
                            # Clamp to bounds
                            if new_left < int(bounds.left()):
                                new_left = int(bounds.left())
                                width = fixed_right - new_left
                                height = int(round(width / target_ratio))
                                new_top = int(round(center_y - height / 2))
                                new_bottom = new_top + height
                            if new_top < int(bounds.top()):
                                new_top = int(bounds.top())
                                height = int(rect.bottom()) - new_top
                                width = int(round(height * target_ratio))
                                new_left = fixed_right - width
                                new_bottom = new_top + height
                            if new_bottom > int(bounds.bottom()):
                                new_bottom = int(bounds.bottom())
                                height = new_bottom - new_top
                                width = int(round(height * target_ratio))
                                new_left = fixed_right - width
                            new_rect = QRect(new_left, new_top, width, height)
                        else:  # handle == 'right'
                            fixed_left = int(rect.left())
                            new_right = max(int(mouse.x()), fixed_left + 10)
                            width = new_right - fixed_left
                            height = int(round(width / target_ratio))
                            center_y = int(rect.center().y())
                            new_top = int(round(center_y - height / 2))
                            new_bottom = new_top + height
                            # Clamp to bounds
                            if new_right > int(bounds.right()):
                                new_right = int(bounds.right())
                                width = new_right - fixed_left
                                height = int(round(width / target_ratio))
                                new_top = int(round(center_y - height / 2))
                                new_bottom = new_top + height
                            if new_top < int(bounds.top()):
                                new_top = int(bounds.top())
                                height = int(rect.bottom()) - new_top
                                width = int(round(height * target_ratio))
                                new_right = fixed_left + width
                                new_bottom = new_top + height
                            if new_bottom > int(bounds.bottom()):
                                new_bottom = int(bounds.bottom())
                                height = new_bottom - new_top
                                width = int(round(height * target_ratio))
                                new_right = fixed_left + width
                            new_rect = QRect(fixed_left, new_top, width, height)
                    else:
                        if handle == "top":
                            fixed_bottom = int(rect.bottom())
                            new_top = min(int(mouse.y()), fixed_bottom - 10)
                            height = fixed_bottom - new_top
                            width = int(round(height * target_ratio))
                            center_x = int(rect.center().x())
                            new_left = int(round(center_x - width / 2))
                            new_right = new_left + width
                            # Clamp to bounds
                            if new_top < int(bounds.top()):
                                new_top = int(bounds.top())
                                height = fixed_bottom - new_top
                                width = int(round(height * target_ratio))
                                new_left = int(round(center_x - width / 2))
                                new_right = new_left + width
                            if new_left < int(bounds.left()):
                                new_left = int(bounds.left())
                                width = new_right - new_left
                                height = int(round(width / target_ratio))
                                new_top = fixed_bottom - height
                            if new_right > int(bounds.right()):
                                new_right = int(bounds.right())
                                width = new_right - new_left
                                height = int(round(width / target_ratio))
                                new_top = fixed_bottom - height
                            new_rect = QRect(new_left, new_top, width, height)
                        else:  # handle == 'bottom'
                            fixed_top = int(rect.top())
                            new_bottom = max(int(mouse.y()), fixed_top + 10)
                            height = new_bottom - fixed_top
                            width = int(round(height * target_ratio))
                            center_x = int(rect.center().x())
                            new_left = int(round(center_x - width / 2))
                            new_right = new_left + width
                            # Clamp to bounds
                            if new_bottom > int(bounds.bottom()):
                                new_bottom = int(bounds.bottom())
                                height = new_bottom - fixed_top
                                width = int(round(height * target_ratio))
                                new_left = int(round(center_x - width / 2))
                                new_right = new_left + width
                            if new_left < int(bounds.left()):
                                new_left = int(bounds.left())
                                width = new_right - new_left
                                height = int(round(width / target_ratio))
                                new_bottom = fixed_top + height
                            if new_right > int(bounds.right()):
                                new_right = int(bounds.right())
                                width = new_right - new_left
                                height = int(round(width / target_ratio))
                                new_bottom = fixed_top + height
                            new_rect = QRect(new_left, fixed_top, width, height)

                    if new_rect.width() < self._min_crop_size or new_rect.height() < self._min_crop_size:
                        return  # Maintain minimum size
                    self._crop_rect = new_rect
                else:
                    # Free aspect: allow edge dragging
                    left = int(rect.left())
                    right = int(rect.right())
                    top = int(rect.top())
                    bottom = int(rect.bottom())
                    if handle == "left":
                        new_left = min(int(mouse.x()), right - 10)
                        left = new_left
                    elif handle == "right":
                        new_right = max(int(mouse.x()), left + 10)
                        right = new_right
                    elif handle == "top":
                        new_top = min(int(mouse.y()), bottom - 10)
                        top = new_top
                    elif handle == "bottom":
                        new_bottom = max(int(mouse.y()), top + 10)
                        bottom = new_bottom
                    # Clamp to image bounds
                    left = max(int(bounds.left()), left)
                    right = min(int(bounds.right()), right)
                    top = max(int(bounds.top()), top)
                    bottom = min(int(bounds.bottom()), bottom)
                    width = right - left
                    height = bottom - top
                    new_rect = QRect(left, top, width, height)

                    if new_rect.width() < self._min_crop_size or new_rect.height() < self._min_crop_size:
                        return  # Maintain minimum size
                    self._crop_rect = new_rect

    def constrain_crop_rect(self) -> None:
        """
        Constrains the crop rectangle to stay within image bounds.

        Args:
            self (ImageViewer): The instance of the image viewer.

        Returns:
            None
        """
        if not self._crop_rect or not self.photo:
            return

        # Get image bounds
        bounds = self.photo.boundingRect()
        min_x = int(bounds.left())
        max_x = int(bounds.right())
        min_y = int(bounds.top())
        max_y = int(bounds.bottom())

        # Store original dimensions
        original_width = self._crop_rect.width()
        original_height = self._crop_rect.height()

        # Create a new rectangle with constrained coordinates
        new_rect = QRect(
            int(max(min_x, min(max_x - original_width, self._crop_rect.left()))),
            int(max(min_y, min(max_y - original_height, self._crop_rect.top()))),
            original_width,
            original_height,
        )

        # Update the crop rectangle
        self._crop_rect = new_rect

        # If we have a fixed ratio, maintain it
        if self._crop_ratio:

            self.adjust_crop_rect_to_ratio()

    def drawForeground(self, painter: QPainter) -> None:  # pylint: disable=C0103
        """
        Draws the crop rectangle and handles when in crop mode.

        Args:
            painter (QPainter): The painter object.
            rect (QRectF): The area to be painted.

        Returns:
            None
        """
        if not self._crop_mode or not self._crop_rect:
            return

        # Draw semi-transparent overlay
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw overlay only outside the crop rectangle
        scene_rect = self.sceneRect()
        painter.drawRect(
            QRectF(scene_rect.left(), scene_rect.top(), self._crop_rect.left() - scene_rect.left(), scene_rect.height())
        )
        painter.drawRect(
            QRectF(
                self._crop_rect.right(),
                scene_rect.top(),
                scene_rect.right() - self._crop_rect.right(),
                scene_rect.height(),
            )
        )
        painter.drawRect(
            QRectF(
                self._crop_rect.left(),
                scene_rect.top(),
                self._crop_rect.width(),
                self._crop_rect.top() - scene_rect.top(),
            )
        )
        painter.drawRect(
            QRectF(
                self._crop_rect.left(),
                self._crop_rect.bottom(),
                self._crop_rect.width(),
                scene_rect.bottom() - self._crop_rect.bottom(),
            )
        )

        # Draw crop rectangle
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor("white"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(self._crop_rect)

        # Draw handles
        handle_size = 8
        pen = QPen(QColor("white"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QColor("white"))

        # Draw corner handles
        corners: list[tuple[int, int, str]] = [
            (self._crop_rect.left(), self._crop_rect.top(), "top_left"),
            (self._crop_rect.right(), self._crop_rect.top(), "top_right"),
            (self._crop_rect.left(), self._crop_rect.bottom(), "bottom_left"),
            (self._crop_rect.right(), self._crop_rect.bottom(), "bottom_right"),
        ]
        for x, y, _ in corners:
            handle_rect = QRectF(
                float(x) - handle_size / 2, float(y) - handle_size / 2, float(handle_size), float(handle_size)
            )
            painter.drawRect(handle_rect)

        # Draw edge handles
        edges: list[tuple[int, int, str]] = [
            (int(self._crop_rect.left() + self._crop_rect.width() / 2), self._crop_rect.top(), "top"),
            (self._crop_rect.right(), int(self._crop_rect.top() + self._crop_rect.height() / 2), "right"),
            (int(self._crop_rect.left() + self._crop_rect.width() / 2), self._crop_rect.bottom(), "bottom"),
            (self._crop_rect.left(), int(self._crop_rect.top() + self._crop_rect.height() / 2), "left"),
        ]
        for x, y, _ in edges:
            handle_rect = QRectF(
                float(x) - handle_size / 2, float(y) - handle_size / 2, float(handle_size), float(handle_size)
            )
            painter.drawRect(handle_rect)
