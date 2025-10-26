# Manual Testing Guide for Grid Feature

## Test Scenarios

### Scenario 1: Grid Button and Dialog Access
**Steps:**
1. Launch the application
2. Observe the left sidebar
3. Locate the "Grid" button at the bottom of the left sidebar
4. Click the "Grid" button

**Expected Results:**
- ✅ "Grid" button is visible in left sidebar
- ✅ Button is at the bottom of the sidebar
- ✅ Clicking button opens Grid Settings dialog
- ✅ Dialog appears as overlay above and to the right of button
- ✅ Dialog is 200x200 pixels
- ✅ Dialog has styled frame with raised shadow

### Scenario 2: Grid Settings Dialog Content
**Steps:**
1. Click the "Grid" button
2. Observe the dialog contents
3. Check for all UI elements

**Expected Results:**
- ✅ Dialog shows "Line Width:" label at top
- ✅ Minus (-) button is present
- ✅ Width display shows current value (default: 4)
- ✅ Plus (+) button is present
- ✅ "Grid Type:" label is present
- ✅ List shows "None" option
- ✅ List shows "3x3 Grid" option
- ✅ "3x3 Grid" is selected by default
- ✅ All elements are properly aligned

### Scenario 3: Grid Line Width Controls
**Steps:**
1. Click the "Grid" button to open settings
2. Note the current width value
3. Click the "+" button multiple times
4. Observe the width value and grid lines
5. Click the "-" button multiple times
6. Try to go below 1 or above 10

**Expected Results:**
- ✅ Width starts at 4 pixels
- ✅ "+" button increases width by 1
- ✅ Width display updates immediately
- ✅ Grid lines become thicker in real-time
- ✅ "-" button decreases width by 1
- ✅ Grid lines become thinner in real-time
- ✅ Cannot go below 1 pixel (button disabled at 1)
- ✅ Cannot go above 10 pixels (button disabled at 10)
- ✅ Status bar shows width change message
- ✅ Changes persist while dialog is open

### Scenario 4: Grid Type Selection
**Steps:**
1. Load images in all channels
2. Click the "Grid" button
3. Verify "3x3 Grid" is selected
4. Click on "None" in the list
5. Observe the grid overlay
6. Click on "3x3 Grid" again
7. Observe the grid overlay

**Expected Results:**
- ✅ Selecting "None" disables grid immediately
- ✅ Grid disappears from viewer
- ✅ Grid disappears from crop area (if in crop mode)
- ✅ Status bar shows "Grid overlay disabled"
- ✅ Selecting "3x3 Grid" enables grid immediately
- ✅ Grid appears on viewer
- ✅ Grid appears in crop area (if in crop mode)
- ✅ Status bar shows "3x3 grid overlay enabled"
- ✅ Changes apply without closing dialog

### Scenario 5: Dialog Positioning
**Steps:**
1. Click the "Grid" button
2. Observe where the dialog appears
3. Note the position relative to the button
4. Close the dialog (click outside)
5. Click the "Grid" button again

**Expected Results:**
- ✅ Dialog bottom-left corner aligns with button top-left
- ✅ Dialog opens above the Grid button
- ✅ Dialog opens to the right of the button
- ✅ Dialog doesn't overlap the button
- ✅ Dialog position is consistent on reopen
- ✅ Dialog is fully visible on screen

### Scenario 6: Dialog Closing Behavior
**Steps:**
1. Click the "Grid" button to open dialog
2. Click somewhere on the image viewer
3. Open dialog again
4. Click on a channel controller
5. Open dialog again
6. Click on the dialog itself
7. Click outside the dialog

**Expected Results:**
- ✅ Clicking on viewer closes dialog
- ✅ Grid settings remain applied
- ✅ Clicking on channel controller closes dialog
- ✅ Clicking inside dialog keeps it open
- ✅ Can interact with dialog controls
- ✅ Clicking outside dialog closes it
- ✅ All settings are preserved after closing

### Scenario 7: Grid in Empty Application
**Steps:**
1. Launch the application
2. Observe the main viewer area
3. Click the "Grid" button
4. Change grid settings

**Expected Results:**
- ✅ No grid is visible (no image loaded)
- ✅ Application displays empty viewer
- ✅ Grid settings dialog works normally
- ✅ Settings are saved for when image is loaded
- ✅ No errors or crashes

### Scenario 8: Grid Appears with Loaded Image
**Steps:**
1. Launch the application
2. Load an image in the Red channel
3. Load an image in the Green channel
4. Load an image in the Blue channel
5. Observe the combined RGB image display

**Expected Results:**
- ✅ Grid overlay is visible on the image
- ✅ Grid has 2 horizontal lines at 1/3 and 2/3 height
- ✅ Grid has 2 vertical lines at 1/3 and 2/3 width
- ✅ Grid divides image into 9 equal parts
- ✅ Grid lines are white, semi-transparent, and clearly visible
- ✅ Grid lines are 4 pixels wide (default)

