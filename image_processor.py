import sys
import numpy as np
import cv2
import rawpy
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QSlider,
                             QLabel, QGroupBox, QGraphicsView, QGraphicsScene)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QImage, QPixmap, QPainter

class ResetSlider(QSlider):
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

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

class ChannelController(QGroupBox):
    def __init__(self, channel_name, color, parent=None):
        super().__init__(parent)
        self.channel_name = channel_name
        self.color = color
        self.processed_image = None
        self.default_values = {'brightness': 0, 'contrast': 0, 'intensity': 100}
        self.initUI()

    def initUI(self):
        self.setTitle(self.channel_name.capitalize())
        layout = QVBoxLayout()

        self.btn_load = QPushButton(f"Load {self.channel_name}")
        self.btn_load.setFixedSize(160, 30)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(160, 120)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray;")

        self.slider_brightness = self.create_slider("Brightness:", -100, 100, 0)
        self.slider_contrast = self.create_slider("Contrast:", -50, 50, 0)
        self.slider_intensity = self.create_slider("Intensity:", 0, 200, 100)

        layout.addWidget(self.btn_load)
        layout.addWidget(self.preview_label)
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.slider_brightness)
        layout.addWidget(QLabel("Contrast:"))
        layout.addWidget(self.slider_contrast)
        layout.addWidget(QLabel("Intensity:"))
        layout.addWidget(self.slider_intensity)

        self.setFixedWidth(200)
        self.setLayout(layout)

    def create_slider(self, label_text, min_val, max_val, default):
        slider = ResetSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setFixedWidth(180)
        slider.doubleClicked.connect(lambda: self.reset_slider(slider, default))
        return slider

    def reset_slider(self, slider, default):
        slider.setValue(default)
        self.parent().recalculate_from_original()

    def update_preview(self):
        if self.processed_image is not None:
            preview = cv2.resize(self.processed_image, (160, 120))
            q_img = QImage(preview.data, preview.shape[1], preview.shape[0],
                           preview.strides[0], QImage.Format_Grayscale8)
            self.preview_label.setPixmap(QPixmap.fromImage(q_img))

