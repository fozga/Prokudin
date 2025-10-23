# Manual Testing Guide for Reset Feature

## Test Scenarios

### Scenario 1: Reset with Empty Application
**Steps:**
1. Launch the application
2. Click the "New" button
3. Verify status message appears

**Expected Results:**
- ✅ Application remains in empty state
- ✅ Status message: "Application reset to default state"
- ✅ All buttons remain in initial state
- ✅ No errors or crashes

### Scenario 2: Reset with Loaded Images
**Steps:**
1. Launch the application
2. Load an image in the Red channel
3. Load an image in the Green channel
4. Load an image in the Blue channel
5. Verify combined RGB image is displayed
6. Click the "New" button

**Expected Results:**
- ✅ All channel previews show gray placeholder
- ✅ Main viewer is cleared (empty)
- ✅ Save button is disabled
- ✅ All images are removed from memory
- ✅ Status message appears

### Scenario 3: Reset with Adjusted Sliders
**Steps:**
1. Launch the application
2. Load images in all channels
3. Adjust sliders:
   - Red brightness: +50
   - Green contrast: -30
   - Blue intensity: 75
4. Click the "New" button
5. Verify all sliders return to defaults

**Expected Results:**
- ✅ Red channel: brightness=0, contrast=0, intensity=100
- ✅ Green channel: brightness=0, contrast=0, intensity=100
- ✅ Blue channel: brightness=0, contrast=0, intensity=100
- ✅ All channel previews cleared
- ✅ Main viewer cleared

### Scenario 4: Reset with Active Crop
**Steps:**
1. Launch the application
2. Load images in all channels
3. Click "Crop" button to enter crop mode
4. Draw/adjust crop rectangle
5. Click the "New" button (without accepting crop)

**Expected Results:**
- ✅ Crop mode is exited
- ✅ Crop controls hidden
- ✅ "Crop" button becomes visible again
- ✅ All images cleared
- ✅ Crop rectangle cleared
- ✅ Crop ratio reset to "Free"

### Scenario 5: Reset with Applied Crop
**Steps:**
1. Launch the application
2. Load images in all channels
3. Click "Crop" button
4. Draw crop rectangle
5. Select aspect ratio (e.g., 16:9)
6. Click "Accept Crop"
7. Verify cropped image is displayed
8. Click the "New" button

**Expected Results:**
- ✅ Cropped image is removed
- ✅ Main viewer is cleared
- ✅ Saved crop rectangle is cleared
- ✅ Crop ratio combo box reset to "Free"
- ✅ All channel previews cleared

### Scenario 6: Reset and Reload Workflow
**Steps:**
1. Launch the application
2. Load images and adjust settings
3. Click the "New" button
4. Load new images in channels
5. Verify normal functionality

**Expected Results:**
- ✅ Can load new images successfully
- ✅ Sliders work correctly
- ✅ Channel switching works
- ✅ Crop functionality works
- ✅ Save button becomes enabled when images are loaded

### Scenario 7: Multiple Resets
**Steps:**
1. Launch the application
2. Load images
3. Click "New" button
4. Click "New" button again (multiple times)

**Expected Results:**
- ✅ No errors or crashes
- ✅ Application remains stable
- ✅ Status message appears each time
- ✅ No memory leaks (visual inspection)

### Scenario 8: Reset During Image Processing
**Steps:**
1. Launch the application
2. Load images in all channels
3. Rapidly adjust sliders while images are processing
4. Click "New" button during processing

**Expected Results:**
- ✅ Processing stops gracefully
- ✅ Application returns to empty state
- ✅ No errors or hangs

## Integration Tests

### Test 1: Button Interaction
**Verify:**
- [ ] "New" button is visible and clickable
- [ ] "New" button is positioned before "Save" and "Crop"
- [ ] Button has correct label ("New")
- [ ] Button is always enabled (even when no images loaded)

### Test 2: Keyboard Shortcuts
**Verify:**
- [ ] Existing keyboard shortcuts still work after reset
- [ ] No keyboard shortcut conflicts with "New" functionality
- [ ] Keys 1, 2, 3, 4 still work for channel switching
- [ ] 'C' key still works for crop mode

### Test 3: Display State
**Verify:**
- [ ] Display mode resets to Combined RGB view
- [ ] Current channel resets to Red (0)
- [ ] Switching channels works after reset

### Test 4: Memory Management
**Verify:**
- [ ] No memory leaks after multiple resets
- [ ] Large images are properly deallocated
- [ ] Application memory usage returns to baseline after reset

## Edge Cases

### Edge Case 1: Reset with Only One Channel Loaded
**Steps:**
1. Load image only in Red channel
2. Click "New" button

**Expected:**
- ✅ Red channel cleared properly
- ✅ Other channels remain empty
- ✅ No errors

### Edge Case 2: Reset with Different Window Sizes
**Steps:**
1. Resize window to various sizes
2. Load images
3. Click "New" button in each size

**Expected:**
- ✅ Reset works correctly at all window sizes
- ✅ UI remains responsive

### Edge Case 3: Rapid Button Clicking
**Steps:**
1. Click "New" button rapidly multiple times

**Expected:**
- ✅ No crashes or errors
- ✅ Application remains stable
- ✅ Last reset completes successfully

## Performance Tests

### Performance 1: Large Images
**Steps:**
1. Load very large images (e.g., 10000x10000 pixels)
2. Click "New" button

**Expected:**
- ✅ Reset completes in reasonable time (< 1 second)
- ✅ Memory is properly freed

### Performance 2: Reset Responsiveness
**Steps:**
1. Load images and adjust settings
2. Click "New" button
3. Measure time to completion

**Expected:**
- ✅ UI remains responsive during reset
- ✅ Reset completes quickly (< 500ms)
- ✅ Status message appears promptly

## Automated Test Template

```python
def test_reset_to_defaults():
    """Test that reset_to_defaults() properly resets all state."""
    window = MainWindow()
    
    # Setup: Load some test images and adjust state
    window.original_images = [test_img1, test_img2, test_img3]
    window.aligned = [test_img1, test_img2, test_img3]
    window.processed = [test_img1, test_img2, test_img3]
    window.crop_rect = QRect(10, 10, 100, 100)
    window.crop_mode = True
    
    # Adjust sliders
    for controller in window.controllers:
        controller.sliders['brightness'].setValue(50)
        controller.sliders['contrast'].setValue(-20)
        controller.sliders['intensity'].setValue(80)
    
    # Action: Reset to defaults
    window.reset_to_defaults()
    
    # Assertions: Verify all state is reset
    assert all(img is None for img in window.original_images)
    assert all(img is None for img in window.aligned)
    assert all(img is None for img in window.processed)
    assert all(img is None for img in window.original_rgb_images)
    assert all(img is None for img in window.aligned_rgb)
    assert window.crop_rect is None
    assert window.crop_mode == False
    assert window.show_combined == True
    assert window.current_channel == 0
    
    # Verify slider values
    for controller in window.controllers:
        assert controller.sliders['brightness'].value() == 0
        assert controller.sliders['contrast'].value() == 0
        assert controller.sliders['intensity'].value() == 100
    
    print("✅ All reset tests passed!")
```

## Checklist for Release

- [ ] All manual test scenarios pass
- [ ] No memory leaks detected
- [ ] Performance is acceptable
- [ ] Edge cases handled properly
- [ ] Documentation is complete
- [ ] Code follows project style guidelines
- [ ] No compilation errors or warnings
- [ ] Feature works on all supported platforms
