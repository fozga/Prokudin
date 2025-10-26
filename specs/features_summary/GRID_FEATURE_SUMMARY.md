# Grid Overlay Feature - Implementation Summary

## Overview
Added grid overlay functionality to the image display that helps with composition. The feature supports multiple grid types including rule-of-thirds (3x3) and golden ratio (1:0.618:1) grids. In crop mode, the grid is visible only within the selected crop area and updates dynamically as the user modifies the crop. Outside crop mode, the grid is visible on the entire displayed preview.

Users can control the grid through a dedicated Grid button in the left sidebar, which opens a popup dialog for selecting grid type and adjusting line width.

## Changes Made

### 1. New File: `src/widgets/grid_overlay.py`
Created a dedicated class to manage and draw the grid overlay.

**Features:**
- `GridOverlay` class with configurable grid settings
- Multiple grid types support:
  - **3x3 Grid**: Rule-of-thirds grid (2 vertical and 2 horizontal lines at 1/3 and 2/3 positions)
  - **Golden Ratio Grid**: Based on golden ratio (1:0.618:1) with lines at 0.382 and 0.618 positions
- Semi-transparent white lines (128/255 opacity)
- Configurable line width (1-10 pixels, default 4)
- Support for both QRect and QRectF rectangle types

**Key Methods:**
- `__init__()` - Initializes grid with default settings (enabled, 3x3 grid type, white color, 4px width, solid lines, 128 opacity)
- `set_enabled(enabled)` - Enable/disable grid display
- `is_enabled()` - Check if grid is enabled
- `set_color(color)` - Set grid line color
- `set_line_width(width)` - Set grid line width (1-10 pixels)
- `get_line_width()` - Get current line width
- `set_opacity(opacity)` - Set transparency (0-255)
- `set_grid_type(grid_type)` - Set grid type (3x3 or golden_ratio)
- `get_grid_type()` - Get current grid type
- `draw_grid(painter, rect)` - Main drawing method that delegates to specific grid type
- `_draw_3x3_grid(painter, rect)` - Draws rule-of-thirds grid
- `_draw_golden_ratio_grid(painter, rect)` - Draws golden ratio grid

**Grid Types:**
- **GRID_TYPE_3X3**: Lines at 1/3 and 2/3 positions (rule-of-thirds composition)
- **GRID_TYPE_GOLDEN_RATIO**: Lines at 0.382 and 0.618 positions (golden ratio φ = 1.618)

**Design:**
- Grid type determines line positioning
- 3x3 grid divides image into 9 equal parts
- Golden ratio grid uses aesthetically pleasing ratio found in nature
- Uses QPainter for efficient rendering
- Configurable properties allow UI controls for user customization
- Works in both scene coordinates and viewport coordinates

### 2. New File: `src/widgets/grid_settings_dialog.py`
Created a popup dialog for grid settings configuration.

**Features:**
- `GridSettingsDialog` class extending QFrame
- Frameless popup window that overlays the main window
- Closes automatically when clicking outside the dialog
- Line width control at the top with +/- buttons and display
- List widget showing available grid types

**Components:**
- **Line Width Control:**
  - Decrease button (-)
  - Width display (non-editable, shows current value)
  - Increase button (+)
  - Range: 1-10 pixels
  - Default: 4 pixels

- **Grid Type List:**
  - "None" - Disables grid overlay
  - "3x3 Grid" - Rule of thirds grid (default)
  - "Golden Ratio" - Golden ratio grid (1:0.618:1)
  - Future: More grid types can be easily added

**Signals:**
- `grid_type_changed(str)` - Emitted when user selects a different grid type
- `line_width_changed(int)` - Emitted when user changes line width

**Positioning:**
- Anchors bottom-left corner to top-left of Grid button
- Opens above and to the right of the button
- Fixed size: 200x200 pixels

### 3. Modified: `src/widgets/image_viewer.py`

#### Imports
- Added import for `GridOverlay` class

#### Constructor Changes
- Added `self._grid_overlay = GridOverlay()` to initialize grid overlay instance

#### New Properties
- Added `@property grid_overlay` - Public property to access the grid overlay instance
- Added `@property crop_handler` - Public property to access the crop handler instance

#### Modified Method: `drawForeground()`
Enhanced the foreground drawing method to include grid overlay:

**Changes:**
1. Added grid drawing for non-crop mode:
   - Gets the visible scene rectangle (`self.mapToScene(self.viewport().rect()).boundingRect()`)
   - Draws grid overlay on entire visible preview area
   - Grid updates automatically when user zooms or pans

**Behavior:**
- Grid is drawn on top of the image but below crop rectangle
- Grid automatically scales with zoom level
- Grid follows pan operations
- Grid remains visible during all image adjustments (brightness, contrast, etc.)

### 4. Modified: `src/widgets/crop_handler.py`

#### Constructor Changes
- **Now accepts a shared `grid_overlay` parameter** instead of creating its own instance
- Stores reference as `self._grid_overlay` to the shared GridOverlay from the viewer
- This eliminates duplication and ensures consistent grid state across viewer and crop modes

#### Architecture Change
- **Removed the `@property grid_overlay`** - No longer needed since grid state is managed centrally
- The crop handler uses the shared grid overlay internally via `self._grid_overlay`
- Grid state changes in the viewer automatically apply to crop mode (same instance)

#### Modified Method: `draw_foreground()`
Enhanced the crop mode drawing to include grid within crop rectangle:

**Changes:**
1. Added grid drawing within crop rectangle:
   - Checks if crop rectangle exists and is valid
   - Draws grid overlay only within the selected crop area
   - Grid is clipped to crop rectangle boundaries

