# Copyright (C) 2025 fozga
#
# This file is part of Prokudin.
#
# Prokudin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prokudin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prokudin.  If not, see <https://www.gnu.org/licenses/>.

"""
Image processing utilities for channel adjustment, combination, and conversion for display.
Includes brightness/contrast adjustment, channel combination, and conversion to QImage.
"""

from typing import List, Union

import numpy as np
from PyQt5.QtGui import QImage


def apply_adjustments(
    image: Union[np.ndarray, None], brightness: int = 0, contrast: int = 0
) -> Union[np.ndarray, None]:
    """
    Applies brightness and contrast adjustments to a grayscale image.

    Args:
        image (numpy.ndarray or None): Input 8-bit grayscale image (shape: HxW).
        brightness (int): [-100, 100] - additive brightness adjustment.
        contrast (int): [-100, 100] - multiplicative contrast adjustment (percentage).

    Returns:
        numpy.ndarray: Adjusted 8-bit image (uint8) or None if input is invalid.

    Example:
        >>> adjusted = apply_adjustments(img, brightness=20, contrast=10)

    Cross-references:
        - handlers.channels.adjust_channel
    """
    if image is None:
        return None

    img = image.astype(np.float32)
    img = img * (1 + contrast / 100) + brightness
    return np.clip(img, 0, 255).astype(np.uint8)


def combine_channels(channels: List[Union[np.ndarray, None]], intensities: List[int]) -> Union[np.ndarray, None]:
    """
    Combines three grayscale channels into RGB image with intensity adjustments.

    Args:
        channels (list of numpy.ndarray): [R, G, B] 8-bit grayscale images (uint8, shape: HxW).
        intensities (list of int): [R%, G%, B%] intensity multipliers (0-200%).

    Returns:
        numpy.ndarray | None: Combined 8-bit RGB image (uint8, shape: HxWx3)
                    or None if any channel missing

    Cross-references:
        - handlers.display.show_combined_image
    """
    if any(channel is None for channel in channels):
        return None

    # Assert to help type checker understand all channels are now definitely not None
    assert all(channel is not None for channel in channels)

    # Create a new variable with a definite non-None type
    valid_channels: List[np.ndarray] = [c for c in channels if c is not None]

    combined = np.zeros((*valid_channels[0].shape, 3), dtype=np.float32)
    for i in range(3):
        combined[:, :, i] = valid_channels[i].astype(np.float32) * (intensities[i] / 100)

    return np.clip(combined, 0, 255).astype(np.uint8)


def convert_to_qimage(image: Union[np.ndarray, None]) -> QImage:
    """
    Converts numpy image to QImage for PyQt5 display.

    Args:
        image (numpy.ndarray | None):
            - Grayscale: HxW (uint8)
            - RGB: HxWx3 (uint8)

    Returns:
        QImage: Empty QImage if input invalid, otherwise formatted image.

    Cross-references:
        - handlers.display.show_combined_image
        - handlers.display.show_single_channel_image
    """
    if image is None:
        return QImage()

    if len(image.shape) == 2:  # Grayscale
        return QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8)

    return QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
