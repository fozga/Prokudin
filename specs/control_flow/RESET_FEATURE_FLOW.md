# Reset Feature - Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                       User Clicks "New" Button                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    reset_to_defaults() Method                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐   ┌────────────────┐   ┌─────────────────┐
│  Clear Images   │   │  Reset Crop    │   │  Reset Display  │
│                 │   │                │   │                 │
│ • original_imgs │   │ • crop_mode    │   │ • show_combined │
│ • aligned       │   │ • crop_rect    │   │ • current_chan  │
│ • processed     │   │ • crop_ratio   │   │                 │
│ • original_rgb  │   │ • exit mode    │   │                 │
│ • aligned_rgb   │   │ • reset combo  │   │                 │
└────────┬────────┘   └────────┬───────┘   └────────┬────────┘
         │                     │                     │
         └──────────────┬──────┴─────────┬──────────┘
                        ▼                ▼
              ┌──────────────┐  ┌──────────────────┐
              │  Reset       │  │  Clear Viewer    │
              │  Controllers │  │                  │
              └──────┬───────┘  └──────┬───────────┘
                     │                 │
     ┌───────────────┼─────────────┐   │
     │               │             │   │
     ▼               ▼             ▼   ▼
┌─────────┐   ┌──────────┐   ┌────────────┐   ┌──────────────┐
│  Red    │   │  Green   │   │   Blue     │   │  Main Viewer │
│ Channel │   │ Channel  │   │  Channel   │   │              │
└────┬────┘   └────┬─────┘   └─────┬──────┘   └──────────────┘
     │             │               │
     ▼             ▼               ▼
┌─────────────────────────────────────────────┐
│     For Each Channel Controller:            │
│                                              │
│  1. reset_all_sliders()                     │
│     • brightness = 0                        │
│     • contrast = 0                          │
│     • intensity = 100                       │
│                                              │
│  2. clear_image()                           │
│     • processed_image = None                │
│     • show gray placeholder                 │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│            Update UI State                  │
│                                              │
│  • update_save_button_state()               │
│    → Save button disabled                   │
│                                              │
│  • _update_mode_from_state()                │
│    → Update mode indicator                  │
│                                              │
│  • Show status message:                     │
│    "Application reset to default state"     │
└─────────────────────────────────────────────┘
```

## State Transitions

### Before Reset (Example State)
```
Images:
  Red:   [Loaded] ────┐
  Green: [Loaded] ────┤──> RGB Combined Image
  Blue:  [Loaded] ────┘

Sliders:
  Red:   brightness: +25, contrast: -10, intensity: 85
  Green: brightness: -15, contrast: +20, intensity: 100
  Blue:  brightness: 0,   contrast: +5,  intensity: 90

Crop:
  Mode:   [Active]
  Rect:   x:100, y:50, w:800, h:600
  Ratio:  16:9

Display:
  Mode:    Combined RGB
  Viewer:  [Shows cropped RGB image]
```

### After Reset
```
Images:
  Red:   [Empty] ────┐
  Green: [Empty] ────┤──> No Image
  Blue:  [Empty] ────┘

Sliders:
  Red:   brightness: 0, contrast: 0, intensity: 100
  Green: brightness: 0, contrast: 0, intensity: 100
  Blue:  brightness: 0, contrast: 0, intensity: 100

Crop:
  Mode:   [Disabled]
  Rect:   None
  Ratio:  Free

Display:
  Mode:    Combined RGB
  Viewer:  [Empty/Gray]
```

## Button Layout

```
┌────────────────────────────────────────────────────────────┐
│  ┌──────┐  ┌──────┐  ┌──────┐                             │
│  │ New  │  │ Save │  │ Crop │                             │
│  └──────┘  └──────┘  └──────┘                             │
│  (Always)  (Disabled  (Disabled                           │
│   Active   when no    when no                             │
│            images)    images)                              │
└────────────────────────────────────────────────────────────┘
```

## Code Structure

```
src/
├── default_state.py          ← NEW: Central configuration
│   └── DefaultState class
│       ├── SLIDER_DEFAULTS
│       ├── SHOW_COMBINED
│       ├── CURRENT_CHANNEL
│       └── CROP_MODE
│
├── main_window.py
│   └── MainWindow class
│       ├── __init__()        ← MODIFIED: Uses DefaultState
│       ├── init_ui()         ← MODIFIED: Added "New" button
│       └── reset_to_defaults() ← NEW: Complete reset logic
│
└── widgets/
    ├── channel_controller.py
    │   └── ChannelController class
    │       ├── _init_ui()    ← MODIFIED: Uses DefaultState
    │       ├── reset_all_sliders() ← NEW: Reset sliders
    │       └── clear_image() ← NEW: Clear preview
    │
    └── image_viewer.py
        └── ImageViewer class
            └── clear_image() ← NEW: Clear main viewer
```
