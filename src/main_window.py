from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from widgets.image_viewer import ImageViewer
from widgets.channel_controller import ChannelController
from handlers.keyboard import handle_key_press
from handlers.channels import load_channel, adjust_channel, update_channel_preview, show_single_channel
from handlers.display import update_main_display

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RGB Channel Processor")
        self.setGeometry(100, 100, 1200, 800)

        self.original_images = [None, None, None]
        self.aligned = [None, None, None]
        self.processed = [None, None, None]
        self.show_combined = True
        self.current_channel = 0

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.viewer = ImageViewer()
        main_layout.addWidget(self.viewer, 70)

        right_panel = QVBoxLayout()
        self.controllers = [
            ChannelController("red", Qt.red),
            ChannelController("green", Qt.green),
            ChannelController("blue", Qt.blue)
        ]

        for idx, controller in enumerate(self.controllers):
            controller.btn_load.clicked.connect(lambda _, i=idx: load_channel(self, i))
            controller.slider_brightness.valueChanged.connect(lambda v, i=idx: adjust_channel(self, i))
            controller.slider_contrast.valueChanged.connect(lambda v, i=idx: adjust_channel(self, i))
            controller.slider_intensity.valueChanged.connect(lambda v, i=idx: update_main_display(self))
            controller.preview_label.mousePressEvent = (lambda event, i=idx: show_single_channel(self, i))

            right_panel.addWidget(controller)
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 30)

        self.setCentralWidget(main_widget)

    def keyPressEvent(self, event):
        if not handle_key_press(self, event):
            super().keyPressEvent(event)
