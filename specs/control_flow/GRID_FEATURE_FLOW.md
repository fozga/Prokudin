# Grid Feature - Visual Flow Diagram

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
              ┌──────────────────────┐
              │ GridOverlay.draw()   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ _calculate_grid_lines(rect)  │
              │                              │
              │ Calculate dimensions:        │
              │ • width = rect.width()       │
              │ • height = rect.height()     │
              │                              │
              │ Calculate positions:         │
              │ • h_line_1 = top + h/3       │
              │ • h_line_2 = top + 2h/3      │
              │ • v_line_1 = left + w/3      │
              │ • v_line_2 = left + 2w/3     │
              └──────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │ _draw_grid_lines()           │
              │                              │
              │ Configure pen:               │
              │ • color = white              │
              │ • width = 3 pixels           │
              │ • opacity = 128 (50%)        │
              │ • style = solid              │
              │                              │
              │ Draw lines:                  │
              │ • 2 horizontal lines         │
              │ • 2 vertical lines           │
              └──────────┬───────────────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │    Grid Rendered on Screen   │
              └──────────────────────────────┘
```

## User Interaction Flows

### Flow 1: Grid in Normal View Mode

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

### Flow 2: Grid in Crop Mode

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
Input: Rectangle (x, y, width, height)
                │
                ▼
Calculate thirds of width
    third_w = width / 3
                │
                ▼
Calculate thirds of height
    third_h = height / 3
                │
                ▼
Calculate vertical line positions
    v_line_1 = x + third_w
    v_line_2 = x + 2 * third_w
                │
                ▼
Calculate horizontal line positions
    h_line_1 = y + third_h
    h_line_2 = y + 2 * third_h
                │
                ▼
Return line coordinates
    horizontal: [h_line_1, h_line_2]
    vertical:   [v_line_1, v_line_2]
                │
                ▼
Draw lines with QPainter
    For each h_line: draw(left, h_line, right, h_line)
    For each v_line: draw(v_line, top, v_line, bottom)
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