**Behavior:**
- Grid appears only inside the crop selection
- Grid updates in real-time as user drags crop rectangle
- Grid updates when user resizes crop rectangle
- Grid scales with the crop area dimensions
- Grid maintains 1/3 and 2/3 divisions within the crop bounds

### 5. Modified: `src/main_window.py`

#### Imports
- Added import for `GridSettingsDialog` class

#### Constructor Changes
- Added `self.grid_settings_dialog: Union[GridSettingsDialog, None] = None` to track the dialog instance

#### UI Layout Changes
- **Added Left Sidebar:**
  - New vertical layout on the left (5% width)
  - Contains stretch to push content to bottom
  - "Grid" button at the bottom of the sidebar
  
- **Reorganized Center Panel:**
  - Moved image viewer to center panel (70% width)
  - Kept New, Save, and Crop buttons at the top
  - Maintained crop controls widget

- **Layout Structure:**
  - Left sidebar (5%): Grid button
  - Center panel (70%): Viewer and controls
  - Right panel (25%): Channel controllers

#### New Methods

**`open_grid_settings()`**
- Opens the grid settings dialog as an overlay popup
- Creates dialog on first call with current settings
- Connects dialog signals to handler methods
- Positions dialog above and to the right of Grid button
- Dialog appears at: button top-left + button width + 10px right, button top - dialog height

**`on_grid_type_changed(grid_type: str)`**
- Handles grid type selection changes from dialog
- Supports three grid types:
  - "none": Disables the grid overlay
  - "3x3": Enables rule-of-thirds grid (lines at 1/3 and 2/3)
  - "golden_ratio": Enables golden ratio grid (lines at 0.382 and 0.618)
- Updates the grid type in the shared grid overlay
- Enables/disables the shared grid overlay in viewer (automatically applies to crop mode)
- Updates status bar with current grid state
- Refreshes viewport to show changes immediately

**`on_grid_line_width_changed(width: int)`**
- Handles line width changes from dialog
- Updates line width in the shared grid overlay (automatically applies to both modes)
- Refreshes viewport to show changes immediately
- Displays new width in status bar

## Architecture

### Shared Grid Overlay Design
- **Single Source of Truth:** Only one `GridOverlay` instance exists (owned by `ImageViewer`)
- **Shared Reference:** `CropHandler` receives and uses the same instance
- **Multiple Grid Types:** Supports different composition guides (3x3, golden ratio)
- **Benefits:**
  - No synchronization issues between viewer and crop modes
  - Simpler state management - changes apply everywhere automatically
  - Easier to extend with new grid types or features
  - Reduced memory footprint
  - More maintainable codebase

### Technical Details

### Coordinate System
- Grid uses scene coordinates for consistency
- Automatically transforms between viewport and scene coordinates
- Works correctly with zoom and pan operations

### Drawing Order
1. Base image (background)
2. Grid overlay (foreground)
3. Crop rectangle (foreground, in crop mode)
4. Crop handles (foreground, in crop mode)

### Performance
- Grid is redrawn only when necessary (pan, zoom, crop changes, settings changes)
- Uses efficient QPainter drawing methods
- Minimal performance impact
- Dialog is created once and reused

### Public API
To avoid accessing protected members, public properties were added:
- `ImageViewer.grid_overlay` - Access to the shared grid overlay instance
- `ImageViewer.crop_handler` - Access to crop handler
- `GridOverlay.get_line_width()` - Get current line width

Note: The `CropHandler` no longer exposes a `grid_overlay` property since it uses the shared instance from the viewer. All grid state management is centralized in `MainWindow` through the viewer's grid overlay.

## User Experience

### Visual Feedback
- Semi-transparent white lines for good visibility on most images
- Configurable line width (1-10 pixels) for user preference
- Multiple grid types for different composition techniques:
  - **3x3 Grid**: Classic rule-of-thirds (divides image into 9 equal parts)
  - **Golden Ratio**: Aesthetically pleasing ratio based on φ ≈ 1.618 (lines at 38.2% and 61.8%)
- Grid can be completely disabled via "None" option

### Grid Control Dialog
- **Access:** Click "Grid" button in left sidebar
- **Appearance:** Popup overlay above the Grid button
- **Controls:** 
  - Line width adjustment at top
  - Grid type selection below
- **Behavior:** 
  - Changes apply immediately
  - Closes when clicking outside
  - Can be reopened anytime

### Behavior in Different Modes
1. **Normal Mode (no crop):**
   - Grid covers entire visible preview area
   - Grid scales with zoom
   - Grid moves with pan

2. **Crop Mode:**
   - Grid appears only within crop rectangle
   - Grid updates in real-time during crop adjustments
   - Grid helps align composition within the crop area
   - Grid disappears outside crop boundaries

### Integration
- Grid is enabled by default (3x3 grid)
- Grid works seamlessly with existing features:
  - Image loading
  - Channel switching
  - RGB combined view
  - Brightness/contrast/intensity adjustments
  - Zoom and pan operations
  - Crop mode
- Grid button always accessible in left sidebar
- Settings persist during session (until grid type is changed)
- Multiple grid types available for different composition preferences

## Future Enhancements
Potential improvements for future versions:
- Additional grid patterns (diagonal lines, center lines, phi grid)
- Grid color customization
- Grid line style options (dashed, dotted)
- Grid visibility based on zoom level
- Keyboard shortcut to toggle grid
- Save grid preferences between sessions
- Custom grid configurations
- Grid opacity controls in UI

## Dependencies
- PyQt5.QtCore (QRect, QRectF, Qt)
- PyQt5.QtGui (QColor, QPainter, QPen)
- PyQt5.QtWidgets (QFrame, QListWidget, QLabel, QPushButton, etc.)

## Testing
See `GRID_FEATURE_TESTING.md` for comprehensive manual testing scenarios.