### Scenario 9: Changing Line Width with Visible Grid
**Steps:**
1. Load images in all channels
2. Observe default grid (4px width)
3. Click "Grid" button
4. Click "+" button to increase to 8px
5. Observe grid changes
6. Click "-" button to decrease to 2px
7. Observe grid changes
8. Set back to default (4px)

**Expected Results:**
- ✅ Grid lines update immediately after each click
- ✅ Thicker lines (8px) are very prominent
- ✅ Thinner lines (2px) are more subtle
- ✅ Grid divisions remain at 1/3 and 2/3
- ✅ Grid remains smooth and anti-aliased
- ✅ No flickering during width changes
- ✅ Status bar shows width changes
- ✅ Changes apply to both normal and crop grids

### Scenario 10: Grid with Single Channel View
**Steps:**
1. Load images in all channels
2. Switch to Red channel only view
3. Switch to Green channel only view
4. Switch to Blue channel only view
5. Switch back to combined RGB view

**Expected Results:**
- ✅ Grid remains visible in all single-channel views
- ✅ Grid position and divisions remain consistent
- ✅ Grid updates correctly when switching between channels
- ✅ Grid maintains proper 1/3 divisions in each view

### Scenario 11: Grid with Zoom Operations
**Steps:**
1. Load images in all channels
2. Verify grid is visible
3. Zoom in using mouse wheel or zoom controls
4. Observe grid at various zoom levels (2x, 4x, etc.)
5. Zoom out to fit view
6. Zoom out further

**Expected Results:**
- ✅ Grid scales correctly with zoom level
- ✅ Grid lines remain at 1/3 and 2/3 positions
- ✅ Grid divisions maintain proper proportions
- ✅ Grid remains visible at all zoom levels
- ✅ Grid line width remains consistent (3 pixels)
- ✅ No performance issues during zoom

### Scenario 12: Grid with Pan Operations
**Steps:**
1. Load images in all channels
2. Zoom in to 200% or more
3. Pan the image left
4. Pan the image right
5. Pan the image up
6. Pan the image down
7. Pan diagonally

**Expected Results:**
- ✅ Grid moves with the image
- ✅ Grid remains aligned with image content
- ✅ Grid divisions maintain correct positions
- ✅ Grid is always visible in the viewport
- ✅ No visual artifacts or flickering

### Scenario 13: Grid with Slider Adjustments
**Steps:**
1. Load images in all channels
2. Verify grid is visible
3. Adjust Red brightness slider (+50)
4. Adjust Green contrast slider (-30)
5. Adjust Blue intensity slider (75)
6. Combine multiple adjustments
7. Reset sliders to default

**Expected Results:**
- ✅ Grid remains visible during all adjustments
- ✅ Grid position does not change
- ✅ Grid is visible on bright and dark areas
- ✅ Grid transparency works well with all image adjustments
- ✅ No performance degradation

### Scenario 14: Grid Enters Crop Mode
**Steps:**
1. Load images in all channels
2. Verify grid is visible on entire preview
3. Click the "Crop" button
4. Observe the display

**Expected Results:**
- ✅ Normal grid disappears from full preview
- ✅ Crop rectangle appears
- ✅ New grid appears inside crop rectangle only
- ✅ Grid inside crop is divided into thirds
- ✅ Grid is clipped to crop boundaries
- ✅ No grid visible outside crop rectangle

### Scenario 15: Grid in Crop Mode - Moving Crop
**Steps:**
1. Load images and enter crop mode
2. Verify grid is visible within crop rectangle
3. Click inside crop rectangle and drag to new position
4. Move crop to different areas of the image:
   - Top-left corner
   - Top-right corner
   - Bottom-left corner
   - Bottom-right corner
   - Center of image

**Expected Results:**
- ✅ Grid updates in real-time during drag operation
- ✅ Grid remains within crop boundaries at all times
- ✅ Grid maintains 1/3 and 2/3 divisions within crop
- ✅ Grid follows crop rectangle smoothly
- ✅ No visual glitches or lag

### Scenario 16: Grid in Crop Mode - Resizing Crop
**Steps:**
1. Load images and enter crop mode
2. Verify grid is visible within crop rectangle
3. Drag corner handle to make crop smaller
4. Drag corner handle to make crop larger
5. Drag edge handle to change aspect ratio
6. Test all 8 handles (4 corners, 4 edges)

**Expected Results:**
- ✅ Grid updates in real-time during resize
- ✅ Grid always divides crop area into thirds
- ✅ Grid lines reposition as crop dimensions change
- ✅ Grid remains proportional at all crop sizes
- ✅ Grid updates smoothly without flickering
- ✅ Grid works correctly with all handles

### Scenario 17: Grid Exits Crop Mode
**Steps:**
1. Load images and enter crop mode
2. Verify grid is visible within crop rectangle
3. Adjust crop position and size
4. Click "Crop" button again to exit crop mode

**Expected Results:**
- ✅ Crop rectangle disappears
- ✅ Crop grid disappears
- ✅ Normal grid reappears on entire preview
- ✅ Normal grid shows correct divisions
- ✅ Transition is smooth and immediate

