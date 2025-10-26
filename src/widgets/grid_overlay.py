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
Grid overlay for image viewer.
Provides various grid types for composition guidance, including rule-of-thirds (3x3)
and golden ratio grids.
"""

from typing import Union

from PyQt5.QtCore import QRect, QRectF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen


class GridOverlay:
    """
    Manages and draws grid overlays on images.

    Supports multiple grid types:
    - 3x3: Divides the image into 9 equal parts (rule-of-thirds)
    - Golden Ratio: Uses the golden ratio (1:0.618:1) for grid lines
    """

    # Grid type constants
    GRID_TYPE_3X3 = "3x3"
    GRID_TYPE_GOLDEN_RATIO = "golden_ratio"

    def __init__(self) -> None:
        """Initialize the grid overlay with default settings."""
        self._enabled = True
        self._color = QColor("white")
        self._line_width = 4
        self._line_style = Qt.PenStyle.SolidLine
        self._opacity = 128  # Semi-transparent (0-255)
        self._grid_type = self.GRID_TYPE_3X3  # Default to 3x3 grid

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the grid overlay.

        Args:
            enabled: True to show the grid, False to hide it.
        """
        self._enabled = enabled

    def is_enabled(self) -> bool:
        """
        Check if the grid is enabled.

        Returns:
            bool: True if grid is enabled, False otherwise.
        """
        return self._enabled

    def set_color(self, color: QColor) -> None:
        """
        Set the color of the grid lines.

        Args:
            color: The color to use for grid lines.
        """
        self._color = color

    def set_line_width(self, width: int) -> None:
        """
        Set the width of the grid lines.

        Args:
            width: Line width in pixels.
        """
        self._line_width = width

    def get_line_width(self) -> int:
        """
        Get the current line width.

        Returns:
            int: The current line width in pixels.
        """
        return self._line_width

    def set_opacity(self, opacity: int) -> None:
        """
        Set the opacity of the grid lines.

        Args:
            opacity: Opacity value from 0 (transparent) to 255 (opaque).
        """
        self._opacity = max(0, min(255, opacity))

    def set_grid_type(self, grid_type: str) -> None:
        """
        Set the grid type.

        Args:
            grid_type: The grid type to use (GRID_TYPE_3X3 or GRID_TYPE_GOLDEN_RATIO).
        """
        self._grid_type = grid_type

    def get_grid_type(self) -> str:
        """
        Get the current grid type.

        Returns:
            str: The current grid type.
        """
        return self._grid_type

    def draw_grid(self, painter: QPainter, rect: Union[QRect, QRectF]) -> None:
        """
        Draw the grid lines on the given rectangle.

        Args:
            painter: QPainter object to draw with.
            rect: The rectangle area to draw the grid on (QRect or QRectF).
        """
        if not self._enabled:
            return

        # Convert QRect to QRectF if needed
        if isinstance(rect, QRect):
            rect = QRectF(rect)

        # Save the current painter state
        painter.save()

        # Set up the pen for drawing grid lines
        color = QColor(self._color)
        color.setAlpha(self._opacity)
        pen = QPen(color, self._line_width, self._line_style)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw grid based on type
        if self._grid_type == self.GRID_TYPE_3X3:
            self._draw_3x3_grid(painter, rect)
        elif self._grid_type == self.GRID_TYPE_GOLDEN_RATIO:
            self._draw_golden_ratio_grid(painter, rect)

        # Restore the painter state
        painter.restore()

    def _draw_3x3_grid(self, painter: QPainter, rect: QRectF) -> None:
        """
        Draw a rule-of-thirds (3x3) grid.

        Args:
            painter: QPainter object to draw with.
            rect: The rectangle area to draw the grid on.
        """
        # Calculate positions for rule-of-thirds lines
        left = rect.left()
        top = rect.top()
        width = rect.width()
        height = rect.height()

        # Vertical lines at 1/3 and 2/3
        x1 = left + width / 3.0
        x2 = left + 2.0 * width / 3.0

        # Horizontal lines at 1/3 and 2/3
        y1 = top + height / 3.0
        y2 = top + 2.0 * height / 3.0

        # Draw the vertical lines
        painter.drawLine(int(x1), int(top), int(x1), int(top + height))
        painter.drawLine(int(x2), int(top), int(x2), int(top + height))

        # Draw the horizontal lines
        painter.drawLine(int(left), int(y1), int(left + width), int(y1))
        painter.drawLine(int(left), int(y2), int(left + width), int(y2))

    def _draw_golden_ratio_grid(self, painter: QPainter, rect: QRectF) -> None:
        """
        Draw a golden ratio grid (1:0.618:1).

        The golden ratio divides the image using the ratio 1:0.618:1,
        which is approximately 0.382 and 0.618 of the total dimension.

        Args:
            painter: QPainter object to draw with.
            rect: The rectangle area to draw the grid on.
        """
        # Calculate positions for golden ratio lines
        left = rect.left()
        top = rect.top()
        width = rect.width()
        height = rect.height()

        # Golden ratio: φ = 1.618...
        # For 1:0.618:1 ratio, the lines are at 0.382 and 0.618
        golden_ratio_small = 0.382  # 1 / (1 + φ) ≈ 0.382
        golden_ratio_large = 0.618  # φ / (1 + φ) ≈ 0.618

        # Vertical lines at golden ratio positions
        x1 = left + width * golden_ratio_small
        x2 = left + width * golden_ratio_large

        # Horizontal lines at golden ratio positions
        y1 = top + height * golden_ratio_small
        y2 = top + height * golden_ratio_large

        # Draw the vertical lines
        painter.drawLine(int(x1), int(top), int(x1), int(top + height))
        painter.drawLine(int(x2), int(top), int(x2), int(top + height))

        # Draw the horizontal lines
        painter.drawLine(int(left), int(y1), int(left + width), int(y1))
        painter.drawLine(int(left), int(y2), int(left + width), int(y2))