class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.show_output = False
        self.aligned = [None, None, None]
        self.original_images = [None, None, None]
        self.processed = [None, None, None]
        self.show_combined = True
        self.current_channel = 0
        self.initUI()
        
    def keyPressEvent(self, event):
        """Handle Ctrl+0/+/"""
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_0:
                self.viewer.toggle_view()
                event.accept()
                return
            elif event.key() == Qt.Key_Plus:
                self.viewer.scale(1.25, 1.25)
                self.viewer._fit_to_view = False
                event.accept()
                return
            elif event.key() == Qt.Key_Minus:
                self.viewer.scale(0.8, 0.8)
                self.viewer._fit_to_view = False
                event.accept()
                return
        if event.key() == Qt.Key_1:
            self.show_combined = False
            self.current_channel = 0
            self.update_main_display()
            event.accept()
            return
        elif event.key() == Qt.Key_2:
            self.show_combined = False
            self.current_channel = 1
            self.update_main_display()
            event.accept()
            return
        elif event.key() == Qt.Key_3:
            self.show_combined = False
            self.current_channel = 2
            self.update_main_display()
            event.accept()
            return
        elif event.key() == Qt.Key_A:
            self.show_combined = True
            self.update_main_display()
            event.accept()
            return
        super().keyPressEvent(event)

    def toggle_output_display(self):
        """Right-click to show processed output"""
        self.show_output = not self.show_output
        self.update_main_display()

    def initUI(self):
        self.setWindowTitle("RGB Channel Processor")
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.viewer = ImageViewer()
        main_layout.addWidget(self.viewer, 70)

        right_panel = QVBoxLayout()
        self.red_controller = ChannelController("red", Qt.red)
        self.green_controller = ChannelController("green", Qt.green)
        self.blue_controller = ChannelController("blue", Qt.blue)

        controllers = [self.red_controller, self.green_controller, self.blue_controller]
        for idx, controller in enumerate(controllers):
            controller.btn_load.clicked.connect(lambda _, i=idx: self.load_raw_image(i))
            controller.slider_brightness.valueChanged.connect(
                lambda v, i=idx: self.adjust_channel(i, 'brightness', v))
            controller.slider_contrast.valueChanged.connect(
                lambda v, i=idx: self.adjust_channel(i, 'contrast', v))
            controller.slider_intensity.valueChanged.connect(
                lambda v, i=idx: self.adjust_channel(i, 'intensity', v))
            controller.preview_label.mousePressEvent = (
                lambda event, i=idx: self.show_single_channel(i))

        right_panel.addWidget(self.red_controller)
        right_panel.addWidget(self.green_controller)
        right_panel.addWidget(self.blue_controller)
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 30)

        self.setCentralWidget(main_widget)
        self.viewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.viewer.customContextMenuRequested.connect(self.toggle_output_display)

    def load_raw_image(self, channel_idx):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select ARW File", "", 
            "Sony RAW Files (*.arw)", options=options)

        if filename:
            try:
                with rawpy.imread(filename) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=True,
                        output_bps=8
                    )
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
                self.original_images[channel_idx] = gray.copy()
                self.processed[channel_idx] = gray.copy()

                # Check if all channels are loaded
                if all(img is not None for img in self.original_images):
                    self.align_images()
                    # Update all previews after alignment
                    for i in range(3):
                        self.update_channel_preview(i)
                else:
                    # Update only current channel
                    self.update_channel_preview(channel_idx)

                self.update_main_display()

            except Exception as e:
                print(f"Error loading ARW file: {e}")

    def align_images(self):
        """Align all channels to the first channel (Red)"""
        self.aligned = [self.original_images[0].copy(), 
                    self.original_images[1].copy(),
                    self.original_images[2].copy()]

        orb = cv2.ORB_create()
        keypoints = []
        descriptors = []

        for img in self.original_images:
            kp, des = orb.detectAndCompute(img, None)
            keypoints.append(kp)
            descriptors.append(des)

        # Wyrównaj do czerwonego kanału (indeks 0)
        for i in range(1, 3):
            if descriptors[0] is not None and descriptors[i] is not None:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches = bf.match(descriptors[0], descriptors[i])  # Porównaj z czerwonym

                if len(matches) > 10:
                    src_pts = np.float32([keypoints[0][m.queryIdx].pt for m in matches]).reshape(-1,1,2)
                    dst_pts = np.float32([keypoints[i][m.trainIdx].pt for m in matches]).reshape(-1,1,2)

                    # Użyj transformacji afinicznej zamiast homografii
                    M, _ = cv2.estimateAffinePartial2D(dst_pts, src_pts)
                    if M is not None:
                        self.aligned[i] = cv2.warpAffine(
                            self.original_images[i], M, 
                            (self.original_images[0].shape[1], self.original_images[0].shape[0])
                        )

        self.processed = [img.copy() for img in self.aligned]
        self.recalculate_from_original()
        
    def apply_adjustments(self, channel_idx):
        """Apply brightness/contrast adjustments to specified channel"""
        if self.aligned[channel_idx] is None:
            return

        # Pobierz wartości z suwaków
        brightness = self.get_controller(channel_idx).slider_brightness.value()
        contrast = self.get_controller(channel_idx).slider_contrast.value() / 100
        
        # Zastosuj korekty
        img = self.aligned[channel_idx].astype(np.float32)
        img = img * (1 + contrast) + brightness
        self.processed[channel_idx] = np.clip(img, 0, 255).astype(np.uint8)


    def recalculate_from_original(self):
        """Reapply adjustments from original aligned images"""
        for i in range(3):
            if self.aligned[i] is not None:
                self.processed[i] = self.aligned[i].copy()
                self.apply_adjustments(i) 

        self.update_main_display()

    def adjust_channel(self, channel_idx, adjustment_type, value):
        self.apply_adjustments(channel_idx)  # Bezpośrednie wywołanie
        self.update_main_display()

    def update_channel_preview(self, channel_idx):
        controller = [self.red_controller,
                      self.green_controller,
                      self.blue_controller][channel_idx]
        controller.processed_image = self.processed[channel_idx]
        controller.update_preview()

    def show_single_channel(self, channel_idx):
        self.show_combined = False
        self.current_channel = channel_idx
        self.update_main_display()
        
    def toggle_output_display(self):
        """Toggle output display on right-click"""
        self.show_output = not self.show_output
        self.update_main_display()

    def update_main_display(self):
        """Update the main display based on the current state."""
        if self.show_output:
            self.show_output_image()
        elif self.show_combined:
            self.show_combined_image()
        else:
            self.show_single_channel_image()

        if self.viewer._photo.pixmap():
            pixmap = self.viewer._photo.pixmap()
            self.viewer.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))
            
    def generate_output_image(self):
        """Create output from processed channels"""
        output = np.zeros((*self.processed[0].shape, 3), dtype=np.uint8)
        for i in range(3):
            output[:,:,i] = self.processed[i] * self.get_intensity(i)
        return cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            
    def show_output_image(self):
        """Display final output image combining all channels"""
        # Check if any channel hasn't been processed
        if any(img is None for img in self.processed):
            return

        # Create output image from processed channels
        output = np.zeros((*self.processed[0].shape, 3), dtype=np.float32)
        
        # Apply intensity and combine channels
        for i in range(3):
            intensity = self.get_controller(i).slider_intensity.value() / 100
            output[:, :, i] = self.processed[i].astype(np.float32) * intensity

        # Convert to 8-bit and display
        output = np.clip(output, 0, 255).astype(np.uint8)
        q_img = QImage(output.data, output.shape[1], output.shape[0],
                    output.strides[0], QImage.Format_RGB888)
        self.viewer.set_image(QPixmap.fromImage(q_img))

    def show_combined_image(self):
        """Display combined RGB view of all channels"""
        # Check if any channel is unprocessed
        if any(img is None for img in self.processed):
            return

        # Combine channels
        combined = np.zeros((*self.processed[0].shape, 3), dtype=np.float32)
        
        for i in range(3):
            intensity = self.get_controller(i).slider_intensity.value() / 100
            combined[:, :, i] = self.processed[i].astype(np.float32) * intensity
        
        # Convert and display
        combined = np.clip(combined, 0, 255).astype(np.uint8)
        q_img = QImage(combined.data, combined.shape[1], combined.shape[0],
                    combined.strides[0], QImage.Format_RGB888)
        self.viewer.set_image(QPixmap.fromImage(q_img))


    def show_single_channel_image(self):
        if self.processed[self.current_channel] is not None:
            img = cv2.cvtColor(self.processed[self.current_channel], cv2.COLOR_GRAY2RGB)
            q_img = QImage(img.data, img.shape[1], img.shape[0],
                           img.strides[0], QImage.Format_RGB888)
            self.viewer.set_image(QPixmap.fromImage(q_img))

    def get_controller(self, index):
        return [self.red_controller, self.green_controller, self.blue_controller][index]
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.toggle_output_display()
        else:
            super().mousePressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessor()
    ex.show()
    sys.exit(app.exec_())
