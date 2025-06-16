"""
Main application window and UI layout for the RGB Channel Processor.
Handles state management, user interactions, and connects UI components to processing logic.
"""

from typing import Callable

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox

from .handlers.channels import adjust_channel, load_channel, show_single_channel
from .handlers.display import update_main_display
from .handlers.keyboard import handle_key_press
from .widgets.channel_controller import ChannelController
from .widgets.image_viewer import ImageViewer


class MainWindow(QMainWindow):
    """
    Main application window for the RGB Channel Processor.

    This window manages the overall GUI layout, holds the state of loaded and processed images,
    and connects user interactions (buttons, sliders, keyboard) to the processing logic.

    Related components:
        - ImageViewer (widgets.image_viewer): Displays the main image.
        - ChannelController (widgets.channel_controller): Controls for each RGB channel.
        - handlers.channels: Functions for loading and adjusting channels.
        - handlers.display: Functions for updating the main display.
        - handlers.keyboard: Keyboard shortcut handling.
    """

    def __init__(self) -> None:
        """
        Initialize the main window, set up the title, geometry, internal state,
        and construct the user interface.

        Args:
            self (MainWindow): The instance of the main window.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("RGB Channel Processor")
        self.setGeometry(100, 100, 1200, 800)

        # State: original, aligned, and processed images for R, G, B channels
        self.original_images = [None, None, None]
        self.aligned = [None, None, None]
        self.processed = [None, None, None]
        # Display state
        self.show_combined = True  # If True, show combined RGB; else show single channel
        self.current_channel = 0   # Index of the currently selected channel
        
        # Crop-related state
        self.crop_mode = False
        self.crop_rect = None
        self.crop_ratio = None
        
        self.init_ui()

    def init_ui(self) -> None:
        """
        Build the main UI layout: image viewer and channel controllers.

        Args:
            self (MainWindow): The instance of the main window.

        Returns:
            None

        - Adds an ImageViewer widget for displaying images.
        - Adds three ChannelController widgets (R, G, B) with sliders and load buttons.
        - Connects controller signals to appropriate handler functions.

        Cross-references:
            - ImageViewer
            - ChannelController
            - handlers.channels.load_channel, adjust_channel, update_channel_preview, show_single_channel
        """
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Add crop mode button (QPushButton)
        self.crop_mode_btn = QPushButton("Crop")
        self.crop_mode_btn.clicked.connect(self.toggle_crop_mode)

        # Crop controls widget (already present)
        self.crop_ratio_combo = QComboBox()
        self.crop_ratio_combo.addItem("Free", None)
        self.crop_ratio_combo.addItem("16:9", (16, 9))
        self.crop_ratio_combo.addItem("3:2", (3, 2))
        self.crop_ratio_combo.addItem("4:3", (4, 3))
        self.crop_ratio_combo.addItem("5:4", (5, 4))
        self.crop_ratio_combo.addItem("1:1", (1, 1))
        self.crop_ratio_combo.addItem("4:5", (4, 5))
        self.crop_ratio_combo.addItem("3:4", (3, 4))
        self.crop_ratio_combo.addItem("2:3", (2, 3))
        self.crop_ratio_combo.addItem("9:16", (9, 16))
        self.crop_ratio_combo.currentIndexChanged.connect(self.set_crop_ratio)

        self.crop_controls_widget = QWidget()
        crop_controls_layout = QHBoxLayout(self.crop_controls_widget)
        crop_controls_layout.setContentsMargins(0, 0, 0, 0)
        crop_controls_layout.addWidget(self.crop_ratio_combo)
        self.accept_crop_btn = QPushButton("Accept Crop")
        self.accept_crop_btn.clicked.connect(self.apply_crop)
        crop_controls_layout.addWidget(self.accept_crop_btn)
        self.cancel_crop_btn = QPushButton("Cancel Crop")
        self.cancel_crop_btn.clicked.connect(self.cancel_crop)
        crop_controls_layout.addWidget(self.cancel_crop_btn)
        self.crop_controls_widget.setVisible(False)

        # Main vertical layout for left side (crop button + crop controls + image viewer)
        left_panel = QVBoxLayout()
        left_panel.addWidget(self.crop_mode_btn)
        left_panel.addWidget(self.crop_controls_widget)
        self.viewer = ImageViewer()
        left_panel.addWidget(self.viewer, 70)

        main_layout.addLayout(left_panel, 70)

        # Right panel with channel controllers
        right_panel = QVBoxLayout()
        self.controllers = [
            ChannelController("red", Qt.GlobalColor.red),
            ChannelController("green", Qt.GlobalColor.green),
            ChannelController("blue", Qt.GlobalColor.blue),
        ]

        for idx, controller in enumerate(self.controllers):
            # Connect load button and sliders to handlers
            controller.btn_load.clicked.connect(lambda _, i=idx: load_channel(self, i))
            controller.sliders["brightness"].valueChanged.connect(lambda _, i=idx: adjust_channel(self, i))
            controller.sliders["contrast"].valueChanged.connect(lambda _, i=idx: adjust_channel(self, i))
            controller.sliders["intensity"].valueChanged.connect(lambda _: update_main_display(self))

            # Fix the mousePressEvent assignment with properly typed functions
            # Pass controller as an argument to avoid cell-var-from-loop issue
            def create_click_handler(index: int, ctrl: ChannelController = controller) -> Callable[[QMouseEvent], None]:
                def click_handler(event: QMouseEvent) -> None:
                    show_single_channel(self, index)
                    # Call the original method to maintain expected behavior
                    QLabel.mousePressEvent(ctrl.preview_label, event)

                return click_handler

            # Instead of directly assigning to mousePressEvent, connect to a custom event filter
            # or subclass QLabel - for now, we'll keep the assignment but add a type ignore comment
            controller.preview_label.mousePressEvent = create_click_handler(idx)  # type: ignore

            right_panel.addWidget(controller)
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 30)

        self.setCentralWidget(main_widget)

    def toggle_crop_mode(self):
        """
        Toggles the crop mode in the application.

        Args:
            self (MainWindow): The instance of the main window.

        Returns:
            None

        - Enables crop mode if currently disabled.
        - Displays crop controls and initializes the crop rectangle.
        - Uses the last saved crop rectangle if available.

        Cross-references:
            - ImageViewer.set_crop_mode
            - update_main_display
        """
        if self.crop_mode:
            return
        if not any(img is not None for img in self.processed):
            return  # Add error message in UI
        self.crop_mode = True
        self.crop_mode_btn.setVisible(False)
        self.crop_controls_widget.setVisible(True)
        # Use last saved crop rectangle if available
        if hasattr(self.viewer, '_saved_crop_rect') and self.viewer._saved_crop_rect:
            self.crop_rect = QRect(self.viewer._saved_crop_rect)
        else:
            if any(img is not None for img in self.processed):
                for img in self.processed:
                    if img is not None:
                        img_w, img_h = img.shape[1], img.shape[0]
                        rect_w = int(img_w * 0.8)
                        rect_h = int(img_h * 0.8)
                        x = (img_w - rect_w) // 2
                        y = (img_h - rect_h) // 2
                        self.crop_rect = QRect(x, y, rect_w, rect_h)
                        break
                if self.crop_ratio:
                    self.crop_rect = self._get_aspect_crop_rect(self.crop_rect, self.crop_ratio)
        self.viewer.set_crop_mode(self.crop_mode)
        if self.crop_rect:
            self.viewer.set_crop_rect(self.crop_rect)
        update_main_display(self)

    def cancel_crop(self):
        """
        Cancels the current crop operation.

        Args:
            self (MainWindow): The instance of the main window.

        Returns:
            None

        - Exits crop mode without applying changes.
        - Restores the last saved crop rectangle if available.

        Cross-references:
            - ImageViewer.set_crop_mode
            - update_main_display
        """
        self.crop_mode = False
        self.crop_mode_btn.setVisible(True)
        self.crop_controls_widget.setVisible(False)
        if hasattr(self.viewer, '_saved_crop_rect') and self.viewer._saved_crop_rect:
            self.crop_rect = QRect(self.viewer._saved_crop_rect)
            self.viewer.set_crop_rect(self.crop_rect)
        else:
            self.crop_rect = None
        self.viewer.set_crop_mode(False)
        update_main_display(self)

    def set_crop_ratio(self, index):
        """
        Sets the aspect ratio for the crop rectangle.

        Args:
            self (MainWindow): The instance of the main window.
            index (int): The index of the selected aspect ratio in the combo box.

        Returns:
            None

        - Adjusts the crop rectangle to maintain the selected aspect ratio.
        - Updates the viewer to reflect the new ratio.

        Cross-references:
            - ImageViewer.set_crop_ratio
            - update_main_display
        """
        self.crop_ratio = self.crop_ratio_combo.currentData()
        # Always get the current rectangle from the viewer
        current_rect = self.viewer._crop_rect if self.viewer._crop_rect else self.crop_rect
        if current_rect and self.crop_ratio:
            new_rect = self._get_aspect_crop_rect(current_rect, self.crop_ratio)
            self.crop_rect = new_rect
            self.viewer.set_crop_ratio(self.crop_ratio)
            self.viewer.set_crop_rect(new_rect)
            # Keep viewer._crop_rect and self.crop_rect in sync
        elif current_rect:
            # Free mode
            self.viewer.set_crop_ratio(None)
            self.viewer.set_crop_rect(current_rect)
            self.crop_rect = current_rect
        update_main_display(self)

    def _get_aspect_crop_rect(self, rect, ratio):
        """
        Returns the largest rectangle with the given aspect ratio that fits within the given rect,
        centered at the same point as the original rect.

        Args:
            self (MainWindow): The instance of the main window.
            rect (QRect): The original rectangle.
            ratio (tuple): The desired aspect ratio as (width, height).

        Returns:
            QRect: The adjusted rectangle.

        Cross-references:
            - set_crop_ratio
        """
        if not rect or not ratio:
            return rect
        orig_w = rect.width()
        orig_h = rect.height()
        center = rect.center()
        w, h = ratio
        target_ratio = w / h
        # Try to maintain width first
        new_w = orig_w
        new_h = int(new_w / target_ratio)
        if new_h > orig_h:
            new_h = orig_h
            new_w = int(new_h * target_ratio)
        # Center the new rect
        new_left = center.x() - new_w // 2
        new_top = center.y() - new_h // 2
        return QRect(new_left, new_top, new_w, new_h)

    def apply_crop(self):
        """
        Applies the current crop rectangle to the processed images.

        Args:
            self (MainWindow): The instance of the main window.

        Returns:
            None

        - Saves the crop rectangle for future use.
        - Exits crop mode and updates the main display.

        Cross-references:
            - ImageViewer._crop_rect, _saved_crop_rect
            - update_main_display
        """
        crop_rect = self.viewer._crop_rect if self.viewer._crop_rect else self.crop_rect
        if not crop_rect or not any(img is not None for img in self.processed):
            return
        self.viewer._saved_crop_rect = crop_rect
        self.crop_mode = False
        self.crop_mode_btn.setVisible(True)
        self.crop_controls_widget.setVisible(False)
        self.viewer.set_crop_mode(False)
        update_main_display(self)

    def keyPressEvent(self, event):
        """
        Handle key press events for channel switching and display mode.

        Args:
            self (MainWindow): The instance of the main window.
            event (QKeyEvent): The key press event.

        Returns:
            None

        Delegates to handle_key_press; falls back to default if not handled.

        Cross-references:
            - handlers.keyboard.handle_key_press
            - toggle_crop_mode
            - cancel_crop
            - apply_crop
        """
        if self.crop_mode:
            if event.key() == Qt.Key_Escape:
                self.cancel_crop()
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.apply_crop()
            # Do not allow toggling crop mode with 'C' while in crop mode
            else:
                super().keyPressEvent(event)
        else:
            if event.key() == Qt.Key_C:
                self.toggle_crop_mode()
            elif not handle_key_press(self, event):
                super().keyPressEvent(event)
