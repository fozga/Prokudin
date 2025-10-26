# Grid Feature - Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   User Clicks Grid Button                            │
│                   (Left Sidebar)                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │ open_grid_settings()   │
                  └────────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
   ┌─────────────────────┐       ┌─────────────────────────┐
   │ Dialog exists?      │       │ Create dialog with      │
   │ Yes: Show existing  │       │ current settings:       │
   └──────────┬──────────┘       │ - Line width            │
              │                  │ - Grid type (3x3/none)  │
              │                  └────────────┬─────────────┘
              │                               │
              │                               ▼
              │                  ┌─────────────────────────┐
              │                  │ Connect signals:        │
              │                  │ - grid_type_changed     │
              │                  │ - line_width_changed    │
              │                  └────────────┬─────────────┘
              │                               │
              └───────────┬───────────────────┘
                          │
                          ▼
              ┌──────────────────────────┐
              │ Position dialog:         │
              │ - Above Grid button      │
              │ - To the right           │
              │ - Bottom-left anchored   │
              └──────────┬───────────────┘
                          │
                          ▼
              ┌──────────────────────────┐
              │ Show dialog overlay      │
              └──────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   Grid Settings Dialog Displayed                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
   ┌─────────────────────┐       ┌─────────────────────────┐
   │ User Changes        │       │ User Changes            │
   │ Grid Type               │       │ Grid Type               │
   └──────────┬──────────┘       └────────────┬─────────────┘
              │                               │
              ▼                               ▼
   ┌─────────────────────┐       ┌─────────────────────────┐
   │ Click +/- buttons   │       │ Select from list:       │
   │ Width: 1-10 pixels  │       │ - None                  │
   └──────────┬──────────┘       │ - 3x3 Grid              │
              │                  │ - Golden Ratio          │
              │                  └────────────┬─────────────┘
              │                  └────────────┬─────────────┘
              │                               │
              ▼                               ▼
   ┌─────────────────────────────┐ ┌─────────────────────────────┐
   │ line_width_changed signal   │ │ grid_type_changed signal    │
   └──────────┬──────────────────┘ └────────────┬─────────────────┘
              │                                  │
              ▼                                  ▼
   ┌─────────────────────────────┐ ┌─────────────────────────────┐
   │ on_grid_line_width_changed()│ │ on_grid_type_changed()      │
   └──────────┬──────────────────┘ └────────────┬─────────────────┘
              │                                  │
              └──────────────┬───────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Update Grid Overlay          │
              │ (shared instance)            │
              │ - viewer.grid_overlay        │
              └──────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ Refresh viewport             │
              │ viewport().update()          │
              └──────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ Grid updated on screen       │
              └──────────────────────────────┘
```

## Main Application Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Application Displays Image                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│      Normal View Mode     │   │      Crop Mode Active     │
└────────────┬──────────────┘   └────────────┬──────────────┘
             │                                │
             ▼                                ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│ ImageViewer              │   │ CropHandler              │
│ drawForeground()         │   │ draw_foreground()        │
└────────────┬─────────────┘   └────────────┬─────────────┘
             │                               │
             ▼                               ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│ Get visible scene rect   │   │ Check crop rect exists   │
│ from viewport            │   │ and is valid             │
└────────────┬─────────────┘   └────────────┬─────────────┘
             │                               │
             ▼                               ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│ Draw grid on entire      │   │ Draw grid within         │
│ visible preview area     │   │ crop rectangle only      │
└────────────┬─────────────┘   └────────────┬─────────────┘
             │                               │
             └───────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ GridOverlay.draw()           │
              └──────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ Check if enabled             │
              │ (grid_type != "none")        │
              └──────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ Check grid type              │
              └──────────┬───────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│ _draw_3x3_grid()        │  │ _draw_golden_ratio_grid()│
│                         │  │                         │
│ Calculate positions:    │  │ Calculate positions:    │
│ • h_line_1 = top + h/3  │  │ • h_line_1 = top +      │
│ • h_line_2 = top + 2h/3 │  │             h * 0.382   │
│ • v_line_1 = left + w/3 │  │ • h_line_2 = top +      │
│ • v_line_2 = left + 2w/3│  │             h * 0.618   │
│                         │  │ • v_line_1 = left +     │
│ Draw 2 horizontal lines │  │             w * 0.382   │
│ Draw 2 vertical lines   │  │ • v_line_2 = left +     │
│                         │  │             w * 0.618   │
│                         │  │                         │
│                         │  │ Draw 2 horizontal lines │
│                         │  │ Draw 2 vertical lines   │
└─────────────────────────┘  └─────────────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │    Grid Rendered on Screen   │
              └──────────────────────────────┘
```

## User Interaction Flows

### Flow 1: Opening and Using Grid Settings

