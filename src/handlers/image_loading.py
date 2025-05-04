import rawpy
import cv2
from PyQt5.QtWidgets import QFileDialog

def load_raw_image(parent):
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(
        parent, "Select ARW File", "", 
        "Sony RAW Files (*.arw)", options=options)
    
    if not filename:
        return None
        
    try:
        with rawpy.imread(filename) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                no_auto_bright=True,
                output_bps=8
            )
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    except Exception as e:
        print(f"Error loading ARW file: {e}")
        return None
