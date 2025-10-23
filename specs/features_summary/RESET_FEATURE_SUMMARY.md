# Reset to Defaults Feature - Implementation Summary

## Overview
Added a "New" button that resets the entire application to its initial state, clearing all loaded images, resetting all slider values, clearing crops, and restoring the default display mode.

## Changes Made

### 1. New File: `src/default_state.py`
Created a centralized configuration class that holds all default values for the application.

**Features:**
- `DefaultState` class with class-level constants for all defaults
- `SliderDefaults` dataclass for slider default values (brightness: 0, contrast: 0, intensity: 100)
- `get_slider_defaults()` method to retrieve slider defaults as a dictionary
- Constants for display defaults (SHOW_COMBINED: True, CURRENT_CHANNEL: 0)
- Constants for crop defaults (CROP_MODE: False)

**Purpose:**
- Single source of truth for default values
- Ensures consistency between application startup and reset operations
- Makes it easy to modify default values in one place

### 2. Modified: `src/main_window.py`

#### Imports
- Added import for `DefaultState` class

#### Constructor Changes
- Updated initial state values to use `DefaultState` constants instead of hardcoded values:
  - `self.show_combined = DefaultState.SHOW_COMBINED`
  - `self.current_channel = DefaultState.CURRENT_CHANNEL`
  - `self.crop_mode = DefaultState.CROP_MODE`

#### UI Changes
- Added "New" button to the UI layout
- Positioned before "Save" and "Crop" buttons
- Connected to `reset_to_defaults()` method

#### New Method: `reset_to_defaults()`
Comprehensive reset method that:
1. **Clears all image data:**
   - `original_images` - clears backup of original loaded images
   - `aligned` - clears aligned/processed images
   - `processed` - clears processed images with adjustments
   - `original_rgb_images` - clears original RGB composite images
   - `aligned_rgb` - clears aligned RGB composite images

2. **Resets display state:**
   - `show_combined` - resets to combined RGB view
   - `current_channel` - resets to red channel (0)

3. **Resets crop state:**
   - Exits crop mode if currently active
   - Clears `crop_rect` and `crop_ratio`
   - Clears saved crop from viewer
   - Resets crop ratio combo box to "Free" (index 0)

4. **Resets all channel controllers:**
   - Calls `reset_all_sliders()` on each controller
   - Calls `clear_image()` on each controller

5. **Updates UI:**
   - Clears the main image viewer
   - Updates save button state (disables it)
   - Updates mode indicator
   - Shows status message

### 3. Modified: `src/widgets/channel_controller.py`

#### Imports
- Added import for `DefaultState` class

#### Constructor Changes
- Modified slider configuration to use `DefaultState.get_slider_defaults()`
- Ensures slider defaults are centrally managed

#### New Methods

**`reset_all_sliders()`:**
- Resets all sliders (brightness, contrast, intensity) to their default values
- Emits `value_changed` signal once after all sliders are reset
- Used when resetting the entire application state

**`clear_image()`:**
- Clears the `processed_image` attribute
- Resets preview to placeholder (gray box)
- Used when resetting channel state

### 4. Modified: `src/widgets/image_viewer.py`

#### New Method: `clear_image()`
- Removes the current pixmap from the scene
- Creates a new empty pixmap item
- Resets scene rectangle to (0, 0, 0, 0)
- Resets zoom to 1.0
- Resets fit_to_view to False
- Calls `resetTransform()` to reset view transformations

## User Experience

### How to Use the New Button
1. **Click the "New" button** at the top-left of the window (before Save and Crop buttons)
2. All images will be cleared from all channels
3. All sliders will return to their default positions
4. Any active crop will be cancelled and cleared
5. The display will show an empty viewer
6. Status bar will display: "Application reset to default state"

### What Gets Reset
- ✅ All loaded images (no images in any channel)
- ✅ Red channel sliders: brightness=0, contrast=0, intensity=100
- ✅ Green channel sliders: brightness=0, contrast=0, intensity=100
- ✅ Blue channel sliders: brightness=0, contrast=0, intensity=100
- ✅ Channel previews: show placeholder (gray box)
- ✅ Crop settings: cleared
- ✅ Crop mode: disabled
- ✅ Crop ratio: reset to "Free"
- ✅ Main viewer: cleared
- ✅ Display mode: combined RGB view
- ✅ Selected channel: red (channel 0)
- ✅ Save button: disabled

## Implementation Benefits

1. **Centralized Configuration:**
   - All defaults in one place (`DefaultState` class)
   - Easy to modify defaults in the future
   - Consistent initialization and reset behavior

2. **Clean Architecture:**
   - Separation of concerns (state management vs UI)
   - Reusable components (`reset_all_sliders()`, `clear_image()`)
   - Clear method responsibilities

3. **User-Friendly:**
   - Quick way to start fresh without restarting the application
   - Clear feedback via status message
   - Predictable behavior (returns to startup state)

4. **Maintainable:**
   - Well-documented methods
   - Type hints throughout
   - Follows existing code patterns and style

## Testing Checklist

- [ ] Click "New" button with no images loaded
- [ ] Click "New" button with images loaded in all channels
- [ ] Click "New" button with adjusted sliders
- [ ] Click "New" button while in crop mode
- [ ] Click "New" button with active crop applied
- [ ] Verify all sliders reset to correct defaults
- [ ] Verify all images are cleared
- [ ] Verify main viewer is cleared
- [ ] Verify crop settings are cleared
- [ ] Verify status message appears
- [ ] Verify Save button is disabled after reset
- [ ] Load images after reset to ensure normal functionality

## Future Enhancements

Possible improvements for future versions:
- Add confirmation dialog before reset (optional setting)
- Add keyboard shortcut for reset (e.g., Ctrl+N)
- Save/load workspace state (save current settings to file)
- Undo/redo functionality for reset action
