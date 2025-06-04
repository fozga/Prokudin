"""
Main application window and UI layout for the RGB Channel Processor.
Handles state management, user interactions, and connects UI components to processing logic.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from handlers.channels import adjust_channel, load_channel, show_single_channel
from handlers.display import update_main_display
from handlers.keyboard import handle_key_press
from widgets.channel_controller import ChannelController
from widgets.image_viewer import ImageViewer


class MainWindow(QMainWindow):
    """
    Main application window for the RGB Channel Processor.

    This window manages the overall GUI layout, holds the state of loaded and processed images,
    and connects user interactions (buttons, sliders, keyboard) to the processing logic.
    """

    def __init__(self):
        """
        Initialize the main window, set up the title, geometry, internal state,
        and construct the user interface.
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
        self.current_channel = 0  # Index of the currently selected channel

        self.init_ui()

    def init_ui(self):
        """
        Build the main UI layout: image viewer and channel controllers.

        - Adds an ImageViewer widget for displaying images.
        - Adds three ChannelController widgets (R, G, B) with sliders and load buttons.
        - Connects controller signals to appropriate handler functions.
        """
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Main image display
        self.viewer = ImageViewer()
        main_layout.addWidget(self.viewer, 70)

        # Right panel with channel controllers
        right_panel = QVBoxLayout()
        self.controllers = [
            ChannelController("red", Qt.red),
            ChannelController("green", Qt.green),
            ChannelController("blue", Qt.blue),
        ]

        for idx, controller in enumerate(self.controllers):
            # Connect load button and sliders to handlers
            controller.btn_load.clicked.connect(lambda _, i=idx: load_channel(self, i))
            controller.slider_brightness.valueChanged.connect(lambda v, i=idx: adjust_channel(self, i))
            controller.slider_contrast.valueChanged.connect(lambda v, i=idx: adjust_channel(self, i))
            controller.slider_intensity.valueChanged.connect(lambda v, i=idx: update_main_display(self))
            controller.preview_label.mousePressEvent = lambda event, i=idx: show_single_channel(self, i)

            right_panel.addWidget(controller)
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 30)

        self.setCentralWidget(main_widget)

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """
        Handle key press events for channel switching and display mode.

        Delegates to handle_key_press; falls back to default if not handled.
        """
        if not handle_key_press(self, event):
            super().keyPressEvent(event)