### Scenario 18: Grid with Crop Mode - Multiple Entries
**Steps:**
1. Load images
2. Enter crop mode - observe grid in crop
3. Exit crop mode - observe grid on preview
4. Enter crop mode again
5. Repeat 3-4 multiple times

**Expected Results:**
- ✅ Grid switches correctly between modes each time
- ✅ Grid always appears in correct location
- ✅ No memory leaks or performance degradation
- ✅ Grid rendering remains consistent
- ✅ No visual artifacts

### Scenario 19: Grid with Different Crop Sizes
**Steps:**
1. Load images and enter crop mode
2. Create very small crop rectangle (e.g., 100x100 pixels)
3. Observe grid within small crop
4. Create very large crop rectangle (nearly full image)
5. Observe grid within large crop
6. Create medium crop rectangle
7. Observe grid within medium crop

**Expected Results:**
- ✅ Grid scales correctly for small crops
- ✅ Grid remains visible and proportional in small crops
- ✅ Grid scales correctly for large crops
- ✅ Grid divisions are accurate at all sizes
- ✅ Grid lines are always at 1/3 and 2/3 positions

### Scenario 20: Grid with Different Crop Aspect Ratios
**Steps:**
1. Load images and enter crop mode
2. Create wide crop rectangle (e.g., 16:9)
3. Observe grid divisions
4. Create tall crop rectangle (e.g., 9:16)
5. Observe grid divisions
6. Create square crop rectangle (1:1)
7. Observe grid divisions

**Expected Results:**
- ✅ Grid adapts to crop aspect ratio
- ✅ Vertical lines at 1/3 and 2/3 of crop width
- ✅ Horizontal lines at 1/3 and 2/3 of crop height
- ✅ Grid creates proper rule-of-thirds composition guide
- ✅ Grid works for all aspect ratios

### Scenario 21: Grid After Reset
**Steps:**
1. Load images in all channels
2. Verify grid is visible
3. Zoom and pan the image
4. Enter crop mode
5. Click "New" button to reset

**Expected Results:**
- ✅ Grid disappears (no image loaded)
- ✅ Viewer is cleared
- ✅ No grid artifacts remain
- ✅ Application is ready for new images

### Scenario 22: Grid Visual Quality
**Steps:**
1. Load images with various characteristics:
   - Bright image
   - Dark image
   - High contrast image
   - Low contrast image
   - Colorful image
   - Grayscale image
2. Observe grid visibility in each case

**Expected Results:**
- ✅ Grid is visible on bright images
- ✅ Grid is visible on dark images
- ✅ Semi-transparent white provides good contrast
- ✅ Grid doesn't obscure important image details
- ✅ 3-pixel line width is appropriate
- ✅ Grid enhances composition without being distracting

### Scenario 23: Grid Performance Test
**Steps:**
1. Load large images (e.g., 4000x3000 pixels or larger)
2. Observe grid rendering time
3. Zoom in and out rapidly
4. Pan around the image quickly
5. Enter and exit crop mode repeatedly
6. Resize crop rectangle rapidly

**Expected Results:**
- ✅ Grid appears instantly when image loads
- ✅ No lag during zoom operations
- ✅ No lag during pan operations
- ✅ Smooth grid updates during crop adjustments
- ✅ No memory leaks or performance degradation
- ✅ Application remains responsive

## Visual Verification Checklist

### Grid Line Positions
- [ ] Horizontal line 1 at exactly 1/3 from top
- [ ] Horizontal line 2 at exactly 2/3 from top (1/3 from bottom)
- [ ] Vertical line 1 at exactly 1/3 from left
- [ ] Vertical line 2 at exactly 2/3 from left (1/3 from right)
- [ ] Lines divide area into 9 equal rectangles
- [ ] Four intersection points create rule-of-thirds focal points

### Grid Visual Properties
- [ ] Lines are white color
- [ ] Lines are semi-transparent (can see image through them)
- [ ] Lines are 3 pixels wide
- [ ] Lines are solid (not dashed or dotted)
- [ ] Lines span entire width/height of display area
- [ ] Lines are straight and precise

### Grid Behavior
- [ ] Grid appears in normal view mode
- [ ] Grid disappears in empty viewer
- [ ] Grid switches to crop-only mode when cropping
- [ ] Grid scales with zoom
- [ ] Grid moves with pan
- [ ] Grid updates smoothly during all operations

## Known Limitations
(Document any known issues or limitations discovered during testing)

## Test Environment
- **OS:** Linux
- **Python Version:** (Check with `python --version`)
- **PyQt5 Version:** (Check with `pip show PyQt5`)
- **Display Resolution:** (Note your screen resolution)
- **Test Images:** (Note characteristics of images used)

## Test Results Summary
- **Test Date:**
- **Tester:**
- **Tests Passed:** ____ / 23
- **Issues Found:**
- **Overall Status:** PASS / FAIL / PARTIAL
