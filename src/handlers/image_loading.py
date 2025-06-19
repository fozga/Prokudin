# Copyright (C) 2025 fozga
#
# This file is part of FullSpectrumProcessor.
#
# FullSpectrumProcessor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FullSpectrumProcessor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FullSpectrumProcessor.  If not, see <https://www.gnu.org/licenses/>.

"""
Image loading utilities for selecting and processing Sony ARW RAW files.
Provides functions to open file dialogs, load RAW images, and convert them for further processing.
"""

from typing import Union

import numpy as np
import rawpy  # type: ignore
from PyQt5.QtWidgets import QFileDialog, QWidget


def load_raw_image(parent: QWidget) -> Union[tuple[np.ndarray, None], tuple[None, str]]:
    """
    Opens a file dialog for the user to select a Sony ARW RAW image,
    loads the image using rawpy, and processes it to an 8-bit RGB image.

    Args:
        parent (QWidget): The parent widget for the QFileDialog (typically the main window).

    Returns:
        tuple: Either (numpy.ndarray, None) with the 3D RGB image as a NumPy array
        (dtype=uint8, shape: HxWx3) and no error, or (None, str) with an error message
        if loading fails or is cancelled.

    Workflow:
        1. Opens a QFileDialog for ARW file selection.
        2. Loads the selected file with rawpy and applies camera white balance.
        3. Disables automatic brightness correction, outputs 8 bits per sample.
        4. Returns the RGB image directly for further processing.
        5. Handles errors gracefully, returning None and an error message.

    Example:
        rgb_image, error = load_raw_image(self)
        if error:
            print(error)
        elif rgb_image is not None:
            # Convert to grayscale if needed
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            # Proceed with processing

    Cross-references:
        - handlers.channels.load_channel
    """
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(parent, "Select ARW File", "", "Sony RAW Files (*.arw)", options=options)

    if not filename:
        return None, "No file selected"

    try:
        with rawpy.imread(filename) as raw:
            rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
        # Return the RGB image directly without converting to grayscale
        result: np.ndarray = rgb
        return result, None
    except (
        rawpy.LibRawFileUnsupportedError,  # pylint: disable=E1101
        rawpy.LibRawIOError,  # pylint: disable=E1101
        FileNotFoundError,
        PermissionError,
    ) as e:  # pylint: disable=E1101
        error_message = f"Error loading ARW file: {e}"
        return None, error_message