```
User Action                          System Response
───────────                          ───────────────

Click Grid Button               →    Call open_grid_settings()
                                     Check if dialog exists
                                     Get current width & type
                                     Position dialog above button
                                     Show dialog overlay

Click + Button                  →    Increase line width by 1
                                     Update display label
                                     Emit line_width_changed signal
                                     Update both grid overlays
                                     Refresh viewport
                                     Show status message

Click - Button                  →    Decrease line width by 1
                                     Update display label
                                     Emit line_width_changed signal
                                     Update both grid overlays
                                     Refresh viewport
                                     Show status message

Select "None"                   →    Emit grid_type_changed("none")
                                     Disable viewer grid
                                     Disable crop handler grid
                                     Refresh viewport
                                     Show "Grid overlay disabled"

Select "3x3 Grid"               →    Emit grid_type_changed("3x3")
                                     Enable viewer grid
                                     Set grid type to 3x3
                                     Refresh viewport
                                     Show "3x3 grid overlay enabled"

Select "Golden Ratio"           →    Emit grid_type_changed("golden_ratio")
                                     Enable viewer grid
                                     Set grid type to golden ratio
                                     Refresh viewport
                                     Show "Golden ratio grid overlay enabled"

Click Outside Dialog            →    Dialog closes automatically
                                     Settings remain applied
                                     Grid continues with current settings
```

### Flow 2: Grid in Normal View Mode

```
User Action                          System Response
───────────                          ───────────────

Load Image                      →    Display image in viewer
                                     Calculate visible scene rect
                                     Draw grid over entire preview
                                     Grid divides view into 9 parts

Zoom In/Out                     →    Recalculate visible scene rect
                                     Redraw grid at new scale
                                     Grid maintains 1/3 divisions

Pan Image                       →    Update visible scene rect
                                     Redraw grid in new position
                                     Grid follows image movement

Adjust Brightness/Contrast      →    Update image display
                                     Grid remains visible
                                     Grid position unchanged

Switch Channels                 →    Update displayed image
                                     Grid remains visible
                                     Grid maintains position
```

### Flow 3: Grid in Crop Mode

```
User Action                          System Response
───────────                          ───────────────

Click Crop Button               →    Enter crop mode
                                     Show crop rectangle
                                     Hide normal grid
                                     Draw grid within crop rect

Drag Crop Rectangle             →    Update crop rectangle position
                                     Recalculate grid within new rect
                                     Redraw grid at 1/3 and 2/3 of crop

Resize Crop Rectangle           →    Update crop rectangle size
                                     Recalculate grid lines
                                     Redraw grid scaled to new size

Move Crop Handle                →    Update crop dimensions
                                     Recalculate grid for new bounds
                                     Redraw grid within updated crop

Exit Crop Mode                  →    Hide crop rectangle
                                     Remove crop grid
                                     Show normal grid on preview
                                     Grid covers visible area
```

### Flow 3: Grid Line Calculation

```
Input: Rectangle (x, y, width, height) + Grid Type
                │
                ▼
      ┌─────────┴─────────┐
      │                   │
      ▼                   ▼
3x3 Grid Type      Golden Ratio Type
      │                   │
      ▼                   ▼
Calculate thirds    Calculate golden ratio
    w3 = width/3        gr_s = 0.382
    h3 = height/3       gr_l = 0.618
      │                   │
      ▼                   ▼
Vertical lines      Vertical lines
v1 = x + w3         v1 = x + width * gr_s
v2 = x + 2*w3       v2 = x + width * gr_l
      │                   │
      ▼                   ▼
Horizontal lines    Horizontal lines
h1 = y + h3         h1 = y + height * gr_s
h2 = y + 2*h3       h2 = y + height * gr_l
      │                   │
      └─────────┬─────────┘
                │
                ▼
        Draw lines with QPainter
        For each h_line: draw(left, h, right, h)
        For each v_line: draw(v, top, v, bottom)
```

## State Transitions

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application States                        │
└─────────────────────────────────────────────────────────────────┘

State 1: No Image Loaded
    Grid: Not visible
    Crop: Disabled
    ↓ [User loads image]

State 2: Image Loaded, Normal View
    Grid: Visible on entire preview
    Crop: Available
    ↓ [User clicks Crop button]

State 3: Crop Mode Active
    Grid: Visible only within crop rectangle
    Crop: Active, adjustable
    ↓ [User adjusts crop rectangle]

State 3a: Crop Rectangle Moving/Resizing
    Grid: Updates in real-time within crop bounds
    Crop: Dimensions changing
    ↓ [User releases mouse]

State 3: Crop Mode Active (stable)
    Grid: Visible within final crop rectangle
    Crop: Active, adjustable
    ↓ [User exits crop mode]

State 2: Image Loaded, Normal View
    Grid: Visible on entire preview
    Crop: Available
    ↓ [User clicks New button]

State 1: No Image Loaded
    Grid: Not visible
    Crop: Disabled
```

## Component Interactions

```
┌──────────────────┐
│   MainWindow     │
│                  │
│  • Manages mode  │
│  • Handles UI    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│              ImageViewer (QGraphicsView)             │
│                                                      │
│  • Displays image scene                             │
│  • Handles zoom/pan                                 │
│  • Contains GridOverlay instance                    │
│  • Calls grid.draw() in drawForeground()           │
└────────┬─────────────────────────────────┬──────────┘
         │                                 │
         ▼                                 ▼
┌──────────────────┐            ┌──────────────────────┐
│  GridOverlay     │◄───────────│   CropHandler        │
│                  │            │                      │
│  • draw()        │            │  • Manages crop rect │
│  • calculate()   │            │  • Has GridOverlay   │
│  • configure()   │            │  • Draws crop grid   │
└──────────────────┘            └──────────────────────┘

Normal Mode:
    ImageViewer → GridOverlay.draw(visible_rect)

Crop Mode:
    ImageViewer → CropHandler → GridOverlay.draw(crop_rect)
```
